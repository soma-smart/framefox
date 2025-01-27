![Framefox](./docs/images/framefox.png?raw=true "Framefox")


# Documentation 
Our documentation is available 
<a href="https://soma-smart.github.io/doc-framefox/" class="button button-docs" target="_blank">
				 Here
			</a> :)



## Introduction

Framefox is a Object oriented Python Framework, that give you the fastest path in Python Environnement to Build you Web Application.

Designed to simplify the development of robust, modular, and maintainable applications, this framework emphasizes a clear MVC  architecture and a productivity-driven philosophy.
 
With its intuitive structure, it helps developers focus on building features while reducing code complexity. Offering simplicity for quick onboarding, modularity for well-structured code, extensibility for project-specific needs, and adherence to best practices for performance and security, this framework suits both beginners exploring foundational architectures and experts tackling complex projects. 
  
  
Key features include an interactive terminal,a powerful routing system,an advanced configuration management, pre-configured authentications and registration, ORM database management,and a lot more. 

Dive into this documentation to discover how Framefox can transform your Python development experience.


## How to test new terminal feature ?
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

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/soma/dev-framework-skeleton.git
    cd dev-framework-skeleton
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    uvicorn main:app --reload
    ```

## Usage

### Terminal Command

To start the development server, use the following command:
```bash
uvicorn main:app --reload
```


## Controller

The main purpose of this framework is to make most functionalities easy to use. Controllers in this framework inherit from the AbstractController class, which provides several useful methods and integrates with the routing system.

#### Routing

Using the Route decorator class helps you define routes directly above your controller methods, making routing straightforward and intuitive. Every HTTP method is available.

```python
from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route

class HomeController(AbstractController):

    @Route("/", "home", methods=["GET"])
    async def index(self):
        return self.render("index.html")
```

In this example, the `@Route` decorator is used to define a route for the index method. The route is accessible via the path `/` and responds to GET requests.

#### Methods Available from AbstractController



The AbstractController class provides several methods that can be used in your controllers:

- ** render(template_name: str, context_list: list)
- ** redirect(location: str, code: int = 302)
- ** flash(category: str, message: str)
- ** json(data: dict, status: int = 200)

#### Example Controller

Here is an example of a controller that uses the AbstractController methods:

```python
from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from framefox.core.session.session import Session
from src.repository.user_repository import UserRepository

class UserController(AbstractController):

    @Route("/users", "get_users", methods=["GET"])
    async def get_users(self):
        # Add a flash message
        self.flash("Welcome to the users page", "info")

        # Store a value in the session
        Session.set('last_visited', '/users')

        # Retrieve a value from the session
        last_visited = Session.get('last_visited')

        # Use the session data in your logic
        user_repository = UserRepository().find_all()

        return self.render("users.html", {
            "users": user_repository,
            "title": "User List",
            "last_visited": last_visited
        })
```

In this example, the UserController class defines a route for the `/users` path that responds to GET requests. The get_users method uses the flash, Session, and render methods provided by the AbstractController to manage flash messages, session data, and template rendering.






### RequestStack Class

The `RequestStack` class allows you to manage request-specific data throughout the lifecycle of a request.

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
