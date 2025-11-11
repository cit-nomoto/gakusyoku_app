from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

# ユーザー登録
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # バリデーション
        if not username or not password:
            flash('全ての項目を入力してください')
            return render_template('register.html')
        
        # 既存ユーザーのチェック
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('そのユーザー名は既に使用されています')
            return render_template('register.html')
        
        # 新しいユーザーを作成
        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('登録が完了しました。ログインしてください')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

# ログイン
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('ログインしました')
            return redirect(url_for('index.index'))
        else:
            flash('ユーザー名またはパスワードが正しくありません')
    
    return render_template('login.html')

# ログアウト
@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('ログアウトしました')
    return redirect(url_for('auth.login'))