
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    @property
    def is_authenticated(self):
        return True

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        from extensions import bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        from extensions import bcrypt
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # Secure filename on disk
    original_name = db.Column(db.String(255), nullable=False) # Original display name
    file_type = db.Column(db.String(50))
    size = db.Column(db.Integer)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('documents', lazy=True))
    
    # Add relationship to shares
    shares = db.relationship('DocumentShare', backref='document', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Document {self.original_name}>'

class DocumentShare(db.Model):
    __tablename__ = 'document_shares'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission = db.Column(db.String(20), default='view') # 'view', 'edit'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('shared_documents', lazy='dynamic'))
    
    __table_args__ = (
        db.UniqueConstraint('document_id', 'user_id', name='unique_share'),
    )
