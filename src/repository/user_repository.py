from framefox.core.orm.abstract_repository import AbstractRepository
from src.entity.user import User


class UserRepository(AbstractRepository):
    def __init__(self):
        super().__init__(User)

    ###########
    # build your own query by using the QueryBuilder
    ###########

    # def get_user_by_email(self, email: str):

    #     query_builder = self.get_query_builder()
    #     return (
    #         query_builder
    #         .select()
    #         .where(self.model.email == email)
    #         .first()
    #     )
