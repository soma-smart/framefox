from sqlalchemy.ext.declarative import declarative_base, declared_attr
from pydantic import create_model

Base = declarative_base()


class AbstractEntity(Base):
    __abstract__ = True

    @classmethod
    def generate_models_response(cls):
        response_model_class = cls.generate_response_model(cls)
        return response_model_class

    @classmethod
    def generate_models_create(cls):
        create_model_class = cls.generate_create_model(cls)
        return create_model_class

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @classmethod
    def create_table(cls, engine):
        cls.metadata.create_all(engine)

    def generate_create_model(entity_class):
        fields = {col.name: (col.type.python_type, ...)
                  for col in entity_class.__table__.columns if col.name != 'id'}
        create_model_name = f"{entity_class.__name__}Create"

        create_model_class = create_model(create_model_name, **fields)

        return create_model_class

    def generate_response_model(entity_class):
        response_fields = {col.name: (col.type.python_type, ...)
                           for col in entity_class.__table__.columns}
        response_model_name = f"{entity_class.__name__}Response"

        # response_model_class = create_model(
        #     response_model_name, **response_fields)
        response_model_class = create_model(
            response_model_name, **response_fields,
            __config__=type(
                'Config', (), {'orm_mode': True, 'from_attributes': True})
        )

        return response_model_class
