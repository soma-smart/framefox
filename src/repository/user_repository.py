# from abc import ABC
from sqlalchemy.orm import Session
from src.entity.user import User, UserCreate
from src.core.orm.config.database import SessionLocal


class UserRepository():
    """
    AbstractRepository provides the following methods:

    - find(id): Retrieve an entity by its ID.
    - find_all(): Retrieve all entities.
    - add(entity): Add a new entity.
    - update(entity): Update an existing entity.
    - delete(entity): Delete an entity.
    - find_by(criteria): Retrieve entities based on specific criteria.
    """

    def __init__(self):
        self.db: Session = SessionLocal()

    def add(self, user: UserCreate):
        db_user = User(name=user.name)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: int):
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return db_user
        return None

    def __del__(self):
        self.db.close()
