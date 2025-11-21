from flask import Blueprint, request, redirect, url_for, flash, send_from_directory, current_app, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from extensions import db
from models import Document
import os
import uuid

documents = Blueprint('documents', __name__)

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
        current_user_id = get_jwt_identity()
        new_doc = Document(
            filename=unique_filename,
            original_name=original_filename,
            file_type=ext,
            size=file_size,
            user_id=current_user_id
        )
        
        db.session.add(new_doc)
        db.session.commit()
        
        try:
            # Try to force sync directory entry
            if hasattr(os, 'sync'):
                os.sync()
        except:
            pass
            
        flash('文件上传成功！', 'success')
        return redirect(url_for('auth.index'))
    else:
        flash('不支持的文件类型', 'danger')
        return redirect(url_for('auth.index'))

@documents.route('/download/<int:doc_id>')
@jwt_required()
def download_file(doc_id):
    current_user_id = get_jwt_identity()
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
        
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], doc.filename, as_attachment=True, download_name=doc.original_name)

@documents.route('/delete/<int:doc_id>', methods=['POST'])
@jwt_required()
def delete_file(doc_id):
    current_user_id = get_jwt_identity()
    doc = Document.query.get_or_404(doc_id)
    
    if doc.user_id != current_user_id:
        flash('您没有权限删除此文件', 'danger')
        return redirect(url_for('auth.index'))
        
    # Remove from disk
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        html_sidecar = f"{file_path}.html"
        if os.path.exists(html_sidecar):
            os.remove(html_sidecar)
    except Exception as e:
        print(f"Error deleting file: {e}")
        
    # Remove from DB AFTER disk cleanup to prevent race conditions or zombie files
    # Actually better to remove from DB first? No, if DB delete fails, we keep file.
    # If disk delete fails, we might keep DB entry? 
    # Current logic: Try delete disk, then delete DB.
    
    db.session.delete(doc)
    db.session.commit()
    
    flash('文件已删除', 'success')
    return redirect(url_for('auth.index'))

@documents.route('/editor/<int:doc_id>')
@jwt_required()
def editor(doc_id):
    current_user_id = get_jwt_identity()
    doc = Document.query.get_or_404(doc_id)
    
    # Check permission
    is_owner = doc.user_id == current_user_id
    can_edit = is_owner
    
    if not is_owner:
        # Check if shared
        from models import DocumentShare
        share = DocumentShare.query.filter_by(document_id=doc.id, user_id=current_user_id).first()
        if share:
            if share.permission == 'edit':
                can_edit = True
            else:
                # View only? Ideally editor should support read-only mode, but for now block or allow
                # If we want to support view-only, we need to pass that flag to template
                pass
                
    if not can_edit:
        flash('您没有权限编辑此文件', 'danger')
        return redirect(url_for('auth.index'))
        
    # Check if file type is editable
    editable_extensions = {'txt', 'md', 'py', 'html', 'css', 'js', 'json', 'xml', 'yml', 'yaml', 'xls', 'xlsx', 'csv', 'doc', 'docx'}
    if doc.file_type not in editable_extensions:
        flash('此文件类型不支持在线编辑', 'warning')
        return redirect(url_for('auth.index'))
        
    # Check if file exists physically to prevent ghost file error
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
        return render_template('spreadsheet.html', doc=doc)

    if doc.file_type in {'doc', 'docx'}:
        return render_template('word_editor.html', doc=doc)

    return render_template('editor.html', doc=doc)

@documents.route('/save_blob/<int:doc_id>', methods=['POST'])
@jwt_required()
def save_blob(doc_id):
    current_user_id = get_jwt_identity()
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
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
    
    try:
        file.save(file_path)
        # Update file size in DB
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
    current_user_id = get_jwt_identity()
    doc = Document.query.get_or_404(doc_id)
    
    # Check permission
    is_owner = doc.user_id == current_user_id
    can_view = is_owner
    can_edit = is_owner
    
    if not is_owner:
        from models import DocumentShare
        share = DocumentShare.query.filter_by(document_id=doc.id, user_id=current_user_id).first()
        if share:
            can_view = True
            if share.permission == 'edit':
                can_edit = True
                
    if not can_view:
        return jsonify({'error': 'Unauthorized'}), 403
        
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
    
    if request.method == 'GET':
        try:
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
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Update file size in DB
            doc.size = os.path.getsize(file_path)
            db.session.commit()
            
            return jsonify({'message': 'Saved successfully'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@documents.route('/word_content/<int:doc_id>', methods=['GET'])
@jwt_required()
def word_html_content(doc_id):
    current_user_id = get_jwt_identity()
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
        
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
    html_sidecar = f"{file_path}.html"
    
    if os.path.exists(html_sidecar):
        try:
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
    current_user_id = get_jwt_identity()
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
