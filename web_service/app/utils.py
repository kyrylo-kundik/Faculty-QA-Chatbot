from elasticsearch import NotFoundError, Elasticsearch
from sqlalchemy.exc import SQLAlchemyError

from app import db, Predictor, KnowledgeQuestion, KnowledgeAnswer, QAExtractor, KnowledgePdfContent


def force_reseed(app):
    app.logger.info("called force reseeding db")
    db.init_app(app)

    # app.logger.info("parsing PDFs")
    # pdf_content = PDFExtractor(app.config["PDF_URL"])

    app.logger.info("Deleting previous knowledge base from postgres")
    try:
        db.session.query(KnowledgePdfContent).delete()
        db.session.query(KnowledgeQuestion).delete()
        db.session.query(KnowledgeAnswer).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']])
    # app.ingest_connector = IngestConnector()

    app.logger.info("deleting elastic indices and pipelines")
    app.elasticsearch.indices.delete(index=KnowledgeAnswer.__tablename__, ignore=[400, 404])
    app.elasticsearch.indices.delete(index=KnowledgeQuestion.__tablename__, ignore=[400, 404])
    # app.elasticsearch.indices.delete(index=app.ingest_connector.index_name, ignore=[400, 404])
    try:
        pass
        # app.ingest_connector.delete_pipeline()
    except NotFoundError:
        pass
    finally:
        pass
        # app.ingest_connector.create_pipeline()
    qa = QAExtractor(app.config["QA_TXT_URL"])

    app.logger.info("parsing QA doc")
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
        except SQLAlchemyError as e:
            db.session.rollback()
            raise e

    app.logger.info("adding qa predictors")
    try:
        predictor = Predictor(
            name="qa_question",
            description="Search based on Buddy QA Knowledge base with elasticsearch"
        )

        db.session.add(predictor)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.warning(f"QA predictor has already been stored in database: {e.__cause__}")

    app.logger.info("force reseeding finished successfully.")
