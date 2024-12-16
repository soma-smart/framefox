from fastapi import APIRouter, HTTPException
from src.entity.user import UserCreate, UserResponse
from src.repository.user_repository import UserRepository

router = APIRouter()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    user_repo = UserRepository()
    db_user = user_repo.add(user)
    return db_user


# @router.get("/users/{user_id}", response_model=UserResponse)
# def read_user(user_id: int):
#     user_repo = UserRepository(db)
#     db_user = user_repo.find(user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @router.get("/users/", response_model=List[UserResponse])
# def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     user_repo = UserRepository(db)
#     users = user_repo.find_all(skip=skip, limit=limit)
#     return users


# @router.put("/users/{user_id}", response_model=UserResponse)
# def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
#     user_repo = UserRepository(db)
#     db_user = user_repo.update(user_id, user)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


@router.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: int):
    user_repo = UserRepository()
    db_user = user_repo.delete(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
