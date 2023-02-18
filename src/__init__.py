from flask.json import jsonify
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.controllers.auth import auth
from src.controllers.tag import tag
from src.controllers.detect import detect
from flask import Flask, config, redirect
from firebase_admin import credentials, initialize_app
import os
from flask_jwt_extended import JWTManager


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    cred = credentials.Certificate("firebase_admin_sdk.json")
    default_app = initialize_app(cred, {
        'storageBucket': 'fu-pet-ai.appspot.com'
    })
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),


            SWAGGER={
                "title": "Bookmarks API",
                "uiversion": 3
            }
        )
    else:
        app.config.from_mapping(test_config)

    JWTManager(app)
    app.register_blueprint(auth)
    app.register_blueprint(tag)
    app.register_blueprint(detect)

    @app.get("/hello")
    def redirect_to_url():
        return "ok", 200

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({"error": "Not found"}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({"error": "Something went wrong, we are working on it"}), HTTP_500_INTERNAL_SERVER_ERROR

    return app
