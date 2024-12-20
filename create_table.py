from sqlmodel import SQLModel, create_engine, Session
from src.entity.user import User
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError

# Charger les variables d'environnement
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_user():
    try:
        # Créer les tables définies dans les modèles SQLModel
        SQLModel.metadata.create_all(engine)

        # Initialiser une session
        with Session(engine) as session:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash("test")  # Mot de passe : test

            # Créer un utilisateur de test
            user = User(
                name="Test User",
                email="test@test.fr",
                password=hashed_password,
                roles=["ROLE_USER"],
            )
            session.add(user)
            session.commit()
            print("Utilisateur créé avec succès.")
    except OperationalError as e:
        print(
            f"Erreur lors de la création de la base de données ou de l'utilisateur : {e}"
        )


if __name__ == "__main__":
    create_db_and_user()
