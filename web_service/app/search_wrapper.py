from flask import current_app

from app import Question, db, Answer, Predictor


def publish_question(query, user_id, chat_id, msg_id):
    question = Question.query.filter_by(text=query).filter_by(user_fk=user_id).first()

    if not question:
        question = Question(text=query, chat_id=chat_id, user_fk=user_id, msg_id=msg_id)
        db.session.add(question)
        db.session.commit()

    return question.id


def search_bert(content, query, question_id) -> Answer:
    pass


def search_ingest(query, question_id) -> Answer:
    knowledge_pdf_content = current_app.ingest_connector.search(query)

    answer = Answer(
        text=knowledge_pdf_content.content,
        question_fk=question_id,
        predictor_fk=Predictor.query.filter_by(name="ingest").first().id
    )
    db.session.add(answer)
    db.session.commit()

    return answer.serialize


def search_elastic(query, question_id) -> Answer:
    pass
