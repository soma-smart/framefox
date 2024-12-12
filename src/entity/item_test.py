from src.core.orm.config.database import db
from src.core.orm.abstract_entity import AbstractEntity


class ItemTest(AbstractEntity):
    """
    Example
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
