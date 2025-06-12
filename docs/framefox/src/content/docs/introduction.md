---
title: Introduction to Framefox
description: Learn about Framefox, a modern Python web framework built with clean architecture principles
---

**Framefox** is a modern Python web framework designed to bring **best practices from day one** to web development. Built from the ground up with object-oriented programming, SOLID principles, and clean code practices, Framefox empowers developers to create maintainable, scalable, and robust web applications.

Whether you're a seasoned developer or just starting your programming journey, Framefox provides the structure and tools needed to build professional web applications while learning industry best practices.

:::tip[Philosophy]
Framefox believes that **good architecture leads to good applications**. By enforcing clean code principles and proven design patterns, the framework helps you write code that is not only functional but also maintainable and enjoyable to work with.
:::

## What Makes Framefox Different?

### Best practices from day one in Python Web Development

While many Python web frameworks focus primarily on rapid prototyping or minimal setup, Framefox takes a different approach. It provides the structured organization and proven patterns of mature frameworks, while preserving Python's natural simplicity and readability.

**Core Principles:**
- **Structure over Convention**: Clear, explicit structure that scales from small projects to large applications
- **Quality over Speed**: Emphasizes code quality and maintainability from day one
- **Education through Implementation**: Learn best practices by using them in real projects
- **Type Safety**: Leverages Python's type hints and Pydantic for runtime validation

## Object-Oriented Programming (OOP) in Framefox

Framefox is built entirely with **object-oriented programming** principles, providing a structured approach to organizing your code through classes, inheritance, and encapsulation.

### Why OOP Matters

Object-oriented programming helps you:
- **Organize code logically** through classes that represent real-world concepts
- **Reuse code effectively** through inheritance and composition
- **Encapsulate data and behavior** within well-defined boundaries
- **Model complex relationships** between different parts of your application

### OOP in Practice with Framefox

```python
# Entity representing a real-world concept
from sqlmodel import Field
from pydantic import EmailStr

from framefox.core.orm.abstract_entity import AbstractEntity

class User(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(nullable=False

# Controller inheriting from AbstractController
class UserController(AbstractController):
    def __init__(self):
        # Dependency injection for loose coupling
        self.user_service = self._container.get_service("user_service")
    
    @Route("/users", "user.index")
    async def index(self) -> HTMLResponse:
        users = await self.user_service.get_all_users()
        return self.render("user/index.html", {"users": users})
```

In this example, you can see how Framefox uses OOP concepts:
- **Classes** represent entities (`User`) and controllers (`UserController`)
- **Inheritance** from base classes (`AbstractEntity`, `AbstractController`)
- **Encapsulation** of data validation and business logic
- **Composition** through dependency injection

**Learn More:**
- [Object-Oriented Programming Concepts](https://docs.python.org/3/tutorial/classes.html)
- [Python OOP Tutorial](https://realpython.com/python3-object-oriented-programming/)

## SOLID Principles in Action

Framefox implements the **SOLID principles** throughout its architecture, helping you write code that is maintainable, extensible, and testable.

### Understanding SOLID

**S - Single Responsibility Principle**: Each class should have only one purpose.
**O - Open/Closed Principle**: Software entities should be open for extension but closed for modification.
**L - Liskov Substitution Principle**: Objects should be replaceable with instances of their subtypes.
**I - Interface Segregation Principle**: Many client-specific interfaces are better than one general-purpose interface.
**D - Dependency Inversion Principle**: Depend on abstractions, not concretions.

### SOLID in Framefox Architecture

```python
# Single Responsibility: UserService only handles user-related business logic
class UserService:
    def __init__(self, user_repository: UserRepository, email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service
    
    async def create_user(self, user_data: dict) -> User:
        # Single responsibility: user creation logic
        user = User(**user_data)
        await self.user_repository.save(user)
        await self.email_service.send_welcome_email(user)
        return user

# Dependency Inversion: Controller depends on abstraction (service interface)
class UserController(AbstractController):
    def __init__(self):
        # Injected dependency, not concrete implementation
        self.user_service = self._container.get_service("user_service")
```

**Benefits of SOLID in Framefox:**
- **Testability**: Easy to mock dependencies and write unit tests
- **Maintainability**: Changes to one component don't ripple through the system
- **Extensibility**: Add new features without modifying existing code
- **Flexibility**: Modify one part without breaking others

**Learn More:**
- [SOLID Principles Explained](https://en.wikipedia.org/wiki/SOLID)
- [SOLID Principles in Python](https://realpython.com/solid-principles-python/)

## Clean Code Principles

Framefox enforces **clean code** practices through its architecture, naming conventions, and structure. Clean code is code that is easy to read, understand, and modify.

### Clean Code in Practice

```python
from fastapi import Request
from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from framefox.core.routing.decorator.route import Route

from src.entity.user import User
from src.form.user_registration_form import UserRegistrationForm
from src.services.user.user_service import UserService

# Descriptive names and clear structure
class UserRegistrationController(AbstractController):
    """Controller for managing user registration"""
    
    def __init__(self):
        self.entity_manager = EntityManagerInterface()
        self.user_service = UserService()
    
    @Route("/register", "user.register", methods=["GET", "POST"])
    async def register_new_user(self, request: Request):
        """Register a new user"""
        # Check if user is already logged in
        if self.get_user():
            return self.redirect(self.generate_url("dashboard.index"))
        
        # Create and handle form
        user = User()
        form = self.create_form(UserRegistrationForm, user)
        await form.handle_request(request)
        
        if form.is_submitted() and form.is_valid():
            try:
                form_data = dict(await request.form())
                success, message, created_user = await self.user_service.create_user(form_data)
                
                if success:
                    await self.login_user(created_user)
                    self.flash("success", "Registration successful! Welcome.")
                    return self.redirect(self.generate_url("dashboard.index"))
                else:
                    self.flash("error", message)
                    
            except Exception as e:
                self.flash("error", f"Registration error: {str(e)}")
        
        return self.render("user/register.html", {
            "form": form.create_view(),
            "user": user
        })
```

### Clean Code Benefits

- **Readability**: Code reads like well-written prose
- **Maintainability**: Easy to understand and modify months later
- **Debugging**: Clear structure makes finding issues straightforward
- **Collaboration**: Team members can easily understand each other's code

**Learn More:**
- [Clean Code by Robert C. Martin](https://github.com/MichaelAndish/Software-Engineering-Concepts/blob/master/References/Clean%20Code/clean-code-robert-martins.md)
- [Clean Code Principles](https://gist.github.com/wojteklu/73c6914cc446146b8b533c0988cf8d29)

## MVC Architecture Pattern

Framefox implements the **Model-View-Controller (MVC)** architectural pattern, providing clear separation of concerns and organized code structure.

### Understanding MVC

**Model**: Represents data and business logic (entities, repositories, services)
**View**: Handles presentation layer (templates, API responses)
**Controller**: Manages user input and coordinates between Model and View

### MVC in Framefox

```python
# MODEL: Entity representing data structure
class Product(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(gt=0)
    description: str | None = None

# MODEL: Repository handling data access
class ProductRepository(AbstractRepository):
    def __init__(self):
        super().__init__(Product)
    
    async def find_by_category(self, category_id: int) -> List[Product]:
        return await self.find_by({"category_id": category_id})

# CONTROLLER: Coordinating between Model and View
class ProductController(AbstractController):
    def __init__(self):
        self.product_repository = ProductRepository()
    
    @Route("/products", "product.index")
    async def index(self) -> HTMLResponse:
        # Controller gets data from Model
        products = await self.product_repository.find_all()
        
        # Controller passes data to View
        return self.render("product/index.html", {"products": products})
```

```html
<!-- templates/product/index.html -->
<!-- VIEW: Template handling presentation -->
<!DOCTYPE html>
<html>
<head>
    <title>Product Catalog</title>
</head>
<body>
    <h1>Our Products</h1>
    <div class="products">
        {% for product in products %}
            <div class="product-card">
                <h3>{{ product.name }}</h3>
                <p>{{ product.description }}</p>
                <span class="price">${{ product.price }}</span>
            </div>
        {% endfor %}
    </div>
</body>
</html>
```

### MVC Benefits

- **Separation of Concerns**: Each layer has a specific responsibility
- **Testability**: Each component can be tested independently
- **Maintainability**: Changes to one layer don't affect others
- **Team Collaboration**: Different developers can work on different layers
- **Reusability**: Models can be reused across different views and controllers

**Learn More:**
- [MVC Architecture Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
- [MVC in Web Development](https://developer.mozilla.org/en-US/docs/Glossary/MVC)

## Design Patterns in Framefox

Framefox leverages several proven **design patterns** to solve common programming problems in elegant and reusable ways.

### Repository Pattern

Encapsulates data access logic and provides a uniform interface for accessing data.

```python
# Abstract repository defining the interface
class AbstractRepository(ABC):
    async def find(self, id: int) -> Optional[T]:
        pass
    
    async def find_all(self) -> List[T]:
        pass
    
    async def save(self, entity: T) -> T:
        pass

# Concrete implementation
class UserRepository(AbstractRepository):
    async def find_by_email(self, email: str) -> Optional[User]:
        return await self.find_one_by({"email": email})
```

### Decorator Pattern

Adds behavior to functions without modifying their structure.

```python
# Route decorator adds routing behavior
@Route("/users/{id}", "user.show", methods=["GET"])
async def show_user(self, id: int):
    return await self.user_service.get_user(id)
```

**Learn More:**
- [Software Design Patterns](https://refactoring.guru/design-patterns)
- [Python Design Patterns](https://python-patterns.guide/)

## Why These Principles Matter

### For Junior Developers

- **Understand professional code organization**
- **Build habits** that will serve you throughout your career
- **Learn industry standards** from the beginning
- **Create portfolio projects** that demonstrate best practices

### For Senior Developers

- **Implement enterprise patterns** without boilerplate
- Build apps that **grow with your needs**
- **Keep your code clean** and readable
- **Mentor junior developers** through structured architecture

## Next Steps

Ready to experience clean, maintainable Python web development?

1. **[How do I get started?](/installation)** - Set up your development environment
2. **[How do I handle web requests?](/core/controllers)** - Learn the MVC controller layer
3. **[How do I work with data?](/core/database)** - Master entities and repositories
4. **[How do I organize business logic?](/advanced_features/services)** - Implement services with dependency injection
5. **[How do I secure my app?](/core/security)** - Build secure applications from the start

---

**Swift, smart, and a bit foxy!** - Framefox brings best practices from day one to Python web development, making it accessible to developers at every level.