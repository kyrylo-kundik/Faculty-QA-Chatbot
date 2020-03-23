from elasticsearch import Elasticsearch
from flask import Flask
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.pdf_extractor import PDFExtractor

db = SQLAlchemy()

app = Flask(__name__, instance_relative_config=False)
app.config.from_object('app.config.DevelopmentConfig')
CORS(app)

from app.models import *

migrate = Migrate(app, db)


@app.cli.command("check_db", help="Check db for all needed data to start the application.")
@with_appcontext
def check_db():
    db.init_app(app)

    # TODO check knowledge database

    return app


@app.cli.command("force_reseed_db", help="Will download, index all needed data to run the app.")
@with_appcontext
def force_reseed_db():
    db.init_app(app)

    # TODO force reseed database
    pdf_content = PDFExtractor()

    try:
        db.session.query(KnowledgePdfContent).delete()
        db.session.commit()
    except:
        db.session.rollback()

    for content in pdf_content.parsed_content:
        c = KnowledgePdfContent(
            content_page=content.page_num,
            content_paragraph=content.paragraph_num,
            content=content.content
        )
        db.session.add(c)
        db.session.commit()

    return app


def create_app():
    # Initialize Plugins
    db.init_app(app)

    with app.app_context():
        # Import parts of our application

        app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])

        # from app.routes import auth, tickets

        # Register Blueprints
        # app.register_blueprint(tickets.tickets_bp)
        # app.register_blueprint(auth.auth_bp)

        return app
