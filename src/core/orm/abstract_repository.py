from abc import ABC
from src.core.orm.config.database import db


class AbstractRepository(ABC):
    def __init__(self, model):
        self.model = model

    def get_all(self):
        return self.model.query.all()

    def get_by_id(self, id):
        return self.model.query.get(id)

    def add(self, item):
        db.session.add(item)
        db.session.commit()

    def delete(self, item):
        db.session.delete(item)
        db.session.commit()
