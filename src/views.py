# from fastapi import APIRouter, HTTPException
# from typing import List, Optional, Dict
# from src.repository.user_repository import UserRepository

# router = APIRouter()

# # find


# @router.get("/users/{user_id}", response_model=UserRepository().response_model)
# def read_user(user_id: int):
#     user_repo = UserRepository()
#     db_user = user_repo.find(user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# # find all


# @router.get("/users/", response_model=List[UserRepository().response_model])
# def read_users():
#     user_repo = UserRepository()
#     users = user_repo.find_all()
#     return users


# # Find by


# @router.post("/users/find_by", response_model=List[UserRepository().response_model])
# def find_users_by(
#     criteria: Dict[str, str],
#     order_by: Optional[Dict[str, str]] = None,
#     limit: Optional[int] = None,
#     offset: Optional[int] = None,
# ):
#     user_repo = UserRepository()
#     users = user_repo.find_by(criteria, order_by, limit, offset)
#     return users


# # update


# @router.put("/users/{user_id}", response_model=UserRepository().response_model)
# def update_user(user_id: int, user: UserRepository().create_model):
#     user_repo = UserRepository()
#     db_user = user_repo.update(user_id, user)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# # add


# @router.post("/users/", response_model=UserRepository().response_model)
# def create_user(user: UserRepository().create_model):
#     user_repo = UserRepository()
#     db_user = user_repo.add(user)
#     return db_user


# # delete


# @router.delete("/users/{user_id}", response_model=UserRepository().response_model)
# def delete_user(user_id: int):
#     user_repo = UserRepository()
#     db_user = user_repo.delete(user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
