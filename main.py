# flaskパッケージをインポート
from flask import Flask
from models import db
from routes.index import index_bp
from routes.auth import auth_bp
from routes.analysis import analysis_bp

def create_app():
    # Flaskのインスタンスを作成
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'abc1234'  # セッション管理のための秘密鍵
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # データベースの初期化
    db.init_app(app)
    
    # Blueprintの登録
    app.register_blueprint(index_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    
    return app

# 呼び出されたとき、アプリケーションを実行
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)