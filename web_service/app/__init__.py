import logging

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
from flask import Flask
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

db = SQLAlchemy()

app = Flask(__name__, instance_relative_config=False)

gunicorn_error_handlers = logging.getLogger('gunicorn').handlers
app.logger.handlers.extend(gunicorn_error_handlers)

app.config.from_object('app.config.DevelopmentConfig')
CORS(app)

from app.models import *

migrate = Migrate(app, db)

from app.elastic.ingest_connector import IngestConnector
from app.pdf_extractor import PDFExtractor
from app.search_wrapper import search_ingest, api_search_elastic, search_elastic
from app.qa_extractor import QAExtractor


@app.cli.command("check_app", help="Check app for all needed data to start.")
@with_appcontext
def check_app():
    app.logger.info("called checking app before start")

    db.init_app(app)
    # TODO check app for possibilities for a proper start

    # checking out ml model
    # QA()

    # TODO refactoring: find a better way to check this
    if KnowledgeQuestion.query.count() == 0 or KnowledgeAnswer.query.count() == 0:
        from app.utils import force_reseed
        force_reseed(app)

    app.logger.info("app checked successfully. it's able to start now.")

    return app


@app.cli.command("force_reseed_db", help="Will download, index all needed data to run the app.")
@with_appcontext
def force_reseed_db():
    from app.utils import force_reseed
    force_reseed(app)

    return app


def create_app():
    app.logger.info("Setting up app...")
    # Initialize Plugins
    db.init_app(app)

    with app.app_context():
        # Import parts of our application

        app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        # app.ingest_connector = IngestConnector()

        # app.bert_context = requests.get(os.getenv("QA_TXT_URL")).text

        # app.bert_model = QA()

        app.api_predictors_table = {
            # "bert_qa": lambda query: app.bert_model.search(
            #     query=query,
            # ),
            # "ingest": lambda query: app.ingest_connector.api_search(
            #     query=query,
            # ),
            "qa": lambda query: api_search_elastic(
                query=query,
            ),
        }

        app.predictors_table = {
            # "bert_qa": lambda query: app.bert_model.search(
            #     query=query,
            # ),
            # "ingest": lambda query, question_id: search_ingest(
            #     query=query,
            #     question_id=question_id
            # ),
            "qa_question": lambda query, question_id: search_elastic(
                query=query,
                question_id=question_id
            ),
            # "qa_answer": lambda query, question_id: search_elastic(
            #     query=query,
            #     question_id=question_id,
            #     mode="answer"
            # ),
        }

        from app.routes import main, predictor, answer, user, expert_question

        # Register Blueprints
        app.register_blueprint(main.main_bp)
        app.register_blueprint(user.user_bp, url_prefix="/user")
        app.register_blueprint(predictor.predictor_bp, url_prefix="/predictor")
        app.register_blueprint(answer.answer_bp, url_prefix="/answer")
        app.register_blueprint(expert_question.expert_question_bp, url_prefix="/question")

        app.logger.info("App created.")

        return app
