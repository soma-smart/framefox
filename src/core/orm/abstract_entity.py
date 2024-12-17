from sqlalchemy.ext.declarative import declarative_base, declared_attr
from pydantic import create_model

Base = declarative_base()


class AbstractEntity(Base):
    __abstract__ = True

    @classmethod
    def generate_models_response(cls):
        """
        Generate the response model class.

        Returns:
            The response model class.
        """
        response_model_class = cls.generate_response_model(cls)
        return response_model_class

    @classmethod
    def generate_models_create(cls):
        """
        Generate the create model class.

        Returns:
            The create model class.
        """
        create_model_class = cls.generate_create_model(cls)
        return create_model_class

    @declared_attr
    def __tablename__(cls):
        """
        Return the lowercase name of the class as the table name.

        Returns:
            str: The lowercase name of the class.
        """
        return cls.__name__.lower()

    @classmethod
    def create_table(cls, engine):
        """
        Create the table for the entity.

        Args:
            engine (sqlalchemy.engine.Engine): The SQLAlchemy engine to use.

        Returns:
            None
        """
        cls.metadata.create_all(engine)

    def generate_create_model(entity_class):
        """
        Generate a create model class for the given entity class.

        Args:
            entity_class (class): The entity class for which to generate the create model.

        Returns:
            class: The create model class.
        """
        fields = {
            col.name: (col.type.python_type, ...)
            for col in entity_class.__table__.columns
            if col.name != "id"
        }
        create_model_name = f"{entity_class.__name__}Create"

        create_model_class = create_model(create_model_name, **fields)

        return create_model_class

    def generate_response_model(entity_class):
        """
        Generate a response model for the given entity class.

        Args:
            entity_class (class): The entity class for which to generate the response model.

        Returns:
            The response model class.
        """
        response_fields = {
            col.name: (col.type.python_type, ...)
            for col in entity_class.__table__.columns
        }
        response_model_name = f"{entity_class.__name__}Response"

        response_model_class = create_model(
            response_model_name,
            **response_fields,
            # __config__=type("Config", (), {"orm_mode": True, "from_attributes": True}),
            __config__=type("Config", (), {"from_attributes": True}),
        )

        return response_model_class
