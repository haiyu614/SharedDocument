from flask import Blueprint, request, redirect, url_for, flash, send_from_directory, current_app, jsonify, render_template, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models import Document
from remote_storage import get_remote_storage
import os
import uuid
import tempfile

documents = Blueprint('documents', __name__)

def get_current_user_id_int():
    """
    Helper: make sure we consistently convert JWT identity to int for comparisons.
    Returns int or None.
    """
    uid = get_jwt_identity()
    try:
        return int(uid) if uid is not None else None
    except (TypeError, ValueError):
        return None

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'md', 'py', 'csv'}

@documents.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        flash('没有文件部分', 'danger')
        return redirect(url_for('auth.index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('未选择文件', 'danger')
        return redirect(url_for('auth.index'))
        
    if file and allowed_file(file.filename):
        original_filename = file.filename
        # Generate a unique filename to prevent collisions
        ext = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        
        current_user_id = get_current_user_id_int()
        if current_user_id is None:
            flash('无法识别当前用户，请重新登录', 'danger')
            return redirect(url_for('auth.index'))
        
        # 检查是否使用远程存储
        if current_app.config.get('USE_REMOTE_STORAGE', False):
            # 使用远程存储
            try:
                storage = get_remote_storage()
                
                # 先保存到临时文件以获取文件大小
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    file.save(tmp_file.name)
                    file_size = os.path.getsize(tmp_file.name)
                    
                    # 上传到远程服务器
                    success = storage.upload_file(tmp_file.name, unique_filename)
                    
                    # 删除临时文件
                    try:
                        os.unlink(tmp_file.name)
                    except:
                        pass
                    
                    if not success:
                        flash('文件上传到远程服务器失败，请重试', 'danger')
                        return redirect(url_for('auth.index'))
                
            except Exception as e:
                print(f"远程上传错误: {e}")
                flash(f'文件上传失败: {str(e)}', 'danger')
                return redirect(url_for('auth.index'))
        else:
            # 使用本地存储
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Force flush to disk
            try:
                os.fsync(file.fileno())
            except:
                pass

            # Double check file exists
            if not os.path.exists(file_path):
                 flash('文件写入验证失败，请重试', 'danger')
                 return redirect(url_for('auth.index'))

            # Get file size
            file_size = os.path.getsize(file_path)
        
        # Create DB record
        new_doc = Document(
            filename=unique_filename,
            original_name=original_filename,
            file_type=ext,
            size=file_size,
            user_id=current_user_id
        )
        
        db.session.add(new_doc)
        db.session.commit()
            
        flash('文件上传成功！', 'success')
        return redirect(url_for('auth.index'))
    else:
        flash('不支持的文件类型', 'danger')
        return redirect(url_for('auth.index'))

@documents.route('/download/<int:doc_id>')
@jwt_required()
def download_file(doc_id):
    current_user_id = get_current_user_id_int()
    doc = Document.query.get_or_404(doc_id)
    
    # Check permission
    is_owner = doc.user_id == current_user_id
    is_shared = False
    
    if not is_owner:
        # Check if shared
        from models import DocumentShare
        share = DocumentShare.query.filter_by(document_id=doc.id, user_id=current_user_id).first()
        if share:
            is_shared = True
            
    if not is_owner and not is_shared:
        flash('您没有权限下载此文件', 'danger')
        return redirect(url_for('auth.index'))
    
    # 检查是否使用远程存储
    if current_app.config.get('USE_REMOTE_STORAGE', False):
        try:
            storage = get_remote_storage()
            file_obj = storage.download_fileobj(doc.filename)
            
            if file_obj is None:
                flash('文件下载失败', 'danger')
                return redirect(url_for('auth.index'))
            
            return send_file(
                file_obj,
                as_attachment=True,
                download_name=doc.original_name,
                mimetype='application/octet-stream'
            )
        except Exception as e:
            print(f"远程下载错误: {e}")
            flash(f'文件下载失败: {str(e)}', 'danger')
            return redirect(url_for('auth.index'))
    else:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], doc.filename, as_attachment=True, download_name=doc.original_name)

@documents.route('/delete/<int:doc_id>', methods=['POST'])
@jwt_required()
def delete_file(doc_id):
    current_user_id = get_current_user_id_int()
    doc = Document.query.get_or_404(doc_id)
    
    if doc.user_id != current_user_id:
        flash('您没有权限删除此文件', 'danger')
        return redirect(url_for('auth.index'))
    
    # 检查是否使用远程存储
    if current_app.config.get('USE_REMOTE_STORAGE', False):
        # 删除远程文件
        try:
            storage = get_remote_storage()
            storage.delete_file(doc.filename)
            storage.delete_file(f"{doc.filename}.html")  # 删除HTML副本
        except Exception as e:
            print(f"Error deleting remote file: {e}")
    else:
        # 删除本地文件
        try:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            html_sidecar = f"{file_path}.html"
            if os.path.exists(html_sidecar):
                os.remove(html_sidecar)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    # Remove from DB
    db.session.delete(doc)
    db.session.commit()
    
    flash('文件已删除', 'success')
    return redirect(url_for('auth.index'))

@documents.route('/editor/<int:doc_id>')
@jwt_required()
def editor(doc_id):
    current_user_id = get_current_user_id_int()
    doc = Document.query.get_or_404(doc_id)
    
    # Check permission
    is_owner = doc.user_id == current_user_id
    can_edit = is_owner
    can_view = is_owner
    
    if not is_owner:
        # Check if shared
        from models import DocumentShare
        share = DocumentShare.query.filter_by(document_id=doc.id, user_id=current_user_id).first()
        if share:
            can_view = True  # 有分享记录就能查看
            if share.permission == 'edit':
                can_edit = True  # edit 权限可以编辑
                
    if not can_view:
        flash('您没有权限编辑此文件', 'danger')
        return redirect(url_for('auth.index'))
        
    # Check if file type is editable
    editable_extensions = {'txt', 'md', 'py', 'html', 'css', 'js', 'json', 'xml', 'yml', 'yaml', 'xls', 'xlsx', 'csv', 'doc', 'docx'}
    if doc.file_type not in editable_extensions:
        flash('此文件类型不支持在线编辑', 'warning')
        return redirect(url_for('auth.index'))
        
    # Check if file exists physically to prevent ghost file error
    if current_app.config.get('USE_REMOTE_STORAGE', False):
        # 检查远程文件是否存在
        try:
            storage = get_remote_storage()
            if not storage.file_exists(doc.filename):
                # Clean up ghost file
                try:
                    db.session.delete(doc)
                    db.session.commit()
                except Exception as e:
                    print(f"Error cleaning up ghost file in editor: {e}")
                    
                flash('文件不存在或已被删除', 'danger')
                return redirect(url_for('auth.index'))
        except Exception as e:
            print(f"Error checking remote file: {e}")
            flash('无法访问远程文件', 'danger')
            return redirect(url_for('auth.index'))
    else:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
        if not os.path.exists(file_path):
            # Clean up ghost file
            try:
                db.session.delete(doc)
                db.session.commit()
            except Exception as e:
                print(f"Error cleaning up ghost file in editor: {e}")
                
            flash('文件不存在或已被删除', 'danger')
            return redirect(url_for('auth.index'))

    if doc.file_type in {'xls', 'xlsx', 'csv'}:
        return render_template('spreadsheet.html', doc=doc, can_view=can_view, can_edit=can_edit)

    if doc.file_type in {'doc', 'docx'}:
        return render_template('word_editor.html', doc=doc, can_view=can_view, can_edit=can_edit)
    
    return render_template('editor.html', doc=doc, can_view=can_view, can_edit=can_edit)

@documents.route('/save_blob/<int:doc_id>', methods=['POST'])
@jwt_required()
def save_blob(doc_id):
    current_user_id = get_current_user_id_int()
    doc = Document.query.get_or_404(doc_id)
    
    # Check permission
    is_owner = doc.user_id == current_user_id
    can_edit = is_owner
    
    if not is_owner:
        from models import DocumentShare
        share = DocumentShare.query.filter_by(document_id=doc.id, user_id=current_user_id).first()
        if share and share.permission == 'edit':
            can_edit = True
            
    if not can_edit:
        # Use 403 for API consistency
        return jsonify({'error': 'Unauthorized'}), 403
        
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    
    try:
        if current_app.config.get('USE_REMOTE_STORAGE', False):
            # 使用远程存储
            storage = get_remote_storage()
            
            # 保存主文件
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                file.save(tmp_file.name)
                file_size = os.path.getsize(tmp_file.name)
                
                success = storage.upload_file(tmp_file.name, doc.filename)
                os.unlink(tmp_file.name)
                
                if not success:
                    return jsonify({'error': 'Failed to upload to remote server'}), 500
            
            # 保存HTML副本（如果有）
            html_content = request.form.get('html_content')
            if html_content is not None:
                html_filename = f"{doc.filename}.html"
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.html') as tmp_html:
                    tmp_html.write(html_content)
                    tmp_html.flush()
                    storage.upload_file(tmp_html.name, html_filename)
                    os.unlink(tmp_html.name)
            
            doc.size = file_size
        else:
            # 使用本地存储
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
            file.save(file_path)
            doc.size = os.path.getsize(file_path)
            
            html_content = request.form.get('html_content')
            if html_content is not None:
                html_sidecar = f"{file_path}.html"
                with open(html_sidecar, 'w', encoding='utf-8') as f:
                    f.write(html_content)
        
        db.session.commit()
        return jsonify({'message': 'Saved successfully'})
    except Exception as e:
        # Log the error
        print(f"Save blob error: {e}")
        return jsonify({'error': str(e)}), 500

@documents.route('/content/<int:doc_id>', methods=['GET', 'POST'])
@jwt_required()
def file_content(doc_id):
    current_user_id = get_current_user_id_int()
    doc = Document.query.get_or_404(doc_id)
    
    # Check permission
    is_owner = doc.user_id == current_user_id
    can_view = is_owner
    can_edit = is_owner
    
    if not is_owner:
        from models import DocumentShare
        share = DocumentShare.query.filter_by(document_id=doc.id, user_id=current_user_id).first()
        if share:
            can_view = True  # 有分享记录就能查看
            if share.permission == 'edit':
                can_edit = True  # edit 权限可以编辑
                
    if not can_view:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'GET':
        try:
            if current_app.config.get('USE_REMOTE_STORAGE', False):
                # 从远程读取
                storage = get_remote_storage()
                file_obj = storage.download_fileobj(doc.filename)
                
                if file_obj is None:
                    return jsonify({'error': 'File not found'}), 404
                
                try:
                    content = file_obj.read().decode('utf-8')
                    return jsonify({'content': content})
                except UnicodeDecodeError:
                    return jsonify({'error': 'Cannot read binary file'}), 400
            else:
                # 从本地读取
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return jsonify({'content': content})
        except UnicodeDecodeError:
            return jsonify({'error': 'Cannot read binary file'}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    elif request.method == 'POST':
        if not can_edit:
            return jsonify({'error': 'Unauthorized to edit'}), 403
            
        try:
            data = request.get_json()
            content = data.get('content')
            
            if content is None:
                return jsonify({'error': 'No content provided'}), 400
            
            if current_app.config.get('USE_REMOTE_STORAGE', False):
                # 保存到远程
                storage = get_remote_storage()
                
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as tmp_file:
                    tmp_file.write(content)
                    tmp_file.flush()
                    file_size = os.path.getsize(tmp_file.name)
                    
                    success = storage.upload_file(tmp_file.name, doc.filename)
                    os.unlink(tmp_file.name)
                    
                    if not success:
                        return jsonify({'error': 'Failed to save to remote server'}), 500
                    
                    doc.size = file_size
            else:
                # 保存到本地
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                doc.size = os.path.getsize(file_path)
            
            db.session.commit()
            return jsonify({'message': 'Saved successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@documents.route('/word_content/<int:doc_id>', methods=['GET'])
@jwt_required()
def word_html_content(doc_id):
    current_user_id = get_current_user_id_int()
    doc = Document.query.get_or_404(doc_id)
    
    # Check permission (view)
    is_owner = doc.user_id == current_user_id
    can_view = is_owner
    
    if not is_owner:
        from models import DocumentShare
        share = DocumentShare.query.filter_by(document_id=doc.id, user_id=current_user_id).first()
        if share:
            can_view = True
            
    if not can_view:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        if current_app.config.get('USE_REMOTE_STORAGE', False):
            # 从远程读取HTML副本
            storage = get_remote_storage()
            html_filename = f"{doc.filename}.html"
            
            if storage.file_exists(html_filename):
                file_obj = storage.download_fileobj(html_filename)
                if file_obj:
                    html_content = file_obj.read().decode('utf-8')
                    return jsonify({'html': html_content})
        else:
            # 从本地读取HTML副本
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
            html_sidecar = f"{file_path}.html"
            
            if os.path.exists(html_sidecar):
                with open(html_sidecar, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                return jsonify({'html': html_content})
    except Exception as e:
        print(f"Error reading html sidecar: {e}")
        return jsonify({'error': str(e)}), 500
    
    # If no sidecar, return empty html struct or null to trigger fallback
    return jsonify({'html': None})

@documents.route('/share/<int:doc_id>', methods=['POST'])
@jwt_required()
def share_document(doc_id):
    current_user_id = get_current_user_id_int()
    doc = Document.query.get_or_404(doc_id)
    
    if doc.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    username = data.get('username')
    permission = data.get('permission', 'view')
    
    from models import User, DocumentShare
    
    user_to_share = User.query.filter_by(username=username).first()
    if not user_to_share:
        return jsonify({'error': 'User not found'}), 404
        
    if user_to_share.id == current_user_id:
        return jsonify({'error': 'Cannot share with yourself'}), 400
        
    # Check if already shared
    share = DocumentShare.query.filter_by(document_id=doc.id, user_id=user_to_share.id).first()
    if share:
        share.permission = permission
    else:
        share = DocumentShare(document_id=doc.id, user_id=user_to_share.id, permission=permission)
        db.session.add(share)
        
    db.session.commit()
    return jsonify({'message': 'Document shared successfully'})
