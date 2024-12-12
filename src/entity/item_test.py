from src.core.orm.config.database import db
from src.core.orm.abstract_entity import AbstractEntity


# class ItemTest(db.Model):
class ItemTest(AbstractEntity):
    """
    Example
    """
    __tablename__ = 'items_test'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
