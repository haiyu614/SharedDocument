
from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, 
    get_jwt_identity, get_jwt, set_access_cookies, 
    set_refresh_cookies, unset_jwt_cookies
)
from werkzeug.urls import url_parse
from extensions import db
from models import User
from forms import LoginForm, RegistrationForm
auth = Blueprint('auth', __name__)

# JWT令牌黑名单存储
blacklisted_tokens = set()

# 在JWT令牌创建时添加jti（JWT ID）到令牌中
# @auth.after_request
# def after_request(response):
#     # 在响应中设置CORS头
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
#     response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
#     # 防止浏览器缓存受保护页面，确保上传/删除后数据立即刷新
#     response.headers['Cache-Control'] = 'no-store, max-age=0, must-revalidate'
#     response.headers['Pragma'] = 'no-cache'
#     response.headers['Expires'] = '0'
#     return response

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if request.is_json:
        data = request.get_json()
        form = LoginForm(data=data)
        
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            
            if user and user.check_password(form.password.data):
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)
                
                return jsonify({
                    "message": "登录成功",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "id": user.id,
                        "username": user.username
                    }
                }), 200
            
            return jsonify({
                "message": "用户名或密码错误",
                "status": "error"
            }), 401
            
        return jsonify({
            "message": "登录失败",
            "errors": form.errors
        }), 400
    

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            response = make_response(redirect(url_for('auth.index')))
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            
            return response
            
        flash('用户名或密码错误', 'danger')
        return redirect(url_for('auth.login'))
    
    return render_template('login.html', title='登录', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    # 处理API请求
    if request.is_json:
        data = request.get_json()
        form = RegistrationForm(data=data)
        
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                "message": "注册成功！现在您可以登录了。",
                "status": "success"
            }), 201
            
        return jsonify({
            "message": "注册失败",
            "errors": form.errors
        }), 400
    
    # 处理网页表单
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！现在您可以登录了。', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='注册', form=form)


@auth.route('/logout')
def logout():
    response = make_response(redirect(url_for('auth.login')))
    unset_jwt_cookies(response)
    flash('您已成功登出。', 'info')
    return response

# 令牌刷新端点
@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    # Ensure identity is a string for create_access_token if needed, although int works usually.
    # But consistency is good.
    new_token = create_access_token(identity=current_user_id)
    response = jsonify({'access_token': new_token})
    set_access_cookies(response, new_token)
    return response

@auth.after_request
def after_request(response):
    # 在响应中设置CORS头
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    # 防止浏览器缓存受保护页面，确保上传/删除后数据立即刷新
    response.headers['Cache-Control'] = 'no-store, max-age=0, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.timestamp(datetime.now(timezone.utc))
        target_timestamp = datetime.timestamp(datetime.now(timezone.utc) + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
    except (RuntimeError, KeyError):
        # Case where there is no valid JWT. Just return the original response
        return response
    return response
@auth.route('/logout2', methods=['DELETE'])
@jwt_required()
def logout2():
    jti = get_jwt()['jti']
    blacklisted_tokens.add(jti)
    return jsonify({"msg": "成功注销"})

# 临时添加一个首页路由
@auth.route('/')
@auth.route('/index')
@jwt_required()
def index():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # Fetch user documents
    from models import Document, DocumentShare
    import os
    from flask import current_app
    
    # Own documents - simple DB fetch, trust the DB
    my_documents = Document.query.filter_by(user_id=current_user_id).order_by(Document.upload_date.desc()).all()
    
    # Shared with me
    shared_shares = DocumentShare.query.filter_by(user_id=current_user_id).all()
    shared_documents = []
    for share in shared_shares:
        if share.document:
            shared_documents.append(share.document)
        else:
            # Clean up orphan share if document is gone (this is safe as it's DB integrity)
            db.session.delete(share)
            
    if len(shared_documents) < len(shared_shares):
         db.session.commit()

    return render_template('index.html', title='共享文档系统', user=user, my_documents=my_documents, shared_documents=shared_documents)
