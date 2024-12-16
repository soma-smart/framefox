from pydantic import create_model
from sqlalchemy import Column, Integer, String
from src.core.orm.abstract_entity import AbstractEntity


class User(AbstractEntity):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

# Fonction pour générer les classes Pydantic


def generate_pydantic_models(entity_class):
    fields = {col.name: (col.type.python_type, ...)
              for col in entity_class.__table__.columns if col.name != 'id'}
    create_model_name = f"{entity_class.__name__}Create"
    response_model_name = f"{entity_class.__name__}Response"

    create_model_class = create_model(create_model_name, **fields)
    response_fields = {col.name: (col.type.python_type, ...)
                       for col in entity_class.__table__.columns}
    response_model_class = create_model(response_model_name, **response_fields)

    return create_model_class, response_model_class


# Générer les classes UserCreate et UserResponse
UserCreate, UserResponse = generate_pydantic_models(User)
