

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


def main():
    # Créer une connexion à la base de données SQLite
    engine = create_engine('sqlite:///db.sqlite3', echo=True)

    # Créer les tables définies dans Base
    Base.metadata.create_all(engine)

    # Créer une session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Ajouter des utilisateurs
    users = [
        User(name='Alice'),
        User(name='Bob'),
        User(name='Charlie')
    ]

    session.add_all(users)
    session.commit()

    # Vérifier les données ajoutées
    for user in session.query(User).all():
        print(f'User ID: {user.id}, Name: {user.name}')


if __name__ == '__main__':
    main()
