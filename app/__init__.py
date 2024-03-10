import logging

from flask import Flask, request as req
from flask_sqlalchemy import SQLAlchemy
from app.controllers import pages


def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)

    app.register_blueprint(pages.blueprint)
    app.secret_key = b'_53oi3uri34fve34fq9pifpff;apl'
    app.logger.setLevel(logging.NOTSET)

    @app.after_request
    def log_response(resp):
        app.logger.info("{} {} {}\n{}".format(
            req.method, req.url, req.data, resp)
        )
        return resp

    return app