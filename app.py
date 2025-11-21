from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit, join_room, leave_room
from extensions import db, bcrypt, jwt, socketio
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for('auth.login'))

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return redirect(url_for('auth.login'))

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return redirect(url_for('auth.login'))

    # 注册蓝图
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from documents import documents as documents_blueprint
    app.register_blueprint(documents_blueprint, url_prefix='/documents')

    from models import User, Document, DocumentShare  # 导入所有模型

    # 创建数据库表
    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return redirect(url_for('auth.index'))

    @app.route('/init_db')
    def init_db():
        with app.app_context():
            db.create_all()
        return "Database tables updated successfully!"
        
    @socketio.on('join')
    def on_join(data):
        room = data['room']
        join_room(room)
        emit('status', {'msg': 'Someone has entered the room.'}, room=room)

    @socketio.on('leave')
    def on_leave(data):
        room = data['room']
        leave_room(room)
        emit('status', {'msg': 'Someone has left the room.'}, room=room)

    @socketio.on('update_content')
    def handle_update_content(data):
        room = data['room']
        # Broadcast the update to everyone in the room except the sender
        emit('update_content', data, room=room, include_self=False)

    @app.context_processor
    def inject_user():
        from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
        from models import User
        
        class Anonymous:
            is_authenticated = False
            username = "Guest"

        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
                if user:
                    return {'current_user': user}
        except Exception:
            pass
            
        return {'current_user': Anonymous()}

    return app

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)
