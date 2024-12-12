from src.core.orm.config.database import db


class ItemTest(db.Model):
    """
    Example
    """
    __tablename__ = 'items_test'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<ItemTest {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
