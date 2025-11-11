from flask import Blueprint, render_template, session, redirect, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI不要でmatplotlib利用
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
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


def preprocess_data(data):
    # dt: データに日時処理を適用する処理
    data['year'] = data['created_at'].dt.year
    data['month'] = data['created_at'].dt.month
    data['day'] = data['created_at'].dt.day
    data['dayofweek'] = data['created_at'].dt.dayofweek  # 0=月曜, 6=日曜
    return data


def predict_next_week_popular_menu(df):
    """
    過去のトレンドから次週の話題になりそうなメニューを予測
    
    機械学習による時系列予測:
    - 過去4週間のデータで学習
    - メニューの価格、カテゴリ、評価、トレンドを考慮
    - 次週の各メニューの人気度(レビュー数)を予測
    """
    if df.empty or 'created_at' not in df.columns:
        return None
    
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = preprocess_data(df)
    
    # 週番号を追加
    df['week'] = df['created_at'].dt.isocalendar().week
    df['year'] = df['created_at'].dt.year
    
    # 現在の週を取得
    current_date = datetime.now()
    current_week = current_date.isocalendar()[1]
    current_year = current_date.year
    
    # 過去4週間のデータのみを使用（学習用）
    past_weeks_data = df[
        ((df['year'] == current_year) & (df['week'] < current_week)) |
        ((df['year'] == current_year - 1) & (df['week'] > current_week))
    ]
    
    if past_weeks_data.empty:
        return None
    
    # 週ごと・メニューごとの集計
    weekly_stats = past_weeks_data.groupby(['week', 'year', 'menu_name', 'menu_id']).agg({
        'rating': ['mean', 'count'],
        'taste_rating': 'mean',
        'volume_rating': 'mean',
        'price_rating': 'mean',
        'price': 'first',
        'category': 'first'
    }).reset_index()
    
    weekly_stats.columns = ['week', 'year', 'menu_name', 'menu_id', 
                           'avg_rating', 'review_count', 'avg_taste', 
                           'avg_volume', 'avg_price_rating', 'price', 'category']
    
    # カテゴリをダミー変数化（One-Hot Encoding）
    category_dummies = pd.get_dummies(weekly_stats['category'], prefix='cat')
    weekly_stats = pd.concat([weekly_stats, category_dummies], axis=1)
    
    # メニューごとに予測モデルを構築
    menu_predictions = []
    
    for menu_name in weekly_stats['menu_name'].unique():
        menu_data = weekly_stats[weekly_stats['menu_name'] == menu_name].copy()
        
        # 最低3週間以上のデータがあるメニューのみ予測
        if len(menu_data) < 3:
            continue
        
        # 週番号を連続値に変換（トレンドの特徴量）
        menu_data = menu_data.sort_values(['year', 'week'])
        menu_data['week_num'] = range(len(menu_data))
        
        # カテゴリのダミー変数カラムを取得
        cat_columns = [col for col in menu_data.columns if col.startswith('cat_')]
        
        # 特徴量の構築
        feature_columns = ['week_num', 'avg_rating', 'price']
        
        # 詳細評価がある場合は追加
        if menu_data['avg_taste'].notna().any():
            feature_columns.append('avg_taste')
        if menu_data['avg_volume'].notna().any():
            feature_columns.append('avg_volume')
        if menu_data['avg_price_rating'].notna().any():
            feature_columns.append('avg_price_rating')
        
        # カテゴリ特徴量を追加
        feature_columns.extend(cat_columns)
        
        # 欠損値を0で埋める
        menu_data[feature_columns] = menu_data[feature_columns].fillna(0)
        
        X = menu_data[feature_columns].values
        # ターゲット: レビュー数（人気度の指標）
        y = menu_data['review_count'].values
        
        # 線形回帰で次週の人気度を予測
        model = LinearRegression()
        model.fit(X, y)
        
        # 次週の予測値を準備
        next_week_num = len(menu_data)
        last_row = menu_data.iloc[-1]
        
        # 次週の特徴量を構築
        next_features = [next_week_num, last_row['avg_rating'], last_row['price']]
        
        if 'avg_taste' in feature_columns:
            next_features.append(last_row['avg_taste'])
        if 'avg_volume' in feature_columns:
            next_features.append(last_row['avg_volume'])
        if 'avg_price_rating' in feature_columns:
            next_features.append(last_row['avg_price_rating'])
        
        # カテゴリダミー変数を追加
        for cat_col in cat_columns:
            next_features.append(last_row[cat_col])
        
        predicted_popularity = model.predict([next_features])[0]
        
        # 予測値が負の場合は0に
        predicted_popularity = max(0, predicted_popularity)
        
        # 総合スコア = 予測レビュー数 × 平均評価 × コスパ係数
        # コスパ係数: 価格が高いほど若干減点（800円を基準に正規化）
        price_factor = 800 / max(last_row['price'], 100)  # 100円未満は100として扱う
        total_score = predicted_popularity * last_row['avg_rating'] * (0.8 + 0.2 * price_factor)
        
        menu_predictions.append({
            'menu_name': menu_name,
            'menu_id': last_row['menu_id'],
            'predicted_popularity': round(predicted_popularity, 2),
            'avg_rating': round(last_row['avg_rating'], 2),
            'price': int(last_row['price']),
            'total_score': round(total_score, 2),
            'category': last_row['category']
        })
    
    # スコア順にソート
    menu_predictions = sorted(menu_predictions, key=lambda x: x['total_score'], reverse=True)
    
    return {
        'next_week': f"{current_year}年 第{current_week + 1}週",
        'top_predictions': menu_predictions[:10]  # TOP10
    }


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
                             charts={},
                             recommendations=None)
    
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
            'user_id': r.user_id,
            'created_at': r.created_at
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
    
    # 機械学習による次週の人気メニュー予測
    recommendations = predict_next_week_popular_menu(df)
    
    return render_template('analysis.html',
                         user=user,
                         charts=charts,
                         recommendations=recommendations)
