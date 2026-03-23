"""
ダミーデータ挿入スクリプト
テスト用のユーザー、カテゴリ、メニュー、レビューを作成
"""
from main import create_app
from models import db, User, Category, Menu, Review
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # データベーステーブルを作成
    print("データベーステーブルを作成中...")
    db.create_all()
    print("テーブル作成完了")
    
    # 既存データを削除
    print("\n既存データを削除中...")
    Review.query.delete()
    Menu.query.delete()
    Category.query.delete()
    User.query.delete()
    db.session.commit()
    print("削除完了")
    
    # ユーザーを作成
    print("\nユーザーを作成中...")
    users = []
    user_names = [
        '田中太郎', '佐藤花子', '鈴木一郎', '高橋美咲', '渡辺健太',
        '伊藤さくら', '山本大輝', '中村優子', '小林翔太', '加藤愛',
        '吉田亮介', '山田莉子', '佐々木翼', '井上結衣', '木村拓也',
        '林美穂', '斎藤駿', '松本彩', '清水聡', '山口真理',
        '森田陸', '池田香織', '橋本健', '石川奈々', '前田涼',
        '岡田ひかり', '長谷川蓮', '藤田理沙', '後藤誠', '近藤舞'
    ]
    
    for name in user_names:
        user = User(
            username=name,
            password_hash=generate_password_hash('password123'),
            is_admin=(name == '田中太郎')  # 最初のユーザーを管理者に
        )
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    print(f"{len(users)}人のユーザーを作成しました")
    
    # カテゴリを作成
    print("\nカテゴリを作成中...")
    categories_data = [
        {'name': '定食', 'description': '主菜・ご飯・味噌汁のセット'},
        {'name': '丼もの', 'description': 'ご飯の上に具材を乗せたメニュー'},
        {'name': '麺類', 'description': 'ラーメン、うどん、そば'},
        {'name': 'カレー', 'description': '各種カレーライス'},
        {'name': '軽食', 'description': 'おにぎり、パン、サンドイッチ'},
        {'name': 'デザート', 'description': 'デザート・飲み物'}
    ]
    
    categories = []
    for cat_data in categories_data:
        category = Category(**cat_data)
        categories.append(category)
        db.session.add(category)
    
    db.session.commit()
    print(f"{len(categories)}個のカテゴリを作成しました")
    
    # メニューを作成
    print("\nメニューを作成中...")
    menus_data = [
        # 定食
        {'name': '唐揚げ定食', 'description': 'ジューシーな唐揚げ5個', 'price': 550, 'category_id': 1},
        {'name': '生姜焼き定食', 'description': '豚肉の生姜焼き', 'price': 600, 'category_id': 1},
        {'name': '焼き魚定食', 'description': '日替わりの焼き魚', 'price': 580, 'category_id': 1},
        {'name': 'ハンバーグ定食', 'description': 'デミグラスソースのハンバーグ', 'price': 620, 'category_id': 1},
        {'name': 'チキン南蛮定食', 'description': 'タルタルソースたっぷり', 'price': 600, 'category_id': 1},
        
        # 丼もの
        {'name': 'ピリ辛そぼろ丼', 'description': '少しスパイシーなそぼろ丼', 'price': 450, 'category_id': 2},
        {'name': 'ソースチキンカツ丼', 'description': 'ボリューム満点', 'price': 500, 'category_id': 2},
        {'name': '豚の照り焼き丼', 'description': '味濃いめの豚肉', 'price': 400, 'category_id': 2},
        {'name': '唐揚げおろし丼', 'description': '大きな唐揚げ', 'price': 550, 'category_id': 2},
        
        # 麺類
        {'name': '醤油ラーメン', 'description': 'あっさり醤油スープ', 'price': 480, 'category_id': 3},
        {'name': '味噌ラーメン', 'description': '濃厚味噌スープ', 'price': 500, 'category_id': 3},
        {'name': 'かけうどん', 'description': 'シンプルなうどん', 'price': 300, 'category_id': 3},
        {'name': '天ぷらうどん', 'description': 'エビ天入りうどん', 'price': 450, 'category_id': 3},
        {'name': 'ざるそば', 'description': '冷たいそば', 'price': 400, 'category_id': 3},
        
        # カレー
        {'name': 'カツカレー', 'description': 'とんかつのせカレー', 'price': 550, 'category_id': 4},
        {'name': 'チキンカレー', 'description': '鶏肉のカレー', 'price': 450, 'category_id': 4},
        {'name': '野菜カレー', 'description': '野菜たっぷりカレー', 'price': 400, 'category_id': 4},
        
        # 軽食
        {'name': 'おにぎりセット', 'description': 'おにぎり2個と味噌汁', 'price': 250, 'category_id': 5},
        {'name': 'サンドイッチ', 'description': 'ハムとチーズのサンド', 'price': 300, 'category_id': 5},
        {'name': '焼きそばパン', 'description': '学食の定番', 'price': 200, 'category_id': 5},
        
        # デザート
        {'name': 'プリン', 'description': '手作りプリン', 'price': 150, 'category_id': 6},
        {'name': 'アイスクリーム', 'description': 'バニラアイス', 'price': 120, 'category_id': 6},
        {'name': 'コーヒー', 'description': 'ホット/アイス', 'price': 100, 'category_id': 6},
    ]
    
    menus = []
    for menu_data in menus_data:
        menu = Menu(**menu_data)
        menus.append(menu)
        db.session.add(menu)
    
    db.session.commit()
    print(f"{len(menus)}個のメニューを作成しました")
    
    # レビューを作成
    print("\nレビューを作成中...")
    comments_positive = [
        '美味しかったです！',
        'ボリュームがあって満足！',
        'コスパ最高！',
        '味付けがちょうど良い',
        'また食べたい',
        'お気に入りメニューです',
        '量もちょうど良かった',
        '値段の割に美味しい',
        '定番で安心の味',
        '友達にもおすすめしたい',
        '期待以上でした',
        'リピート確定です',
        '毎週食べてます',
        '最高の一品',
        '文句なし！'
    ]
    
    comments_neutral = [
        '普通に美味しい',
        '可もなく不可もなく',
        'まあまあかな',
        '値段相応',
        '悪くはない',
        '普通の学食メニュー',
        '標準的な味',
        'たまに食べる分には良い'
    ]
    
    comments_negative = [
        '少し物足りない',
        '値段が高い気がする',
        '味が薄い',
        '量が少ない',
        'もう少し改善してほしい',
        '期待外れでした',
        'もう注文しないかも'
    ]
    
    reviews = []
    review_count = 0
    
    # 各メニューに15〜25件のレビューをランダムに作成
    for menu in menus:
        # 丼ものカテゴリ（category_id=2）は人気なのでレビュー数を多めに
        if menu.category_id == 2:
            num_reviews = random.randint(22, 28)  # 丼ものは多め
        else:
            num_reviews = random.randint(12, 20)  # 他は少なめ
        
        # ユーザー数を超える場合は調整
        num_reviews = min(num_reviews, len(users))
        selected_users = random.sample(users, num_reviews)
        
        for user in selected_users:
            # 価格による評価の調整
            # 安いほど高評価になる傾向（400円以下は高評価、600円以上は低評価傾向）
            if menu.price <= 400:
                # 安いメニュー: 高評価が多い
                rating = random.choices([1, 2, 3, 4, 5], weights=[3, 5, 20, 40, 32])[0]
            elif menu.price <= 500:
                # 中価格: バランス良く
                rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 30, 35, 20])[0]
            else:
                # 高いメニュー: やや低評価傾向
                rating = random.choices([1, 2, 3, 4, 5], weights=[8, 15, 35, 30, 12])[0]
            
            # 丼ものは全体的に評価を+0.5ポイント上げる（人気）
            if menu.category_id == 2:
                rating = min(5, rating + (1 if random.random() < 0.5 else 0))
            
            # 評価に応じてコメントを選択
            if rating >= 4:
                comment = random.choice(comments_positive)
            elif rating >= 3:
                comment = random.choice(comments_neutral)
            else:
                comment = random.choice(comments_negative)
            
            # 詳細評価（90%の確率で入力）
            if random.random() < 0.9:
                taste_rating = max(1, min(5, rating + random.randint(-1, 1)))
                volume_rating = max(1, min(5, rating + random.randint(-1, 1)))
                
                # コスパ評価: 安いメニューほど高く
                if menu.price <= 400:
                    price_rating = max(1, min(5, rating + random.randint(0, 1)))
                elif menu.price >= 600:
                    price_rating = max(1, min(5, rating + random.randint(-1, 0)))
                else:
                    price_rating = max(1, min(5, rating + random.randint(-1, 1)))
            else:
                taste_rating = None
                volume_rating = None
                price_rating = None
            
            # ランダムな日時（過去60日以内）
            days_ago = random.randint(0, 60)
            created_at = datetime.utcnow() - timedelta(days=days_ago, hours=random.randint(0, 23))
            
            review = Review(
                user_id=user.id,
                menu_id=menu.id,
                rating=rating,
                comment=comment,
                taste_rating=taste_rating,
                volume_rating=volume_rating,
                price_rating=price_rating,
                created_at=created_at
            )
            reviews.append(review)
            db.session.add(review)
            review_count += 1
    
    db.session.commit()
    print(f"{review_count}件のレビューを作成しました")
    
    # サマリーを表示
    print("\n" + "="*50)
    print("ダミーデータの挿入が完了しました！")
    print("="*50)
    print(f"ユーザー数: {len(users)}")
    print(f"カテゴリ数: {len(categories)}")
    print(f"メニュー数: {len(menus)}")
    print(f"レビュー数: {review_count}")
