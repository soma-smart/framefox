![Framefox](./docs/images/framefox.png?raw=true "Framefox")


## Documentation 
Our documentation is available 
<a href="https://soma-smart.github.io/doc-framefox/" class="button button-docs" target="_blank">
				 Here
			</a> :)


# Swift, smart, and a bit foxy !

- **Object-oriented framework**: Framefox is designed with an object-oriented approach, providing a structured and organized way to build your web applications.
- **Simplified development**: The framework is designed to simplify the development of robust, modular, and maintainable applications.
- **Clear MVC architecture**: Emphasizes a clear Model-View-Controller (MVC) architecture for better code organization and separation of concerns.
- **Productivity-driven philosophy**: Focuses on enhancing developer productivity with its intuitive structure and features.

Key features include an interactive terminal, a powerful routing system, advanced configuration management, pre-configured authentications and registration, ORM database management, and much more.

Dive into this documentation to discover how Framefox can transform your Python development experience.

Key features include an interactive terminal, a powerful routing system, advanced configuration management, pre-configured authentications and registration, ORM database management, and much more.



## How to test terminal locally without importing from pip ?

### Using venv

```bash
python -m venv env
source env/bin/activate
```
### Using Conda
```bash
conda create -n framefox_env python=3.12
conda activate framefox_env
```

### Then, to use framefox command
```bash
pip install -e .
```

## Contributing

We welcome contributions to Framefox! To ensure a smooth collaboration, please adhere to the following rules:

1. **Fork the Repository**
   - Create a personal fork of the repository on GitHub.

2. **Create a Branch**
   - Before making changes, create a new branch for your feature or bugfix:
     ```bash
     git checkout -b feature/your-feature-name
     ```

3. **Write Clear Commit Messages**
   - Use concise and descriptive commit messages to explain your changes.

4. **Follow the Code Style**
   - Adhere to the existing coding standards and style guidelines used in Framefox.

5. **Ensure Code Quality**
   - Write clean, readable, and well-documented code.
   - Include unit tests for new features and bug fixes.

6. **Update Documentation**
   - If your changes affect the documentation, update the relevant sections accordingly.

7. **Run Tests**
   - Ensure that all tests pass before submitting your pull request

8. **Submit a Pull Request**
   - After pushing your changes, submit a pull request against the `main` branch.
   - Provide a detailed description of your changes and their purpose.

9. **Be Respectful and Collaborative**
   - Communicate respectfully with other contributors.
   - Be open to feedback and willing to make necessary adjustments.

10. **Review and Respond Promptly**
    - Respond to feedback on your pull requests in a timely manner.

By following these guidelines, you help maintain the quality and integrity of the Framefox framework. Thank you for your contributions!

______________________ EVERYTHING AFTER HERE WILL BE REMOVED _____________________


## Project Tree

```
your-app/
├── config/
│   ├── application.yaml
│   ├── orm.yaml
│   └── security.yaml
├── src/
│   ├── controllers/
│   ├── entity/
│   ├── repository/
├── templates/
│   ├── base.html
├── var/
│   └── log/
├── venv/
├── .env
├── .gitignore
├── main.py
└── requirements.txt
```

### Entity
Entities are business objects that represent the application's data and are typically mapped to database tables. They are very easy to use due to their inheritance from the AbstractEntity class. Here is an example of a user entity:
```python
from sqlmodel import Field
from framefox.core.orm.abstract_entity import AbstractEntity
from datetime import datetime

class User(AbstractEntity, table=True):
    """
    Example entity representing a user.
    """

    id: int = Field(default=None, primary_key=True, description="The unique identifier of the user.")
    name: str = Field(index=True, description="The name of the user.")
    email: str = Field(index=True, description="The email address of the user.")
    age: int = Field(default=None, description="The age of the user.")
    created_at: datetime = Field(default=datetime.utcnow, description="The timestamp when the user was created.")
```
AbstractEntity is based on Pydantic, so it implements dynamic model creation that simplifies data validation. To use it, simply use:
```python
User.generate_create_model()
```
Will see later how to use it with a controller.

### Repository
A repository is a design pattern that encapsulates data access logic, centralizing data operations and promoting modular, testable, and maintainable code by abstracting the data access layer.
The repository inherits from the AbstractRepository, making its creation very easy. The idea is to simply connect the repository to the corresponding entity. Here is an example of UserRepository :
```python
from framefox.core.orm.abstract_repository import AbstractRepository
from src.entity.user import User


class UserRepository(AbstractRepository):
    def __init__(self):
        super().__init__(User)
```
Due to its ineritance, the repository implement many features such as :
- find(id): Retrieve an entity by its ID.
- find_all(): Retrieve all entities.
- find_by(criteria): Retrieve entities based on specific criteria.
- add(entity): Add a new entity.
- update(entity): Update an existing entity.
- delete(entity): Delete an entity.



# External DB 

```python
external_session = self.entity_manager.external_connection(
            "sqlite:///app.db")

query = text('SELECT * FROM user')
result = external_session.execute(query).mappings().all()
```

### Use repository with controllers
Thanks to repository and pydantic it is super easy to create a controller that refines routes. Here is an example of UserController that illustrate all features of UserRepository and the Pydantic data validation :
```python
from framefox.core.routing.decorator.route import Route
from src.repository.user_repository import UserRepository
from framefox.core.controller.abstract_controller import AbstractController
from typing import Optional, Dict


class UserController(AbstractController):
    """
    Example
    """

    def __init__(self):
        super().__init__()

    @Route("/users", "get_users", methods=["GET"])
    async def get_users(self):
        return UserRepository().find_all()

    @Route("/users/search", "search_users", methods=["POST"])
    async def search_users(
        self,
        criteria: Dict[str, str],
        order_by: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        users = UserRepository().find_by(
            criteria, order_by, limit, offset)
        return users

    @Route("/users/{id}", "get_user", methods=["GET"])
    async def get_user(self, id: int):
        return UserRepository().find(id)

    @Route("/users", "create_user", methods=["POST"])
    async def create_user(self, user: UserRepository().create_model):
        user_instance = UserRepository().model(**user.dict())
        UserRepository().add(user_instance)
        return None

    @Route("/users/{id}", "update_user", methods=["PUT"])
    async def update_user(self, id: int, user: UserRepository().create_model):
        return UserRepository().update(id, user)

    @Route("/users/{id}", "delete_user", methods=["DELETE"])
    async def delete_user(self, id: int):
        return UserRepository().delete(id)

```
Let's detail a bit this route :
```python
    @Route("/users", "create_user", methods=["POST"])
    async def create_user(self, user: UserRepository().create_model):
        user_instance = UserRepository().model(**user.dict())
        UserRepository().add(user_instance)
        return None
```
This line define the route by using the @Route decorator
```python
    @Route("/users", "create_user", methods=["POST"])
```
This function requires a user to do its magic. The user is a Pydantic creation model that validates if you give the correct data for user creation. In our example, at least the name and email are required:
```python
    async def create_user(self, user: UserRepository().create_model):
```
After all, the user object is instantiated and added to the database:
```python
        user_instance = UserRepository().model(**user.dict())
        UserRepository().add(user_instance)
        return None
```

## Configuration

Application configurations are defined in the `config` folder. The configuration files are in YAML format and include parameters for the database, sessions, security, and CORS.

- `application.yaml`: General application settings.
- `orm.yaml`: ORM (Object-Relational Mapping) settings.
- `security.yaml`: Security settings including authentication and authorization.


## Authors

- Boumaza Rayen - [@RayenBou](https://github.com/RayenBou)
- Raphaël Lerond - [@Vasulvius](https://github.com/Vasulvius)