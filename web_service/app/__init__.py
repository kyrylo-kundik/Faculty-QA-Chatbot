from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
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

from app.elastic.ingest_connector import IngestConnector
from app.pdf_extractor import PDFExtractor
from app.search_wrapper import search_ingest
from app.qas.bert import QA


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

    predictor = Predictor(name="ingest", description="Search based on ingest plugin for elasticsearch")
    db.session.add(predictor)
    db.session.commit()

    return app


def create_app():
    # Initialize Plugins
    db.init_app(app)

    with app.app_context():
        # Import parts of our application

        app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        app.ingest_connector = IngestConnector()

        # app.bert_model = QA()

        app.predictors_table = {
            # "bert_qa": lambda query: app.bert_model.search(
            #     query=query,
            # ),
            "ingest": lambda query, question_id: search_ingest(
                query=query,
                question_id=question_id
            ),
        }

        from app.routes import main, predictor, answer, user

        # Register Blueprints
        app.register_blueprint(main.main_bp)
        app.register_blueprint(user.user_bp, url_prefix="/user")
        app.register_blueprint(predictor.predictor_bp, url_prefix="/predictor")
        app.register_blueprint(answer.answer_bp, url_prefix="/answer")

        return app
