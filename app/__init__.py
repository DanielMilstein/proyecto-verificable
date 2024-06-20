import logging

from flask import Flask, request as req
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.controllers.pages import blueprint as pages_blueprint
from config.config import Config
from app.models import db
from app.seeder import seed_database

migrate = Migrate()


def create_app(config_name=None, config_object=None):
    app = Flask(__name__, template_folder='src/views')
    app.config.from_object(Config)

    if config_object:
        app.config.from_object(config_object)
    else:
        ...

    app.register_blueprint(pages_blueprint)
    app.secret_key = b'_53oi3uri34fve34fq9pifpff;apl'

    
    db.init_app(app)
    migrate.init_app(app, db)



    with app.app_context():
        db.create_all()
        seed_database()

    @app.after_request
    def log_response(resp):
        app.logger.info("{} {} {}\n{}".format(
            req.method, req.url, req.data, resp)
        )
        return resp

    return app