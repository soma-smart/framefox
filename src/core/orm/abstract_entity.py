from src.core.orm.config.database import db
from src.core.orm.config.model_abc_meta import ModelABCMeta


class AbstractEntity(db.Model):
    __abstract__ = True
    __metaclass__ = ModelABCMeta

    @classmethod
    def __declare_last__(cls):
        cls.__tablename__ = cls.__name__

    def __repr__(self):
        column_values = ', '.join(f"{column.name}={getattr(
            self, column.name)}" for column in self.__table__.columns)
        return f"<{self.__class__.__name__}({column_values})>"

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    @classmethod
    def required_fields(cls):
        return [column.name for column in cls.__table__.columns if not column.nullable and not column.primary_key]
