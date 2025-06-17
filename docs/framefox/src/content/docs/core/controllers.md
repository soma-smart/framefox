---
title: Controllers
description: Complete guide to controllers in Framefox - handling HTTP requests, responses, and business logic coordination
---

Controllers are the heart of your Framefox application. They handle HTTP requests, orchestrate business logic, and return appropriate responses. Acting as the intermediary between your routes and your application's core functionality, controllers keep your code organized and maintainable.

In Framefox, controllers inherit from `AbstractController`, providing a rich set of methods for handling requests, rendering templates, managing redirects, and interfacing with services. This architecture promotes clean separation of concerns and makes your application easier to test and maintain.

:::tip[Best Practice]
Controllers should focus on handling HTTP concerns (request/response) and delegating business logic to services or repositories. This keeps your controllers thin and your application well-structured.
:::

:::note[Framework Architecture]
Framefox follows the MVC (Model-View-Controller) pattern where controllers serve as the coordination layer between your routes and business logic. They should not contain complex business rules but rather orchestrate the flow of data between different layers of your application.
:::

## Controller Architecture

### AbstractController Foundation

All Framefox controllers inherit from `AbstractController`, which provides essential functionality and follows dependency injection patterns for clean, testable code architecture.

The `AbstractController` base class establishes the foundation for all controller functionality in Framefox. It provides a consistent interface for handling HTTP requests, managing responses, and interfacing with the framework's core services. This inheritance model ensures that all controllers have access to the same set of powerful methods while maintaining a clean and predictable API.

```python
from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route

class UserController(AbstractController):
    def __init__(self):
        """
        Initialize controller with dependency injection.
        The parent constructor sets up essential framework services.
        """
        super().__init__()
```

### Creating Controllers

#### Interactive CLI Generation

Generate controllers using the framework's interactive command system that guides you through the creation process step by step.

```bash
framefox create controller
```

The CLI provides an interactive workflow with validation and helpful prompts:

```
What is the name of the controller ?(snake_case)
Controller name: user

✓ Controller created successfully: src/controller/user_controller.py
✓ View created successfully: templates/user/index.html
```

**Generated Controller Structure:**
```python
# src/controller/user_controller.py
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController

class UserController(AbstractController):
    @Route("/user", "user.index", methods=["GET"])
    async def index(self):
        return self.render("user/index.html")
```

**Generated Template:**
```html
# templates/user/index.html
<!DOCTYPE html>
<html>
<head>
    <title>User Index</title>
</head>
<body>
    <h1>User Index Page</h1>
    <p>Welcome to the User controller!</p>
</body>
</html>
```

#### Manual Controller Creation

For specialized functionality and custom implementations that require fine-grained control over the controller structure and behavior.

```python
# src/controller/user_controller.py
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from fastapi import Request
from src.repository.user_repository import UserRepository
from src.service.email_service import EmailService

class UserController(AbstractController):
    def __init__(self):
        self.user_repository = UserRepository()
        self.email_service = EmailService()
    
    @Route("/users", "user.index", methods=["GET"])
    async def index(self, request: Request):
        page = int(request.query_params.get("page", 1))
        search = request.query_params.get("search", "")
        
        users = await self.user_repository.find_paginated(
            page=page,
            search=search
        )
        
        return self.render("users/index.html", {
            "users": users,
            "search": search,
            "title": "User Management"
        })
    
    @Route("/users/{id}", "user.show", methods=["GET"])
    async def show(self, id: int):
        user = await self.user_repository.find_by_id(id)
        if not user:
            self.flash("error", "User not found")
            return self.redirect(self.generate_url("user.index"))
        
        return self.render("users/show.html", {
            "user": user,
            "title": f"User Profile: {user.name}"
        })
```

## AbstractController Methods

The `AbstractController` provides seven essential methods that cover all common controller requirements. Each method is designed for specific use cases and follows framework conventions for consistency and reliability.

### Template Rendering - `render(template_path, context=None)`

Renders HTML templates with data binding and returns an `HTMLResponse`. This is the primary method for generating web pages in your application, providing seamless integration with Jinja2 templating engine.

**Method Signature:**
```python
def render(self, template_path: str, context: dict = None) -> HTMLResponse
```

**Basic Usage:**
```python
@Route("/dashboard", "dashboard.index", methods=["GET"])
async def dashboard(self):
    users = await self.user_service.get_recent(limit=5)
    stats = await self.analytics_service.get_stats()
    
    return self.render("dashboard/index.html", {
        "users": users,
        "stats": stats,
        "page_title": "Dashboard Overview"
    })
```

**Advanced Template Context:**
```python
@Route("/users/{id}/profile", "user.profile", methods=["GET"])
async def profile(self, id: int):
    user = await self.user_service.get_by_id(id)
    recent_posts = await self.post_service.get_by_user(id, limit=5)
    
    return self.render("users/profile.html", {
        "user": user,
        "recent_posts": recent_posts,
        "meta": {
            "title": f"{user.name}'s Profile",
            "description": f"View {user.name}'s profile and recent activity"
        }
    })
```

### JSON API Responses - `json(data: dict, status: int = 200)`

Creates JSON responses for API endpoints with proper content-type headers and HTTP status codes. Essential for building RESTful APIs and handling AJAX requests.

**Method Signature:**
```python
def json(self, data: dict, status: int = 200) -> JSONResponse
```

**API Response Patterns:**
```python
@Route("/api/users", "api.user.index", methods=["GET"])
async def api_index(self):
    users = await self.user_service.get_all()
    return self.json({
        "users": [user.to_dict() for user in users],
        "total": len(users),
        "status": "success"
    })

@Route("/api/users/{id}", "api.user.show", methods=["GET"])
async def api_show(self, id: int):
    user = await self.user_service.get_by_id(id)
    if not user:
        return self.json({
            "error": "User not found",
            "code": "USER_NOT_FOUND"
        }, status=404)
    
    return self.json({
        "user": user.to_dict(),
        "status": "success"
    })
```

### URL Generation - `generate_url(route_name: str, **params)`

Generates type-safe URLs for named routes with parameter substitution, essential for maintaining URL consistency throughout your application and enabling easy route changes without breaking existing links.

**Method Signature:**
```python
def generate_url(self, route_name: str, **params) -> str
```

**URL Generation Examples:**
```python
@Route("/users/{id}/edit", "user.edit", methods=["GET"])
async def edit(self, id: int):
    user = await self.user_service.get_by_id(id)
    
    return self.render("users/edit.html", {
        "user": user,
        "urls": {
            "profile": self.generate_url("user.show", id=user.id),
            "index": self.generate_url("user.index"),
            "delete": self.generate_url("user.delete", id=user.id)
        }
    })
```

### HTTP Redirects - `redirect(location: str, code: int = 302)`

Performs HTTP redirects with proper status codes for navigation and form processing. Essential for implementing the Post-Redirect-Get pattern and handling authentication flows.

**Method Signature:**
```python
def redirect(self, location: str, code: int = 302) -> RedirectResponse
```

**Redirect Patterns:**
```python
@Route("/users", "user.create", methods=["POST"])
async def create(self, request: Request):
    try:
        form_data = await request.form()
        user = await self.user_service.create(form_data)
        
        self.flash("success", f"User {user.name} created successfully!")
        return self.redirect(self.generate_url("user.show", id=user.id))
        
    except ValidationError as e:
        self.flash("error", "Please correct the errors below")
        return self.redirect(self.generate_url("user.new"))
```

### Flash Messaging - `flash(category: str, message: str)`

Provides session-based messaging for user feedback that persists across redirects. Messages are automatically stored in the session and can be retrieved in templates for display to users.

**Method Signature:**
```python
def flash(self, category: str, message: str) -> None
```

**Flash Message Categories:**
```python
# Success notifications
self.flash("success", "User updated successfully!")

# Error messages
self.flash("error", "Failed to delete user. Please try again.")

# Warning notifications
self.flash("warning", "This action cannot be undone.")

# Informational messages
self.flash("info", "Your session will expire in 5 minutes.")
```

**Template Integration:**
```html
{% if get_flashed_messages() %}
    <div class="flash-messages">
        {% for category, message in get_flashed_messages() %}
            <div class="alert alert-{{ category }}">{{ message }}</div>
        {% endfor %}
    </div>
{% endif %}
```

### Form Creation - `create_form(form_type, entity=None)`

Creates and binds forms to entities for automatic data handling and validation. This method integrates with Framefox's form system to provide seamless form processing and validation.

**Method Signature:**
```python
def create_form(self, form_type, entity=None) -> Form
```

**Form Handling Example:**
```python
@Route("/users/create", "user.create", methods=["GET", "POST"])
async def create(self, request: Request):
    user = User()
    form = self.create_form(UserType, user)
    await form.handle_request(request)
    
    if form.is_submitted() and form.is_valid():
        await self.user_service.create(user)
        self.flash("success", "User created successfully!")
        return self.redirect(self.generate_url("user.index"))
    
    return self.render("users/create.html", {"form": form.create_view()})
```

### User Authentication - `get_user(user_class=None)`

Retrieves the currently authenticated user from the security context. Works across all authentication methods (form-based, JWT, OAuth) and returns the appropriate user object for the current request context.

**Method Signature:**
```python
def get_user(self, user_class=None) -> Optional[User]
```

**User Information Access:**
- **User Identity**: `current_user.id`, `current_user.email`
- **User Roles**: `current_user.roles` (list of role strings)
- **User Properties**: Any custom fields defined in your User entity
- **Authentication Type**: For OAuth users, `current_user.provider`
- **Virtual User Flag**: `current_user.is_virtual` for token-based users

**Use Case Example:**
You might want to know how user authentication works in practice. In an e-commerce app, when someone visits their profile page, `get_user()` retrieves their authentication data. For a Google OAuth user, it returns an object with `provider="google"`, while premium users get access to exclusive features based on their "ROLE_PREMIUM" status. Non-authenticated users are automatically redirected to login.

```python
@Route("/profile", "user.profile", methods=["GET"])
async def profile(self):
    current_user = self.get_user()
    if not current_user:
        return self.redirect(self.generate_url("auth.login"))
    
    is_admin = "ROLE_ADMIN" in current_user.roles
    
    return self.render("users/profile.html", {
        "user": current_user,
        "is_admin": is_admin,
        "auth_method": "oauth" if hasattr(current_user, 'provider') else "standard"
    })
```
## Dependency Injection

Dependency injection is a design pattern that enables loose coupling between components by automatically providing required dependencies rather than having objects create their own dependencies. In Framefox controllers, this pattern eliminates manual service instantiation and promotes testable, maintainable code architecture.

The framework implements constructor injection through Python's type hint system, analyzing method signatures at runtime to resolve and inject appropriate service instances. This approach follows the Inversion of Control principle, where the framework manages object creation and lifetime rather than your application code.

:::tip[Design Pattern Benefits]
Dependency injection promotes the SOLID principles by reducing coupling between classes, making your code more modular and easier to test. Services can be easily mocked or replaced without modifying controller code.
:::

:::note[Framework Integration]
Framefox's dependency injection integrates seamlessly with FastAPI's parameter resolution system, automatically distinguishing between injectable services and framework-native types like Request objects and path parameters.
:::

### Automatic Service Injection

Controller methods automatically receive injected services based on type hints, eliminating the need for manual service instantiation and configuration. The injection mechanism analyzes your method signatures during route registration, examining each parameter's type annotation to determine injection eligibility.

The framework intelligently differentiates between injectable services and framework-native types, ensuring that only registered services are injected while preserving FastAPI's natural parameter binding for requests, responses, and path variables. This smart filtering maintains clean separation between dependency injection and HTTP parameter handling.

**Service Resolution Process:**
1. **Type Analysis**: Framework examines method parameter type hints
2. **Service Lookup**: Container searches for registered service implementations
3. **Instance Resolution**: Framework creates or retrieves service instances
4. **Dependency Injection**: Services are automatically provided to method parameters

```python
from src.service.user_service import UserService
from src.repository.user_repository import UserRepository

class UserController(AbstractController):
    
    @Route("/users", "user.index", methods=["GET"])
    async def index(self, 
                   user_service: UserService,        # ✅ Resolved from DI container
                   user_repository: UserRepository,  # ✅ Auto-injected based on type hint
                   request: Request):                # ✅ FastAPI native - bypassed by injection
        
        # Services are ready to use without manual instantiation
        users = await user_service.get_paginated(page=1)
        return self.render("users/index.html", {"users": users})
```

**Parameter Type Resolution:**
- **✅ Injectable Types**: Custom services, repositories, framework components
- **⚠️ Bypassed Types**: FastAPI Request/Response, Pydantic models, primitive types
- **🔄 Optional Types**: Services with default values gracefully handle missing dependencies


**Discovery Locations and Patterns:**

- **Framework Components**: Built-in Framefox services like template renderers, form builders, and security providers
- **User Extensions**: Custom classes implementing service interfaces or marked with service annotations

The framework respects inheritance hierarchies and interface implementations, enabling powerful architectural patterns like strategy injection and polymorphic service resolution. Abstract base classes and protocols can define service contracts while concrete implementations are automatically wired based on type hints.

### Manual Service Access

While automatic injection handles most dependency resolution scenarios elegantly, the framework provides direct access to the dependency injection container for advanced use cases requiring dynamic service resolution or conditional dependency selection.

Manual access patterns are particularly valuable for factory implementations, runtime service selection based on configuration or request parameters, and scenarios where services require complex initialization logic that cannot be expressed through simple type hints.

The container API maintains service instances and handles circular dependency detection automatically, providing a robust foundation for complex dependency graphs while maintaining performance and reliability.

**Dynamic Service Resolution:**
```python
class UserController(AbstractController):
    
    @Route("/users/export", "user.export", methods=["GET"])
    async def export(self, request: Request):
        # Conditional service resolution based on request parameters
        export_format = request.query_params.get("format", "csv")
        user_service = self._container.get(UserService)
        
        # Factory pattern for format-specific exporters
        if export_format == "pdf":
            export_service = self._container.get(PdfExportService)
            media_type = "application/pdf"
        elif export_format == "excel":
            export_service = self._container.get(ExcelExportService)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            export_service = self._container.get(CsvExportService)
            media_type = "text/csv"
        
        users = await user_service.get_all()
        export_data = await export_service.export(users)
        
        return Response(
            content=export_data, 
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename=users.{export_format}"}
        )
```

**Container Interface Methods:**
- **`container.get(ServiceType)`** - Retrieve service instance by type
- **`container.has(ServiceType)`** - Check if service is registered
- **`container.set_instance(ServiceType, instance)`** - Manually set service instance
- **`container.get_by_tag(tag)`** - Get first service with tag
- **`container.get_all_by_tag(tag)`** - Get all services with tag
- **`container.register_factory(factory)`** - Register service factory

**Discovery Locations and Patterns:**
- **Framework Core**: All modules in `framefox.core.*` 
- **Controllers**: Classes in `src/controller/` directory (always scanned)
- **Services**: Classes in `src/service/` directory (background scan)
- **Repositories**: Classes in `src/repository/` directory (background scan)
- **Factory Support**: Services created via registered factories

**Error Handling:**
The container raises specific exceptions:
- **`ServiceNotFoundError`**: When service is not registered and cannot be auto-registered
- **`ServiceInstantiationError`**: When service creation fails
- **`CircularDependencyError`**: When circular dependencies are detected


**Graceful Degradation Patterns:**
```python
@Route("/dashboard", "dashboard.index", methods=["GET"])
async def dashboard(self, 
                   analytics_service: AnalyticsService,      # Required service
                   cache_service: CacheService = None,       # Optional with fallback
                   notification_service: Optional[NotificationService] = None):
    
    # Required service - injection failure raises RuntimeError
    stats = await analytics_service.get_daily_stats()
    
    # Optional service with graceful fallback
    if cache_service:
        cached_data = await cache_service.get("dashboard_data")
    else:
        cached_data = None  # Fallback to direct computation
    
    # Optional service using typing.Optional
    if notification_service:
        await notification_service.mark_dashboard_viewed()
```

**Error Handling Strategies:**
1. **Required Dependencies**: Missing services raise `RuntimeError` with descriptive messages
2. **Optional Dependencies**: Default values provide graceful fallback behavior
3. **Logging Integration**: Service resolution failures are logged for debugging
4. **Development Mode**: Enhanced error messages include service registration hints
## Request Handling

Framefox controllers use FastAPI's `Request` object to access all request data. The `Request` object provides comprehensive access to form data, JSON payloads, query parameters, headers, and path variables through standard FastAPI patterns. This approach leverages FastAPI's powerful request handling capabilities while maintaining Framefox's controller architecture.

**[📖 FastAPI Request Documentation →](https://fastapi.tiangolo.com/advanced/using-request-directly/)**

### Accessing Request Data

The FastAPI `Request` object exposes various properties and methods to access different types of request data. Understanding these properties is essential for building robust web applications that can handle different content types and data sources effectively.

**Available Request Properties:**
- **`await request.form()`** - Form data (multipart/form-data or application/x-www-form-urlencoded)
- **`await request.json()`** - JSON payload data from request body
- **`request.query_params`** - URL query parameters (?key=value&another=value)
- **`request.headers`** - HTTP headers including authorization, content-type, user-agent
- **`request.path_params`** - Path parameters extracted from URL patterns
- **`request.method`** - HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)
- **`request.url`** - Complete request URL with scheme, host, path, and query
- **`request.client`** - Client information including IP address and port
- **`await request.body()`** - Raw request body as bytes
- **`request.cookies`** - Request cookies sent by the client
- **`request.state`** - Application state attached to the request
- **`request.scope`** - ASGI scope containing low-level request information

### Comprehensive Request Handling

```python
@Route("/api/users/{user_id}/posts", "user.posts.create", methods=["POST"])
async def create_post(self, user_id: int, request: Request):
    # Form data from HTML forms or multipart uploads
    form_data = await request.form()
    title = form_data.get("title")
    uploaded_file = form_data.get("attachment")
    
    # JSON data from API requests
    try:
        json_data = await request.json()
        content = json_data.get("content")
        tags = json_data.get("tags", [])
    except Exception:
        json_data = None
    
    # Query parameters for filtering and options
    draft = request.query_params.get("draft", "false") == "true"
    tags_from_query = request.query_params.getlist("tags")
    page = int(request.query_params.get("page", 1))
    
    # Headers for authentication and content negotiation
    auth_token = request.headers.get("authorization")
    content_type = request.headers.get("content-type")
    accept_language = request.headers.get("accept-language", "en")
    
    # Client information for logging and security
    client_ip = request.client.host
    http_method = request.method
    full_url = str(request.url)
    
    return {
        "message": "Post created successfully",
        "user_id": user_id,
        "draft": draft,
        "client_ip": client_ip,
        "method": http_method
    }
```



## CRUD Controller Generation

Framefox simplifies CRUD development through automated controller generation that creates complete Create, Read, Update, Delete functionality with proper architecture patterns. Rather than manually building repetitive CRUD operations, the framework generates production-ready controllers with consistent patterns and best practices.

The CLI-driven approach ensures consistency across your application while saving development time and reducing boilerplate code. This automated generation follows established conventions and integrates seamlessly with Framefox's ORM, form system, and templating engine to provide a complete development solution.

**[📖 CRUD Design Patterns →](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete)**

### Automated CRUD Setup

Generate complete CRUD controllers using the interactive CLI that guides you through the entire setup process:

```bash
framefox create crud
```

**Interactive Workflow:**
```
What is the name of the entity you want to create a CRUD with ?(snake_case)
Entity name: post

What type of controller do you want to create?

1. API CRUD controller
2. Templated CRUD controller

CRUD controller type (1): 2

✓ CRUD Controller created successfully: src/controller/post_controller.py
✓ Form type created successfully: src/form/post_type.py
```

### Templated CRUD Controllers

Templated CRUD controllers generate HTML-based interfaces with complete form handling, validation, and view templates for traditional web applications. This approach is perfect for admin interfaces, content management systems, and user-facing web applications.

**Generated Routes and Methods:**
- **GET `/posts`** - `read_all()` - List all entities with pagination
- **GET `/post/create`** - `create()` - Show creation form
- **POST `/post/create`** - `create()` - Process form submission
- **GET `/post/{id}`** - `read()` - Display single entity
- **GET `/post/{id}/update`** - `update()` - Show edit form
- **POST `/post/{id}/update`** - `update()` - Process update
- **POST `/post/delete/{id}`** - `delete()` - Delete entity

**Generated Controller Structure:**
```python
# src/controller/post_controller.py
from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from framefox.core.routing.decorator.route import Route
from src.entity.post import Post
from src.form.post_type import PostType
from src.repository.post_repository import PostRepository

class PostController(AbstractController):
    def __init__(self, entityManager: EntityManagerInterface):
        self.entity_manager = entityManager
        self.repository = PostRepository()

    @Route("/posts", "post.read_all", methods=["GET"])
    async def read_all(self):
        items = self.repository.find_all()
        return self.render("post/index.html", {"items": items})

    @Route("/post/create", "post.create", methods=["GET", "POST"])
    async def create(self, request: Request):
        entity_instance = Post()
        form = self.create_form(PostType, entity_instance)
        await form.handle_request(request)
        
        if form.is_submitted() and form.is_valid():
            self.entity_manager.persist(entity_instance)
            self.entity_manager.commit()
            self.flash("success", "Post created successfully!")
            return self.redirect(self.generate_url("post.read_all"))

        return self.render("post/create.html", {"form": form.create_view()})
```

**Generated Template Structure:**
```
templates/post/
├── create.html     # Entity creation form with validation
├── index.html      # Entity listing with pagination and search
├── read.html       # Single entity display with actions
└── update.html     # Entity editing form with pre-filled data
```

**Generated Form Type:**
```python
# src/form/post_type.py
from framefox.core.form.form_type import FormType
from framefox.core.form.form_field import FormField

class PostType(FormType):
    def build_form(self):
        self.add_field('title', FormField('text', 
            label='Title', 
            required=True,
            attributes={'class': 'form-control'}
        ))
        self.add_field('content', FormField('textarea', 
            label='Content', 
            required=True,
            attributes={'class': 'form-control', 'rows': 10}
        ))
```

### API CRUD Controllers

API CRUD controllers generate RESTful JSON endpoints following industry standards and HTTP conventions for modern API development. These controllers are optimized for mobile applications, single-page applications, and microservice architectures.

:::note[RESTful Standards]
API CRUD controllers follow established conventions:
- [REST API Design Best Practices](https://restfulapi.net/) - RESTful architecture principles
- [HTTP Status Codes](https://httpstatuses.com/) - Proper status code usage
- [JSON API Specification](https://jsonapi.org/) - Standardized JSON response format
:::

**Generated Routes and Methods:**
- **GET `/posts`** - `index()` - List all resources with pagination
- **GET `/posts/{id}`** - `show()` - Retrieve specific resource
- **POST `/posts`** - `create()` - Create new resource
- **PUT `/posts/{id}`** - `update()` - Replace entire resource
- **PATCH `/posts/{id}`** - `patch()` - Partial resource update
- **DELETE `/posts/{id}`** - `destroy()` - Delete resource

**Generated API Controller Structure:**
```python
# src/controller/post_controller.py
from framefox.core.controller.abstract_controller import AbstractController
from framefox.core.routing.decorator.route import Route
from src.entity.post import Post
from src.repository.post_repository import PostRepository

class PostController(AbstractController):
    def __init__(self, entityManager: EntityManagerInterface):
        self.entity_manager = entityManager
        self.repository = PostRepository()

    @Route("/posts", "post.index", methods=["GET"])
    async def index(self):
        """GET /posts - Retrieve all post resources"""
        try:
            items = self.repository.find_all()
            return self.json({
                "posts": [item.dict() for item in items], 
                "total": len(items), 
                "status": "success"
            }, status=200)
        except Exception as e:
            return self.json({
                "error": "Failed to retrieve posts", 
                "message": str(e), 
                "status": "error"
            }, status=500)

    @Route("/posts", "post.create", methods=["POST"])
    async def create(self, data: Post.generate_create_model()):
        """POST /posts - Create a new post resource"""
        try:
            post = self.repository.model(**data.dict())
            self.entity_manager.persist(post)
            self.entity_manager.commit()
            self.entity_manager.refresh(post)

            return self.json({
                "post": post.dict(), 
                "message": "Post created successfully", 
                "status": "created"
            }, status=201)
        except Exception as e:
            return self.json({
                "error": "Failed to create post", 
                "message": str(e), 
                "status": "error"
            }, status=400)
```

### CRUD Architecture Benefits

The generated CRUD controllers provide several architectural advantages that make them suitable for production applications:

**Consistency**: All CRUD operations follow the same patterns and conventions, making the codebase predictable and easier to maintain. Developers can quickly understand and work with any CRUD controller in the project.

**Security**: Built-in validation, error handling, and security measures protect against common vulnerabilities. Form handling includes CSRF protection, input sanitization, and proper error handling.

**Maintainability**: Clean, readable code structure that's easy to modify and extend. The generated code serves as a solid foundation that can be customized for specific business requirements.

**Extensibility**: Generated controllers can be easily enhanced with custom business logic, additional endpoints, and specialized functionality while maintaining the core CRUD structure.

**Best Practices**: Follows established patterns for both web and API development, including proper HTTP status codes, RESTful conventions, and error handling strategies.

The generated controllers include comprehensive error handling, proper HTTP status codes, consistent response formats, and support for both full resource replacement (PUT) and partial updates (PATCH) following RESTful conventions. This ensures that your API endpoints are robust, predictable, and follow industry standards.

---

## Related Topics

**[❓ How to validate request data in Framefox controllers?](core/controllers/request-validation/)**  
**[📁 How to upload files using Framefox services?](core/controllers/file-upload/)**  
