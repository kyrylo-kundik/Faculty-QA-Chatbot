from typing import Union

from flask import current_app

from app import Question, db, Answer, Predictor, KnowledgeQuestion, KnowledgeAnswer


def publish_question(query, user_id, chat_id, msg_id):
    question = Question.query.filter_by(text=query).filter_by(user_fk=user_id).first()

    if not question:
        question = Question(text=query, chat_id=chat_id, user_fk=user_id, msg_id=msg_id)
        db.session.add(question)
        db.session.commit()

    return question.id


# def search_bert(content, query, question_id) -> Answer:
#     pass


def search_ingest(query, question_id) -> Union[Answer, None]:
    knowledge_pdf_content = current_app.ingest_connector.search(query)

    if not knowledge_pdf_content:
        return None

    answer = Answer(
        text=knowledge_pdf_content.content,
        question_fk=question_id,
        predictor_fk=Predictor.query.filter_by(name="ingest").first().id
    )
    db.session.add(answer)
    db.session.commit()

    return answer


def api_search_elastic(query) -> dict:
    knowledge_question: KnowledgeQuestion = KnowledgeQuestion.search(query)
    knowledge_answer: KnowledgeAnswer = KnowledgeAnswer.search(query)

    if not knowledge_answer and not knowledge_question:
        return {"success": False}

    resp = {
        "success": True,
        "answer": knowledge_answer.serialize,
    }

    if knowledge_answer.text != knowledge_question.knowledge_answer.text:
        resp.update({"question_answer": knowledge_question.knowledge_answer.serialize})

    return resp


def search_elastic(query, question_id) -> Union[Answer, None]:
    knowledge_question: KnowledgeQuestion = KnowledgeQuestion.search(query)
    knowledge_answer: KnowledgeAnswer = KnowledgeAnswer.search(query)

    if not knowledge_answer and not knowledge_question:
        return None

    answer_text = knowledge_answer.text
    question_answer_text = knowledge_question.knowledge_answer.text
    if answer_text != question_answer_text:
        answer_text = knowledge_answer.text + "\n\n_АБО_\n\n" + knowledge_question.knowledge_answer.text

    answer = Answer(
        text=answer_text,
        question_fk=question_id,
        predictor_fk=Predictor.query.filter_by(name="qa").first().id
    )
    db.session.add(answer)
    db.session.commit()

    return answer
