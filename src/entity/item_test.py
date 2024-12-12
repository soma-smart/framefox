from src.core.orm.config.database import db


class ItemTest(db.Model):
    """
    Example
    """
    __tablename__ = 'items_test'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        column_values = ', '.join(f"{column.name}={getattr(
            self, column.name)}" for column in self.__table__.columns)
        return f"<ItemTest({column_values})>"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @staticmethod
    def required_fields():
        return [column.name for column in ItemTest.__table__.columns if not column.nullable and not column.primary_key]
