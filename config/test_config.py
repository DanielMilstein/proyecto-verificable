import os

basedir = os.path.abspath(os.path.dirname(__file__))

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sii-test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
