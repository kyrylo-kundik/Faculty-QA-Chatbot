import click
from elasticsearch import Elasticsearch
from flask import Flask
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__, instance_relative_config=False)
app.config.from_object('app.config.DevelopmentConfig')
CORS(app)

from app.models import *

migrate = Migrate(app, db)


def create_app():
    # Initialize Plugins
    db.init_app(app)

    with app.app_context():
        # Import parts of our application

        app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
            if app.config['ELASTICSEARCH_URL'] else None

        # from app.routes import auth, tickets

        # Register Blueprints
        # app.register_blueprint(tickets.tickets_bp)
        # app.register_blueprint(auth.auth_bp)

        return app


@click.command("check_db")
@with_appcontext
def seed_db():
    db.init_app(app)

    # TODO check knowledge base

    return app
