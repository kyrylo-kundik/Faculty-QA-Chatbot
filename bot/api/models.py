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
        self.text = text,
        self.predictor = predictor
        self.rating = rating
        self.msg_id = msg_id
