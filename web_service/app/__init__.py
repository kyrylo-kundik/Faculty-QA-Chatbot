import logging
import os

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
from app.search_wrapper import search_ingest, api_search_elastic, search_elastic
from app.qa_extractor import QAExtractor


@app.cli.command("check_app", help="Check app for all needed data to start.")
@with_appcontext
def check_app():
    db.init_app(app)

    # checking out ml model
    # QA()
    # TODO check knowledge database

    return app


@app.cli.command("force_reseed_db", help="Will download, index all needed data to run the app.")
@with_appcontext
def force_reseed_db():
    db.init_app(app)

    # TODO force reseed database
    pdf_content = PDFExtractor(os.getenv("PDF_URL"))

    try:
        db.session.query(KnowledgePdfContent).delete()
        db.session.query(KnowledgeQuestion).delete()
        db.session.query(KnowledgeAnswer).delete()
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

    try:
        predictor = Predictor(
            name="ingest",
            description="Search based on ingest plugin for elasticsearch"
        )

        db.session.add(predictor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.warning("Ingest predictor has already been stored in db", str(e))

    qa = QAExtractor(os.getenv("QA_TXT_URL"))

    for qa_content in qa.parse():
        try:
            answer = KnowledgeAnswer(
                text=qa_content.answer
            )

            db.session.add(answer)
            db.session.commit()

            question = KnowledgeQuestion(
                text=qa_content.question, knowledge_answer_fk=answer.id
            )

            db.session.add(question)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    try:
        predictor = Predictor(
            name="qa_question",
            description="Search based on Buddy QA Knowledge base with elasticsearch"
        )

        db.session.add(predictor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.warning("QA predictor has already been stored in database.", str(e))

    try:
        predictor = Predictor(
            name="qa_answer",
            description="Search based on Buddy QA Knowledge base with elasticsearch"
        )

        db.session.add(predictor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.warning("QA predictor has already been stored in database.", str(e))

    return app


def create_app():
    logging.info("Setting up app.")
    # Initialize Plugins
    db.init_app(app)

    with app.app_context():
        # Import parts of our application

        app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
        app.ingest_connector = IngestConnector()

        # app.bert_context = requests.get(os.getenv("QA_TXT_URL")).text

        # app.bert_model = QA()

        app.api_predictors_table = {
            # "bert_qa": lambda query: app.bert_model.search(
            #     query=query,
            # ),
            "ingest": lambda query: app.ingest_connector.api_search(
                query=query,
            ),
            "qa": lambda query: api_search_elastic(
                query=query,
            ),
        }

        app.predictors_table = {
            # "bert_qa": lambda query: app.bert_model.search(
            #     query=query,
            # ),
            "ingest": lambda query, question_id: search_ingest(
                query=query,
                question_id=question_id
            ),
            "qa_question": lambda query, question_id: search_elastic(
                query=query,
                question_id=question_id
            ),
            "qa_answer": lambda query, question_id: search_elastic(
                query=query,
                question_id=question_id,
                mode="answer"
            ),
        }

        from app.routes import main, predictor, answer, user, expert_question

        # Register Blueprints
        app.register_blueprint(main.main_bp)
        app.register_blueprint(user.user_bp, url_prefix="/user")
        app.register_blueprint(predictor.predictor_bp, url_prefix="/predictor")
        app.register_blueprint(answer.answer_bp, url_prefix="/answer")
        app.register_blueprint(expert_question.expert_question_bp, url_prefix="/question")

        logging.info("App started.")

        return app
