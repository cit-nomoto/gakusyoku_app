from flask import Blueprint, render_template, session, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI不要でmatplotlib利用
import matplotlib.pyplot as plt
import io
import base64
from models import User, Menu, Review

analysis_bp = Blueprint('analysis', __name__)

# 日本語フォント設定
plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False


def plot_to_base64(fig):
    """matplotlibのfigureをbase64エンコードした画像に変換"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64


@analysis_bp.route('/analysis')
def analysis_dashboard():
    """データ分析ダッシュボード"""
    # ログインチェック
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    
    # レビューデータをDataFrameに変換
    reviews = Review.query.all()
    if not reviews:
        return render_template('analysis.html', 
                             user=user,
                             charts={})
    
    review_data = []
    for r in reviews:
        review_data.append({
            'menu_id': r.menu_id,
            'menu_name': r.menu.name,
            'category': r.menu.category.name,
            'price': r.menu.price,
            'rating': r.rating,
            'taste_rating': r.taste_rating or 0,
            'volume_rating': r.volume_rating or 0,
            'price_rating': r.price_rating or 0,
            'user_id': r.user_id
        })
    
    df = pd.DataFrame(review_data)
    
    # グラフ生成
    charts = {}
    
    # 人気メニューTOP10
    fig, ax = plt.subplots(figsize=(10, 6))
    menu_counts = df['menu_name'].value_counts().head(10)
    menu_counts.plot(kind='barh', ax=ax, color='lightgreen')
    ax.set_title('レビュー数が多いメニュー TOP10')
    ax.set_xlabel('レビュー数')
    ax.set_ylabel('メニュー名')
    charts['popular_menus'] = plot_to_base64(fig)
    
    return render_template('analysis.html',
                         user=user,
                         charts=charts)

