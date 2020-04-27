class User:
    def __init__(
            self,
            tg_id: int,
            first_name: str,
            username: str
    ):
        self.tg_id = tg_id
        self.first_name = first_name
        self.username = username

    def __repr__(self):
        return f"<User(tg_id={self.tg_id}, first_name={self.first_name}, username={self.username})>"


class Answer:
    def __init__(
            self,
            id_: int,
            text: str = None,
            predictor: str = None,
            rating: int = None,
            msg_id: int = None
    ):
        self.id_ = id_
        self.text = text
        self.predictor = predictor
        self.rating = rating
        self.msg_id = msg_id

    def __repr__(self):
        return f"<Answer(id_={self.id_}, text={self.text}, predictor={self.predictor}, rating={self.rating}, " \
               f"msg_id={self.msg_id})>"


class ExpertQuestion:
    def __init__(
            self,
            id_: int = None,
            question_text: str = None,
            question_msg_id: int = None,
            question_chat_id: int = None,
            expert_question_chat_id: int = None,
            expert_question_msg_id: int = None,
            expert_answer_msg_id: int = None,
            expert_answer_text: str = None,
            expert_user_fk: int = None
    ):
        self.id_ = id_
        self.question_text = question_text
        self.question_msg_id = question_msg_id
        self.question_chat_id = question_chat_id
        self.expert_question_chat_id = expert_question_chat_id
        self.expert_question_msg_id = expert_question_msg_id
        self.expert_answer_msg_id = expert_answer_msg_id
        self.expert_answer_text = expert_answer_text
        self.expert_user_fk = expert_user_fk

    def __repr__(self):
        return f"<ExpertQuestion(id_={self.id_}, question_text={self.question_text}, " \
               f"question_msg_id={self.question_msg_id}, question_chat_id={self.question_chat_id}, " \
               f"expert_question_chat_id={self.expert_question_chat_id}, " \
               f"expert_question_msg_id={self.expert_question_msg_id}, " \
               f"expert_answer_msg_id={self.expert_answer_msg_id}, expert_answer_text={self.expert_answer_text}, " \
               f"expert_user_fk={self.expert_user_fk})>"
