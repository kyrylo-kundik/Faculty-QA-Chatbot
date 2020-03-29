import datetime

from app import db
from app.elastic.models import SearchableMixin


class User(db.Model):
    __tablename__ = "user"

    tg_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    first_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String)

    joined_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), nullable=False)
    last_active_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), nullable=False)


class Predictor(db.Model):
    __tablename__ = "predictor"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)


class Question(db.Model):
    __tablename__ = "question"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    chat_id = db.Column(db.Integer, nullable=False)
    msg_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), nullable=False)

    answers = db.relationship("Answer")

    user_fk = db.Column(db.Integer, db.ForeignKey(
        'user.tg_id',
        ondelete='RESTRICT',
    ), nullable=False)


class Answer(db.Model):
    __tablename__ = "answer"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer)
    msg_id = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow(), nullable=False)

    question_fk = db.Column(db.Integer, db.ForeignKey(
        'question.id',
        ondelete='RESTRICT',
    ), nullable=False)
    predictor_fk = db.Column(db.Integer, db.ForeignKey(
        'predictor.id',
        ondelete='RESTRICT',
    ), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "text": self.text,
            "rating": self.rating,
            "msg_id": self.msg_id,
            "created_at": self.created_at,
            "question_fk": self.question_fk,
            "predictor_fk": self.predictor_fk,
        }


class KnowledgeQuestion(SearchableMixin, db.Model):
    __tablename__ = "knowledge_question"

    __searchable__ = ["text"]

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)

    knowledge_answer_fk = db.Column(db.Integer, db.ForeignKey(
        'knowledge_answer.id',
    ), nullable=False)
    knowledge_answer = db.relationship('KnowledgeAnswer', back_populates='knowledge_question')


class KnowledgeAnswer(SearchableMixin, db.Model):
    __tablename__ = "knowledge_answer"

    __searchable__ = ["text"]

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)

    knowledge_question = db.relationship('KnowledgeQuestion', back_populates='knowledge_answer')

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "id": self.id,
            "text": self.text,
        }


class KnowledgePdfContent(db.Model):
    __tablename__ = "knowledge_pdf_content"

    id = db.Column(db.Integer, primary_key=True)
    content_page = db.Column(db.Integer, nullable=False)
    content_paragraph = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String, nullable=False)
