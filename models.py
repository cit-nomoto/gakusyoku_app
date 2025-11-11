from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# SQLAlchemyのインスタンスを作成
db = SQLAlchemy()

# Userテーブルの定義
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # リレーション
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')


# Categoryテーブルの定義
class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # リレーション
    menus = db.relationship('Menu', backref='category', lazy=True)


# Menuテーブルの定義
class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False)  # 円単位
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String(300))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    reviews = db.relationship('Review', backref='menu', lazy=True, cascade='all, delete-orphan')


# Reviewテーブルの定義
class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5の評価
    comment = db.Column(db.Text)
    taste_rating = db.Column(db.Integer)  # 味の評価 1-5
    volume_rating = db.Column(db.Integer)  # 量の評価 1-5
    price_rating = db.Column(db.Integer)  # コスパの評価 1-5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 制約: 1ユーザーは1メニューに1レビューまで
    __table_args__ = (
        db.UniqueConstraint('user_id', 'menu_id', name='unique_user_menu_review'),
    )