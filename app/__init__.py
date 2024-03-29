import logging

from flask import Flask, request as req
from flask_sqlalchemy import SQLAlchemy
from app.controllers.pages import blueprint as pages_blueprint
from config.config import Config
from app.models import db


def create_app(config_filename):
    app = Flask(__name__, template_folder='src/views')
    app.config.from_object(Config)

    #app.static_folder = 'src/css'

    app.register_blueprint(pages_blueprint)
    app.secret_key = b'_53oi3uri34fve34fq9pifpff;apl'
    # app.logger.setLevel(logging.NOTSET)
    
    db.init_app(app)


    with app.app_context():
        db.create_all()

    @app.after_request
    def log_response(resp):
        app.logger.info("{} {} {}\n{}".format(
            req.method, req.url, req.data, resp)
        )
        return resp

    return app