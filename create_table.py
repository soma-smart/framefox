from sqlalchemy import create_engine
from src.core.orm.config.database import SQLALCHEMY_DATABASE_URL
from src.entity.user import User

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Crée la table User dans la base de données
User.create_table(engine)
