import os

DEBUG = True
SECRET_KEY = 'my precious'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://myuser:verificables@localhost/project_app_db'
HOST = 'localhost'
PORT = int(os.environ.get('PORT', 5000))