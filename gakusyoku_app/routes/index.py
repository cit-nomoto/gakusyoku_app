from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from datetime import datetime
from models import db, User, Menu, Review, Category

index_bp = Blueprint('index', __name__)

# （/）エンドポイントでの処理を定義 - メニュー一覧
@index_bp.route('/')
def index():
    # ログインチェック
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    
    # カテゴリとメニューを取得
    categories = Category.query.all()
    menus = Menu.query.filter_by(is_available=True).all()
    
    # メニューごとの平均評価とレビュー数を計算
    menu_stats = {}
    for menu in menus:
        reviews = Review.query.filter_by(menu_id=menu.id).all()
        if reviews:
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            menu_stats[menu.id] = {
                'avg_rating': round(avg_rating, 1),
                'review_count': len(reviews)
            }
        else:
            menu_stats[menu.id] = {
                'avg_rating': 0,
                'review_count': 0
            }
    
    return render_template('index.html', user=user, menus=menus, categories=categories, menu_stats=menu_stats)


# メニュー詳細とレビュー一覧
@index_bp.route('/menus/<int:id>')
def menu_detail(id):
    # ログインチェック
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    menu = Menu.query.get_or_404(id)
    
    # レビューを取得（新しい順）
    reviews = Review.query.filter_by(menu_id=id).order_by(Review.created_at.desc()).all()
    
    # 平均評価を計算
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        avg_taste = sum(r.taste_rating for r in reviews if r.taste_rating) / len([r for r in reviews if r.taste_rating]) if any(r.taste_rating for r in reviews) else 0
        avg_volume = sum(r.volume_rating for r in reviews if r.volume_rating) / len([r for r in reviews if r.volume_rating]) if any(r.volume_rating for r in reviews) else 0
        avg_price = sum(r.price_rating for r in reviews if r.price_rating) / len([r for r in reviews if r.price_rating]) if any(r.price_rating for r in reviews) else 0
    else:
        avg_rating = avg_taste = avg_volume = avg_price = 0
    
    # ユーザーが既にレビュー済みかチェック
    user_review = Review.query.filter_by(user_id=user.id, menu_id=id).first()
    
    return render_template('menu_detail.html', 
                         user=user, 
                         menu=menu, 
                         reviews=reviews,
                         avg_rating=round(avg_rating, 1),
                         avg_taste=round(avg_taste, 1),
                         avg_volume=round(avg_volume, 1),
                         avg_price=round(avg_price, 1),
                         review_count=len(reviews),
                         user_review=user_review)


# レビュー投稿
@index_bp.route('/menus/<int:id>/review', methods=['GET', 'POST'])
def post_review(id):
    # ログインチェック
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    menu = Menu.query.get_or_404(id)
    
    if request.method == 'POST':
        # 既存レビューをチェック
        existing_review = Review.query.filter_by(user_id=user.id, menu_id=id).first()
        
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment', '').strip()
        taste_rating = request.form.get('taste_rating')
        volume_rating = request.form.get('volume_rating')
        price_rating = request.form.get('price_rating')
        
        # バリデーション
        if not (1 <= rating <= 5):
            flash('評価は1〜5の範囲で入力してください')
            return redirect(url_for('index.post_review', id=id))
        
        if existing_review:
            # 既存レビューを更新
            existing_review.rating = rating
            existing_review.comment = comment if comment else None
            existing_review.taste_rating = int(taste_rating) if taste_rating else None
            existing_review.volume_rating = int(volume_rating) if volume_rating else None
            existing_review.price_rating = int(price_rating) if price_rating else None
            existing_review.updated_at = datetime.utcnow()
            flash('レビューを更新しました')
        else:
            # 新規レビューを作成
            review = Review(
                user_id=user.id,
                menu_id=id,
                rating=rating,
                comment=comment if comment else None,
                taste_rating=int(taste_rating) if taste_rating else None,
                volume_rating=int(volume_rating) if volume_rating else None,
                price_rating=int(price_rating) if price_rating else None
            )
            db.session.add(review)
            flash('レビューを投稿しました')
        
        db.session.commit()
        return redirect(url_for('index.menu_detail', id=id))
    
    # GET: レビュー投稿フォームを表示
    # 既存レビューがあれば編集モード
    existing_review = Review.query.filter_by(user_id=user.id, menu_id=id).first()
    
    return render_template('post_review.html', user=user, menu=menu, review=existing_review)