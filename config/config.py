import os
class Config:
    DEBUG = True
    SECRET_KEY = 'my precious'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://myuser:verificables@sii-mysql-db/project_app_db'