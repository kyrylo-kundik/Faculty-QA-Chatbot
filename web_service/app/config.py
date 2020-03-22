import os


class Config:
    FLASK_APP = "app"

    PORT = os.getenv("APP_PORT")
    HOST = os.getenv("APP_HOST")

    DEBUG = False
    TESTING = False

    CSRF_ENABLED = True

    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = f'postgres+psycopg2://' \
                              f'{os.getenv("PG_USER")}:{os.getenv("PG_PASS")}@' \
                              f'{os.getenv("PG_HOST")}:{os.getenv("PG_PORT")}/{os.getenv("PG_DB")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ELASTICSEARCH_URL = f'http://{os.getenv("ES_USER")}:{os.getenv("ES_PASS")}@' \
                        f'{os.getenv("ES_HOST")}:{os.getenv("ES_PORT")}'


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
