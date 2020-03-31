from app import db
from app.elastic.search import add_to_index, query_index, remove_from_index


class SearchableMixin:
    @classmethod
    def search(cls, expression):
        ids = query_index(cls.__tablename__, expression)

        if len(ids) == 0:
            return None

        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        res = cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)
        ).all()
        return res[0] if len(res) > 0 else None

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
