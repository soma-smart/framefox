# Soma Framework Skeleton

## Introduction

Welcome to the **Soma Framework Skeleton**, a development framework designed to simplify the creation of robust and scalable web applications. This framework is built on FastAPI and SQLModel, and it integrates advanced features such as session management, authentication, entity and repository management, as well as custom middlewares.

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


### Controller

The main purpose of this framework is to make most functionalities easy to use. Controllers in this framework inherit from the AbstractController class, which provides several useful methods and integrates with the routing system.

#### Routing

Using the Route decorator class helps you define routes directly above your controller methods, making routing straightforward and intuitive. Every HTTP method is available.

```python
from src.core.controller.abstract_controller import AbstractController
from src.core.routing.decorator.route import Route

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
from src.core.controller.abstract_controller import AbstractController
from src.core.routing.decorator.route import Route
from src.core.session.session import Session
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


### Entity & Repository



### RequestStack Class

The `RequestStack` class allows you to manage request-specific data throughout the lifecycle of a request.

## Configuration

Application configurations are defined in the `config` folder. The configuration files are in YAML format and include parameters for the database, sessions, security, and CORS.

- `application.yaml`: General application settings.
- `orm.yaml`: ORM (Object-Relational Mapping) settings.
- `security.yaml`: Security settings including authentication and authorization.


