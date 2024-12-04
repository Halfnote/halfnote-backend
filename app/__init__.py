from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from .routes import albums, singles, auth, reviews
        app.register_blueprint(albums.bp)
        app.register_blueprint(singles.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(reviews.bp)

        db.create_all()

    return app
