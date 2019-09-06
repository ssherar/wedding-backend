import os

basedir = os.path.abspath(os.path.dirname(__file__))

def _gather_docker_secret(key: str) -> str:
    path = os.path.join(os.path.sep, "run", "secrets", key)
    try:
        with open(path, "rt") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise Exception(f"Secret for path '{path}' does not exist")

class Config(object):
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    EMAIL_EXP = 3600 * 3  # 3 days


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "wedding_dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEND_EMAIL = False


class ProductionConfig(Config):
    SEND_EMAIL = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "wedding_dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = "https://sherar.wedding"


class LocalConfig(Config):
    SEND_EMAIL = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "wedding_dev.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = "http://localhost:4200"


class DockerConfig(Config):
    SECRET_KEY = _gather_docker_secret("WEDDING_SECRET_KEY")
    SEND_EMAIL = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:postgres@db:5432/wedding"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_URL = "http://localhost:4200"




config_by_name = dict(dev=DevelopmentConfig, prod=ProductionConfig, local=LocalConfig, docker=DockerConfig)
key = Config.SECRET_KEY
