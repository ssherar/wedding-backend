import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    EMAIL_EXP = 3600 * 3  # 3 days
    SWAGGER_UI = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "wedding_dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEND_EMAIL = False
    BASE_URL = "http://localhost:4200"


class ProductionConfig(Config):
    SEND_EMAIL = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "wedding_dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = "https://sherar.wedding"
    SWAGGER_UI = False


class LocalConfig(Config):
    SEND_EMAIL = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "wedding_dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = "http://localhost:4200"


config_by_name = dict(dev=DevelopmentConfig, prod=ProductionConfig, local=LocalConfig)
key = Config.SECRET_KEY
