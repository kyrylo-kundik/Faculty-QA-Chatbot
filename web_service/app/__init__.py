from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from flask import Flask
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.elastic.ingest_connector import IngestConnector
from app.pdf_extractor import PDFExtractor
from app.qas.bert import QA

db = SQLAlchemy()

app = Flask(__name__, instance_relative_config=False)
app.config.from_object('app.config.DevelopmentConfig')
CORS(app)

from app.models import *

migrate = Migrate(app, db)


@app.cli.command("check_app", help="Check app for all needed data to start.")
@with_appcontext
def check_app():
    db.init_app(app)

    # checking out ml model
    QA()
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
        db.session.query(KnowledgeAnswer).delete()
        db.session.query(KnowledgeQuestion).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
    app.ingest_connector = IngestConnector()

    app.elasticsearch.indices.delete(index=app.ingest_connector.index_name, ignore=[400, 404])
    try:
        app.ingest_connector.delete_pipeline()
    except NotFoundError:
        pass
    finally:
        app.ingest_connector.create_pipeline()

    for content in pdf_content.parsed_content:
        c = KnowledgePdfContent(
            content_page=content.page_num,
            content_paragraph=content.paragraph_num,
            content=content.content
        )
        try:
            db.session.add(c)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        app.ingest_connector.add_to_index(
            c.id, c.content, c.content_page, c.content_paragraph
        )

    return app


def create_app():
    # Initialize Plugins
    db.init_app(app)

    with app.app_context():
        # Import parts of our application
        # pdf_content = []
        # for content in KnowledgePdfContent.query.all():
        #     pdf_content.append(str(content.content))
        # app.pdf_content = "\n\n".join(pdf_content)

        app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        app.ingest_connector = IngestConnector()

        app.bert_model = QA()

        app.predictors_table = {
            "bert_qa": lambda query: app.bert_model.search(
                query=query,
            ),
            "ingest": lambda query: app.ingest_connector.search(
                query=query
            ),
        }

        from app.routes import main_bp

        # Register Blueprints
        app.register_blueprint(main_bp.main_bp)
        # app.register_blueprint(auth.auth_bp)

        return app
