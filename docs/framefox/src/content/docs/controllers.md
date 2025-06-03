---
title: Controllers
description: Complete guide to controllers in Framefox
---

# Controllers

Controllers are the heart of your Framefox application. They handle HTTP requests, orchestrate business logic, and return appropriate responses. Acting as the intermediary between your routes and your application's core functionality, controllers keep your code organized and maintainable.

In Framefox, controllers inherit from `AbstractController`, providing a rich set of methods for handling requests, rendering templates, managing redirects, and interfacing with services. This architecture promotes clean separation of concerns and makes your application easier to test and maintain.

:::tip[Best Practice]
Controllers should focus on handling HTTP concerns (request/response) and delegating business logic to services or repositories. This keeps your controllers thin and your application well-structured.
:::

:::info[Framework Architecture]
Framefox follows the MVC (Model-View-Controller) pattern where controllers serve as the coordination layer between your routes and business logic. They should not contain complex business rules but rather orchestrate the flow of data between different layers of your application.
:::

## Creating Controllers

### Using the Interactive Terminal

Framefox provides several commands to create different types of controllers through an interactive command-line interface that guides you through the process step by step.

:::warning[Prerequisites]
Before creating controllers, ensure that:
- Your Framefox project is properly initialized
- You're running commands from the project root directory
- Required directories (`src/controllers/`, `templates/`) exist
:::

#### Basic Controller Creation

```bash
framefox create controller
```

This interactive command will guide you through the controller creation process:

1. **Controller Name Prompt**: Enter the controller name in `snake_case` format
   - ✅ Valid: `user`, `blog_post`, `admin_dashboard`
   - ❌ Invalid: `User`, `blogPost`, `admin-dashboard`

2. **Automatic File Generation**:
   - Creates controller file in `src/controllers/{name}_controller.py`
   - Generates corresponding view template in `templates/{name}/index.html`
   - Sets up basic route structure with proper naming conventions

:::info[File Naming Convention]
Framefox follows Python naming conventions:
- Controller files: `{name}_controller.py`
- Controller classes: `{Name}Controller` (PascalCase)
- Template directories: `{name}/` (snake_case)
:::

#### CRUD Controller Creation

```bash
framefox create crud
```

This advanced command creates a complete CRUD (Create, Read, Update, Delete) controller:

1. **Entity Name Prompt**: Must correspond to an existing model and repository
2. **Controller Type Selection**:
   - **Option 1**: API CRUD controller (RESTful JSON endpoints)
   - **Option 2**: Templated CRUD controller (HTML forms and views)

:::danger[Entity Requirements]
The entity must already exist in your project:
- Model class in `src/entity/{entity_name}.py`
- Repository class in `src/repository/{entity_name}_repository.py`
- Proper SQLAlchemy/SQLModel configuration

Without these, the command will fail with an error message.
:::

**For Templated CRUD Controllers**, the command automatically generates:
- Complete CRUD controller with all HTTP methods
- Form types for entity manipulation (`src/form/{entity_name}_type.py`)
- HTML templates in `templates/{entity_name}/`:
  - `create.html` - Entity creation form
  - `read.html` - Single entity display
  - `update.html` - Entity editing form
  - `index.html` - Entity listing with pagination
- Proper view folder structure with consistent styling

## Generated Controller Examples

The Framefox CLI generates well-structured, production-ready code that follows framework conventions and best practices. Let's examine what gets generated for different controller types.

### Basic Controller Generation

When you run `framefox create controller` with the name "user", the CLI generates:

**File:** `src/controllers/user_controller.py`
```python
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController

class UserController(AbstractController):
    @Route("/user", "user.index", methods=["GET"])
    async def index(self):
        return self.render("user/index.html")
```

**File:** `templates/user/index.html`
```html
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

:::tip[Template Inheritance]
Consider extending from a base template for consistent styling:
```html
{% extends "base.html" %}
{% block content %}
    <h1>User Index Page</h1>
    <p>Welcome to the User controller!</p>
{% endblock %}
```
:::

### CRUD Controller Generation

CRUD generation creates comprehensive, database-ready controllers with full Create, Read, Update, Delete functionality.

:::info[Entity Relationship]
CRUD controllers automatically establish relationships with your data layer:
- **Entity**: The data model representing your database table
- **Repository**: The data access layer for database operations
- **Form Type**: Form handling and validation logic
- **Templates**: User interface for data manipulation
:::

#### API CRUD Controller Example

For an entity called "post", the API CRUD controller (`src/controllers/post_controller.py`) includes:

```python
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from src.repository.post_repository import PostRepository
from src.entity.post import Post
from fastapi import Request
import json

class PostController(AbstractController):
    def __init__(self):
      
        self.post_repository = PostRepository()
    
    @Route("/api/posts", "api.post.index", methods=["GET"])
    async def index(self):
        """Retrieve all posts with pagination support."""
        posts = await self.post_repository.find_all()
        return self.json({
            "posts": [post.to_dict() for post in posts],
            "total": len(posts),
            "status": "success"
        })
    
    @Route("/api/posts", "api.post.create", methods=["POST"])
    async def create(self, request: Request):
        """Create a new post from JSON data."""
        try:
            data = await request.json()
            post = Post(**data)
            created_post = await self.post_repository.save(post)
            return self.json({
                "post": created_post.to_dict(),
                "message": "Post created successfully",
                "status": "success"
            }, status=201)
        except Exception as e:
            return self.json({
                "error": str(e),
                "status": "error"
            }, status=400)
    
    @Route("/api/posts/{id}", "api.post.show", methods=["GET"])
    async def show(self, id: int):
        """Retrieve a specific post by ID."""
        post = await self.post_repository.find_by_id(id)
        if not post:
            return self.json({"error": "Post not found"}, status=404)
        return self.json({"post": post.to_dict()})
    
    @Route("/api/posts/{id}", "api.post.update", methods=["PUT"])
    async def update(self, id: int, request: Request):
        """Update an existing post."""
        data = await request.json()
        updated_post = await self.post_repository.update(id, data)
        if not updated_post:
            return self.json({"error": "Post not found"}, status=404)
        return self.json({
            "post": updated_post.to_dict(),
            "message": "Post updated successfully"
        })
    
    @Route("/api/posts/{id}", "api.post.delete", methods=["DELETE"])
    async def delete(self, id: int):
        """Delete a post by ID."""
        success = await self.post_repository.delete(id)
        if not success:
            return self.json({"error": "Post not found"}, status=404)
        return self.json({"message": "Post deleted successfully"})
```

#### Templated CRUD Controller Example

The templated CRUD controller generates HTML-based interfaces:

```python
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from src.repository.post_repository import PostRepository
from src.form.post_type import PostType
from src.entity.post import Post
from fastapi import Request

class PostController(AbstractController):
    def __init__(self):
        self.post_repository = PostRepository()
    
    @Route("/posts", "post.index", methods=["GET"])
    async def index(self):
        """Display all posts in a paginated table."""
        posts = await self.post_repository.find_all()
        return self.render("post/index.html", {
            "posts": posts,
            "title": "All Posts"
        })
    
    @Route("/posts/create", "post.create", methods=["GET"])
    async def create(self):
        """Show the post creation form."""
        form = self.create_form(PostType, Post())
        return self.render("post/create.html", {
            "form": form,
            "title": "Create New Post"
        })
    
    @Route("/posts", "post.store", methods=["POST"])
    async def store(self, request: Request):
        """Handle post creation form submission."""
        form_data = await request.form()
        form = self.create_form(PostType, Post())
        
        if form.validate(form_data):
            post = form.get_entity()
            await self.post_repository.save(post)
            self.flash("success", "Post created successfully!")
            return self.redirect(self.generate_url("post.index"))
        
        return self.render("post/create.html", {
            "form": form,
            "title": "Create New Post"
        })
    
    @Route("/posts/{id}", "post.show", methods=["GET"])
    async def show(self, id: int):
        """Display a single post."""
        post = await self.post_repository.find_by_id(id)
        if not post:
            self.flash("error", "Post not found")
            return self.redirect(self.generate_url("post.index"))
        
        return self.render("post/show.html", {
            "post": post,
            "title": f"Post: {post.title}"
        })
    
    @Route("/posts/{id}/edit", "post.edit", methods=["GET"])
    async def edit(self, id: int):
        """Show the post editing form."""
        post = await self.post_repository.find_by_id(id)
        if not post:
            self.flash("error", "Post not found")
            return self.redirect(self.generate_url("post.index"))
        
        form = self.create_form(PostType, post)
        return self.render("post/edit.html", {
            "form": form,
            "post": post,
            "title": f"Edit: {post.title}"
        })
    
    @Route("/posts/{id}", "post.update", methods=["POST"])
    async def update(self, id: int, request: Request):
        """Handle post update form submission."""
        post = await self.post_repository.find_by_id(id)
        if not post:
            self.flash("error", "Post not found")
            return self.redirect(self.generate_url("post.index"))
        
        form_data = await request.form()
        form = self.create_form(PostType, post)
        
        if form.validate(form_data):
            updated_post = form.get_entity()
            await self.post_repository.update(id, updated_post)
            self.flash("success", "Post updated successfully!")
            return self.redirect(self.generate_url("post.show", id=id))
        
        return self.render("post/edit.html", {
            "form": form,
            "post": post,
            "title": f"Edit: {post.title}"
        })
    
    @Route("/posts/{id}/delete", "post.destroy", methods=["POST"])
    async def destroy(self, id: int):
        """Delete a post."""
        success = await self.post_repository.delete(id)
        if success:
            self.flash("success", "Post deleted successfully!")
        else:
            self.flash("error", "Failed to delete post")
        
        return self.redirect(self.generate_url("post.index"))
```

:::warning[Form Security]
Always validate form data and sanitize user input:
- Use form types for validation
- Implement CSRF protection
- Sanitize HTML content
- Validate file uploads
:::

**Generated Templates Structure:**
```
templates/post/
├── index.html      # Post listing with pagination
├── create.html     # Post creation form
├── show.html       # Single post display
├── edit.html       # Post editing form
└── _form.html      # Reusable form partial
```

### Manual Controller Creation

For maximum control over your controller structure, you can create controllers manually. This approach is ideal when you need custom logic that doesn't fit the standard patterns or when you're building specialized controllers.

:::tip[When to Use Manual Creation]
Choose manual creation when:
- Building API endpoints with custom logic
- Creating specialized controllers (webhooks, file uploads, etc.)
- Implementing complex business logic
- Need fine-grained control over routing and methods
:::

**Example:** `src/controllers/user_controller.py`

```python
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from fastapi import Request, HTTPException
from src.repository.user_repository import UserRepository
from src.service.email_service import EmailService

class UserController(AbstractController):
    def __init__(self):
        """Initialize controller with dependencies."""
        self.user_repository = UserRepository()
        self.email_service = EmailService()
    
    @Route("/users", "user.index", methods=["GET"])
    async def index(self, request: Request):
        """Display a paginated list of all users with filtering."""
        # Extract query parameters
        page = int(request.query_params.get("page", 1))
        per_page = int(request.query_params.get("per_page", 10))
        search = request.query_params.get("search", "")
        
        # Get filtered and paginated results
        users = await self.user_repository.find_paginated(
            page=page,
            per_page=per_page,
            search=search
        )
        
        # For API responses
        if request.headers.get("accept") == "application/json":
            return self.json({
                "users": [user.to_dict() for user in users.items],
                "pagination": {
                    "page": users.page,
                    "per_page": users.per_page,
                    "total": users.total,
                    "pages": users.pages
                }
            })
        
        # For HTML responses
        return self.render("users/index.html", {
            "users": users,
            "search": search,
            "title": "User Management"
        })
    
    @Route("/users/{id}", "user.show", methods=["GET"])
    async def show(self, id: int):
        """Display a specific user with error handling."""
        try:
            user = await self.user_repository.find_by_id(id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return self.render("users/show.html", {
                "user": user,
                "title": f"User Profile: {user.name}"
            })
        except Exception as e:
            self.flash("error", f"Error loading user: {str(e)}")
            return self.redirect(self.generate_url("user.index"))
    
    @Route("/users/{id}/send-welcome", "user.send_welcome", methods=["POST"])
    async def send_welcome_email(self, id: int):
        """Custom endpoint to send welcome email."""
        user = await self.user_repository.find_by_id(id)
        if not user:
            return self.json({"error": "User not found"}, status=404)
        
        try:
            await self.email_service.send_welcome_email(user)
            self.flash("success", f"Welcome email sent to {user.email}")
            return self.json({"message": "Welcome email sent successfully"})
        except Exception as e:
            return self.json({"error": str(e)}, status=500)
```

:::warning[Error Handling]
Always implement proper error handling in manual controllers:
- Use try-catch blocks for database operations
- Validate input parameters
- Return appropriate HTTP status codes
- Log errors for debugging
:::

## Controller Architecture & Design Patterns

### AbstractController Base Class

All Framefox controllers inherit from `AbstractController`, which provides a comprehensive set of methods and follows dependency injection patterns for clean, testable code.

```python
from framefox.core.controller.abstract_controller import AbstractController

class MyController(AbstractController):
    def __init__(self):
        """
        Initialize controller with dependency injection.
        The parent constructor sets up essential services.
        """
        # Access to service container
        # Template renderer automatically configured
        # Session and flash messaging available
        
        # Inject your own dependencies
        self.custom_service = self._container.get_by_name("CustomService")
```

:::info[Dependency Injection]
Framefox uses a powerful dependency injection container that:
- Automatically resolves service dependencies
- Provides access to framework services (templating, routing, etc.)
- Enables easy testing through service mocking
- Follows inversion of control principles
:::

### Service Container Integration

The `AbstractController` provides seamless integration with Framefox's service container:

```python
class AdvancedController(AbstractController):
    def __init__(self):
        
        # Access framework services
        self.router = self._container.get_by_name("Router")
        self.session = self._container.get_by_name("Session")
        self.logger = self._container.get_by_name("Logger")
        
        # Access your custom services
        self.user_service = self._container.get_by_name("UserService")
        self.notification_service = self._container.get_by_name("NotificationService")
    
    async def complex_operation(self):
        """Example of using multiple services together."""
        current_user = self.get_user()
        await self.user_service.update_last_activity(current_user)
        await self.notification_service.mark_as_read(current_user.id)
        
        self.logger.info(f"User {current_user.id} performed complex operation")
```

## Complete AbstractController API Reference

The `AbstractController` provides 7 essential methods that cover all common controller needs. Each method is designed for specific use cases and follows framework conventions.

:::tip[Method Overview]
- **`render()`** - Template rendering for HTML responses
- **`json()`** - JSON API responses with status codes
- **`redirect()`** - URL redirections with status codes
- **`generate_url()`** - Type-safe URL generation
- **`flash()`** - Session-based messaging
- **`create_form()`** - Form instantiation and binding
- **`get_user()`** - Authentication and user management
:::

### 1. Template Rendering - `render(template_path, context=None)`

Renders HTML templates with data binding and returns an `HTMLResponse`. This is the primary method for generating web pages in your application.

**Method Signature:**
```python
def render(self, template_path: str, context: dict = None) -> HTMLResponse
```

**Parameters:**
- `template_path` (str): Path to the template file relative to the templates directory
- `context` (dict, optional): Variables to pass to the template

**Basic Usage:**
```python
@Route("/users", "user.index", methods=["GET"])
async def index(self):
    users = await self.user_service.get_all()
    return self.render("users/index.html", {
        "users": users,
        "title": "User Management",
        "current_page": "users"
    })
```

**Advanced Usage with Complex Data:**
```python
@Route("/dashboard", "dashboard.index", methods=["GET"])
async def dashboard(self):
    # Gather multiple data sources
    recent_users = await self.user_service.get_recent(limit=5)
    stats = await self.analytics_service.get_dashboard_stats()
    notifications = await self.notification_service.get_unread()
    
    return self.render("dashboard/index.html", {
        "recent_users": recent_users,
        "stats": stats,
        "notifications": notifications,
        "page_title": "Dashboard Overview",
        "sidebar_active": "dashboard"
    })
```

:::tip[Template Organization]
Structure your templates logically:
```
templates/
├── base.html              # Base layout
├── components/            # Reusable components
│   ├── navbar.html
│   └── pagination.html
├── users/                 # User-related templates
│   ├── index.html
│   ├── show.html
│   └── edit.html
└── dashboard/
    └── index.html
```
:::

:::warning[Template Security]
Always escape user-generated content to prevent XSS attacks:
```html
<!-- Safe: automatically escaped -->
<h1>{{ user.name }}</h1>

<!-- Dangerous: unescaped HTML -->
<div>{{ user.bio | safe }}</div>

<!-- Better: use a filter for safe HTML -->
<div>{{ user.bio | clean_html }}</div>
```
:::

### 2. JSON API Responses - `json(data: dict, status: int = 200)`

Creates JSON responses for API endpoints with proper content-type headers and status codes.

**Method Signature:**
```python
def json(self, data: dict, status: int = 200) -> JSONResponse
```

**Parameters:**
- `data` (dict): The data to serialize to JSON
- `status` (int): HTTP status code (default: 200)

**Basic API Response:**
```python
@Route("/api/users", "api.user.index", methods=["GET"])
async def api_index(self):
    users = await self.user_service.get_all()
    return self.json({
        "users": [user.to_dict() for user in users],
        "total": len(users),
        "status": "success"
    })
```

**Error Handling with Status Codes:**
```python
@Route("/api/users/{id}", "api.user.show", methods=["GET"])
async def api_show(self, id: int):
    try:
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
    except Exception as e:
        return self.json({
            "error": "Internal server error",
            "message": str(e),
            "code": "INTERNAL_ERROR"
        }, status=500)
```

**Structured API Responses:**
```python
@Route("/api/posts", "api.post.create", methods=["POST"])
async def api_create_post(self, request: Request):
    try:
        data = await request.json()
        post = await self.post_service.create(data)
        
        return self.json({
            "data": {
                "post": post.to_dict(),
                "links": {
                    "self": self.generate_url("api.post.show", id=post.id),
                    "edit": self.generate_url("api.post.update", id=post.id)
                }
            },
            "message": "Post created successfully",
            "status": "success"
        }, status=201)
    except ValidationError as e:
        return self.json({
            "error": "Validation failed",
            "details": e.errors(),
            "code": "VALIDATION_ERROR"
        }, status=422)
```

:::info[API Best Practices]
Follow RESTful conventions for status codes:
- **200**: Success (GET, PUT, PATCH)
- **201**: Created (POST)
- **204**: No Content (DELETE)
- **400**: Bad Request (invalid data)
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **422**: Unprocessable Entity (validation errors)
- **500**: Internal Server Error
:::

### 3. URL Generation - `generate_url(route_name: str, **params)`

Generates type-safe URLs for named routes with parameter substitution. Essential for maintaining URL consistency and enabling easy route changes.

**Method Signature:**
```python
def generate_url(self, route_name: str, **params) -> str
```

**Parameters:**
- `route_name` (str): The unique name of the route
- `**params`: Named parameters to substitute in the URL pattern

**Basic URL Generation:**
```python
@Route("/users/{id}/edit", "user.edit", methods=["GET"])
async def edit(self, id: int):
    user = await self.user_service.get_by_id(id)
    
    # Generate URLs for navigation
    profile_url = self.generate_url("user.show", id=user.id)
    index_url = self.generate_url("user.index")
    delete_url = self.generate_url("user.delete", id=user.id)
    
    return self.render("users/edit.html", {
        "user": user,
        "navigation": {
            "profile": profile_url,
            "index": index_url,
            "delete": delete_url
        }
    })
```

**Complex URL Generation with Multiple Parameters:**
```python
@Route("/users/{user_id}/posts/{post_id}/comments", "user.post.comments", methods=["GET"])
async def show_comments(self, user_id: int, post_id: int):
    # Generate related URLs
    post_url = self.generate_url("user.post.show", user_id=user_id, post_id=post_id)
    user_profile = self.generate_url("user.show", id=user_id)
    create_comment_url = self.generate_url("user.post.comment.create", 
                                         user_id=user_id, post_id=post_id)
    
    return self.render("comments/index.html", {
        "post_url": post_url,
        "user_profile": user_profile,
        "create_comment_url": create_comment_url
    })
```

:::danger[URL Generation Errors]
Common mistakes to avoid:
```python
# ❌ Wrong: Missing required parameters
self.generate_url("user.show")  # Error: 'id' parameter required

# ❌ Wrong: Invalid route name
self.generate_url("user.nonexistent")  # Error: Route not found

# ✅ Correct: All parameters provided
self.generate_url("user.show", id=123)

# ✅ Correct: Handle optional parameters
url = self.generate_url("search.results", q="python", page=1)
```
:::

### 4. HTTP Redirects - `redirect(location: str, code: int = 302)`

Performs HTTP redirects with proper status codes. Essential for form processing, authentication flows, and navigation.

**Method Signature:**
```python
def redirect(self, location: str, code: int = 302) -> RedirectResponse
```

**Parameters:**
- `location` (str): The URL to redirect to
- `code` (int): HTTP status code (default: 302 - Temporary Redirect)

**Common Redirect Patterns:**
```python
@Route("/users", "user.create", methods=["POST"])
async def create(self, request: Request):
    try:
        form_data = await request.form()
        user = await self.user_service.create(form_data)
        
        # Success: redirect to user profile
        self.flash("success", f"User {user.name} created successfully!")
        return self.redirect(self.generate_url("user.show", id=user.id))
        
    except ValidationError as e:
        # Error: redirect back to form
        self.flash("error", "Please correct the errors below")
        return self.redirect(self.generate_url("user.new"))
```

**Different Redirect Types:**
```python
# Temporary redirect (302) - default
return self.redirect(self.generate_url("user.index"))

# Permanent redirect (301) - for moved resources
return self.redirect(self.generate_url("new.location"), code=301)

# See Other (303) - after POST requests
return self.redirect(self.generate_url("user.show", id=user.id), code=303)

# Temporary redirect (307) - preserves request method
return self.redirect(self.generate_url("user.process"), code=307)
```

**Authentication Redirects:**
```python
@Route("/admin/dashboard", "admin.dashboard", methods=["GET"])
async def admin_dashboard(self):
    user = self.get_user()
    if not user or not user.is_admin:
        self.flash("error", "Admin access required")
        return self.redirect(self.generate_url("auth.login"))
    
    return self.render("admin/dashboard.html")
```

### 5. Flash Messaging - `flash(category: str, message: str)`

Provides session-based messaging for user feedback across requests. Messages persist across redirects and are automatically cleared after display.

**Method Signature:**
```python
def flash(self, category: str, message: str) -> None
```

**Parameters:**
- `category` (str): Message type (success, error, warning, info)
- `message` (str): The message content

**Standard Flash Categories:**
```python
# Success messages
self.flash("success", "User updated successfully!")

# Error messages  
self.flash("error", "Failed to delete user. Please try again.")

# Warning messages
self.flash("warning", "This action cannot be undone.")

# Informational messages
self.flash("info", "Your session will expire in 5 minutes.")
```

**Comprehensive Form Processing Example:**
```python
@Route("/users/{id}", "user.update", methods=["POST"])
async def update(self, id: int, request: Request):
    try:
        user = await self.user_service.get_by_id(id)
        if not user:
            self.flash("error", "User not found")
            return self.redirect(self.generate_url("user.index"))
        
        form_data = await request.form()
        
        # Validate email uniqueness
        if form_data.get("email") != user.email:
            if await self.user_service.email_exists(form_data.get("email")):
                self.flash("error", "Email address already in use")
                return self.redirect(self.generate_url("user.edit", id=id))
        
        # Update user
        updated_user = await self.user_service.update(id, form_data)
        self.flash("success", f"User {updated_user.name} updated successfully!")
        
        return self.redirect(self.generate_url("user.show", id=id))
        
    except ValidationError as e:
        self.flash("error", f"Validation failed: {e.message}")
        return self.redirect(self.generate_url("user.edit", id=id))
    except Exception as e:
        self.flash("error", "An unexpected error occurred. Please try again.")
        # Log the actual error for debugging
        logger.error(f"User update failed: {str(e)}")
        return self.redirect(self.generate_url("user.edit", id=id))
```

**Template Integration:**
```html
<!-- Display flash messages in your template -->
{% if get_flashed_messages() %}
    <div class="flash-messages">
        {% for category, message in get_flashed_messages(with_categories=true) %}
            <div class="alert alert-{{ category }}">
                {{ message }}
                <button type="button" class="close">&times;</button>
            </div>
        {% endfor %}
    </div>
{% endif %}
```

:::tip[Flash Message Best Practices]
- Use consistent categories across your application
- Keep messages concise and actionable
- Provide context for error messages
- Use success messages to confirm actions
- Consider internationalization for multi-language apps
:::

```python
from src.form.user_type import UserType

@Route("/users/{id}/edit", "user.edit", methods=["GET"])
async def edit(self, id: int):
    user = await self.user_service.get_by_id(id)
    form = self.create_form(UserType, user)
    return self.render("users/edit.html", {"form": form, "user": user})
```

### User Authentication

#### `get_user(user_class=None)`
Retrieves the currently authenticated user.

```python
@Route("/profile", "user.profile", methods=["GET"])
async def profile(self):
    current_user = self.get_user()
    if not current_user:
        return self.redirect(self.generate_url("auth.login"))
    return self.render("users/profile.html", {"user": current_user})
```

### Dependency Injection

The base class provides access to the service container for dependency injection:

```python
class UserController(AbstractController):
    def __init__(self):
        # Access services through the container
        self.user_service = self._container.get_by_name("UserService")
        self.email_service = self._container.get_by_name("EmailService")
```

### Controller Structure

A well-structured controller follows these conventions:

```python
class ProductController(AbstractController):
    def __init__(self, product_service: ProductService):
        """Initialize with dependency injection."""
        self.product_service = product_service
    
    @Route("/products", "product.index", methods=["GET"])
    async def index(self, request: Request):
        """List all products with pagination."""
        page = int(request.query_params.get("page", 1))
        products = await self.product_service.get_paginated(page)
        return self.render("products/index.html", {"products": products})
    
    @Route("/products/{id}", "product.show", methods=["GET"])
    async def show(self, id: int):
        """Display a single product."""
        product = await self.product_service.get_by_id(id)
        if not product:
            return self.render("errors/404.html"), 404
        
        return self.render("products/show.html", {"product": product})
```

## Request Handling

### Accessing Request Data

Controllers provide multiple ways to access request information:

```python
@Route("/submit", "form.submit", methods=["POST"])
async def submit(self, request: Request):
    # Form data
    form_data = await request.form()
    name = form_data.get("name")
    
    # JSON data
    json_data = await request.json()
    
    # Query parameters
    search = request.query_params.get("search", "")
    
    # Headers
    auth_header = request.headers.get("authorization")
    
    # Path parameters are automatically injected
    return {"message": "Data received"}

@Route("/users/{id}/posts/{post_id}", "user.post.show", methods=["GET"])
async def show_user_post(self, id: int, post_id: int, request: Request):
    # Path parameters are automatically available
    user = await self.user_service.get_by_id(id)
    post = await self.post_service.get_by_id(post_id)
    return {"user": user, "post": post}
```

### Request Validation with Pydantic

Use Pydantic models for robust request validation:

```python
from pydantic import BaseModel, EmailStr
from typing import Optional

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
    is_active: bool = True

class UserController(AbstractController):
    @Route("/users", "user.create", methods=["POST"])
    async def create(self, user_data: CreateUserRequest):
        # user_data is automatically validated
        user = await self.user_service.create(user_data.dict())
        return {"user": user, "message": "User created successfully"}
```

## Response Types

### JSON Responses

Return dictionaries or Pydantic models for automatic JSON serialization:

```python
@Route("/api/users", "api.user.index", methods=["GET"])
async def api_index(self):
    users = await self.user_service.get_all()
    return {
        "users": users,
        "total": len(users),
        "timestamp": datetime.now().isoformat()
    }

# With status codes
@Route("/api/users", "api.user.create", methods=["POST"])
async def api_create(self, user_data: CreateUserRequest):
    user = await self.user_service.create(user_data.dict())
    return {"user": user}, 201  # Created
```

### Template Responses

Render HTML templates using the `render` method:

```python
@Route("/users", "user.index", methods=["GET"])
async def index(self, request: Request):
    page = int(request.query_params.get("page", 1))
    users = await self.user_service.get_paginated(page)
    
    return self.render("users/index.html", {
        "users": users,
        "current_page": page,
        "title": "All Users"
    })

@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):
    user = await self.user_service.get_by_id(id)
    if not user:
        return self.render("errors/404.html", {"resource": "User"}), 404
    
    return self.render("users/show.html", {
        "user": user,
        "title": f"User: {user.name}"
    })
```

### Redirects

Use the `redirect` method for HTTP redirects:

```python
@Route("/users", "user.create", methods=["POST"])
async def create(self, request: Request):
    data = await request.form()
    user = await self.user_service.create(data)
    
    # Redirect to the user's profile using generate_url
    return self.redirect(self.generate_url("user.show", id=user.id))

@Route("/login", "auth.login", methods=["POST"])
async def login(self, request: Request):
    data = await request.form()
    if await self.auth_service.authenticate(data):
        return self.redirect(self.generate_url("dashboard.index"))
    else:
        self.flash("error", "Invalid credentials")
        return self.redirect(self.generate_url("auth.login"))
```

## Dependency Injection

### Service Injection

Inject services into controllers for clean architecture:

```python
from src.services.user_service import UserService
from src.services.email_service import EmailService

class UserController(AbstractController):
    def __init__(self, user_service: UserService, email_service: EmailService):
        self.user_service = user_service
        self.email_service = email_service
    
    @Route("/users", "user.create", methods=["POST"])
    async def create(self, user_data: CreateUserRequest):
        user = await self.user_service.create(user_data.dict())
        await self.email_service.send_welcome_email(user)
        return {"user": user, "message": "User created and welcome email sent"}
```

### Configuration Injection

Access application configuration through dependency injection:

```python
from framefox.core.config.settings import Settings

class ConfigController(AbstractController):
    def __init__(self, settings: Settings):
        self.settings = settings
    
    @Route("/config", "config.show", methods=["GET"])
    async def show(self):
        if self.settings.app_env != "development":
            raise HTTPException(status_code=404)
        
        return {
            "environment": self.settings.app_env,
            "debug": self.settings.debug,
            "database_url": self.settings.database_url
        }
```

## Error Handling

### HTTP Exceptions

Handle errors gracefully with proper HTTP status codes:

```python
from fastapi import HTTPException

@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):
    try:
        user = await self.user_service.get_by_id(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user": user}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        # Log the error
        self.logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Custom Error Responses

Create custom error responses for better user experience:

```python
@Route("/users/{id}", "user.delete", methods=["DELETE"])
async def delete(self, id: int):
    try:
        await self.user_service.delete(id)
        return {"message": "User deleted successfully"}
    
    except UserNotFoundError:
        return {"error": "User not found"}, 404
    
    except UserHasDependenciesError:
        return {
            "error": "Cannot delete user with existing dependencies",
            "suggestion": "Archive the user instead"
        }, 409
```

## Middleware and Decorators

### Authentication Decorators

Protect routes with authentication decorators:

```python
from framefox.core.security.decorators import RequireAuth

class ProfileController(AbstractController):
    @Route("/profile", "profile.show", methods=["GET"])
    @RequireAuth
    async def show(self, current_user: User):
        return self.render("profile/show.html", {"user": current_user})
    
    @Route("/admin/users", "admin.user.index", methods=["GET"])
    @RequireAuth(roles=["admin"])
    async def admin_users(self, current_user: User):
        users = await self.user_service.get_all()
        return self.render("admin/users.html", {"users": users})
```

### Custom Decorators

Create custom decorators for cross-cutting concerns:

```python
from functools import wraps

def require_premium(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user or not current_user.is_premium:
            raise HTTPException(status_code=403, detail="Premium subscription required")
        return await func(self, *args, **kwargs)
    return wrapper

class PremiumController(AbstractController):
    @Route("/premium/dashboard", "premium.dashboard", methods=["GET"])
    @RequireAuth
    @require_premium
    async def dashboard(self, current_user: User):
        return self.render("premium/dashboard.html")
```

## CRUD Controllers

### Complete CRUD Implementation

Build full CRUD controllers with proper RESTful conventions:

```python
class PostController(AbstractController):
    def __init__(self, post_service: PostService):
        self.post_service = post_service
    
    # List all posts
    @Route("/posts", "post.index", methods=["GET"])
    async def index(self, request: Request):
        page = int(request.query_params.get("page", 1))
        search = request.query_params.get("search", "")
        
        posts = await self.post_service.get_paginated(page, search)
        return self.render("posts/index.html", {
            "posts": posts,
            "search": search,
            "page": page
        })
    
    # Show creation form
    @Route("/posts/create", "post.create", methods=["GET"])
    @RequireAuth
    async def create(self):
        return self.render("posts/create.html")
    
    # Store new post
    @Route("/posts", "post.store", methods=["POST"])
    @RequireAuth
    async def store(self, request: Request, current_user: User):
        data = await request.form()
        post_data = {
            "title": data.get("title"),
            "content": data.get("content"),
            "author_id": current_user.id
        }
        
        post = await self.post_service.create(post_data)
        return self.redirect(self.generate_url("post.show", id=post.id))
    
    # Show single post
    @Route("/posts/{id}", "post.show", methods=["GET"])
    async def show(self, id: int):
        post = await self.post_service.get_by_id(id)
        if not post:
            return self.render("errors/404.html"), 404
        
        return self.render("posts/show.html", {"post": post})
    
    # Show edit form
    @Route("/posts/{id}/edit", "post.edit", methods=["GET"])
    @RequireAuth
    async def edit(self, id: int, current_user: User):
        post = await self.post_service.get_by_id(id)
        if not post:
            return self.render("errors/404.html"), 404
        
        if post.author_id != current_user.id:
            return self.render("errors/403.html"), 403
        
        form = self.create_form(PostType, post)
        return self.render("posts/edit.html", {
            "form": form,
            "post": post,
            "title": f"Edit: {post.title}"
        })
    
    # Update post
    @Route("/posts/{id}", "post.update", methods=["PUT"])
    @RequireAuth
    async def update(self, id: int, request: Request, current_user: User):
        post = await self.post_service.get_by_id(id)
        if not post:
            raise HTTPException(status_code=404)
        
        if post.author_id != current_user.id:
            raise HTTPException(status_code=403)
        
        data = await request.form()
        updated_post = await self.post_service.update(id, {
            "title": data.get("title"),
            "content": data.get("content")
        })
        
        return self.redirect(self.generate_url("post.show", id=updated_post.id))
    
    # Delete post
    @Route("/posts/{id}", "post.destroy", methods=["DELETE"])
    @RequireAuth
    async def destroy(self, id: int, current_user: User):
        post = await self.post_service.get_by_id(id)
        if not post or post.author_id != current_user.id:
            raise HTTPException(status_code=404)
        
        await self.post_service.delete(id)
        return self.redirect(self.generate_url("post.index"))
```

## API Controllers

### RESTful API Design

Create dedicated API controllers for clean API endpoints:

```python
from fastapi import HTTPException
from typing import List

class PostApiController(AbstractController):
    def __init__(self, post_service: PostService):
        self.post_service = post_service
    
    @Route("/api/posts", "api.post.index", methods=["GET"])
    async def index(self, request: Request) -> dict:
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        
        posts = await self.post_service.get_paginated(page, limit)
        total = await self.post_service.count()
        
        return {
            "posts": posts,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        }
    
    @Route("/api/posts", "api.post.create", methods=["POST"])
    @RequireAuth
    async def create(self, post_data: CreatePostRequest, current_user: User):
        post = await self.post_service.create({
            **post_data.dict(),
            "author_id": current_user.id
        })
        return {"post": post}, 201
    
    @Route("/api/posts/{id}", "api.post.show", methods=["GET"])
    async def show(self, id: int):
        post = await self.post_service.get_by_id(id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"post": post}
    
    @Route("/api/posts/{id}", "api.post.update", methods=["PUT"])
    @RequireAuth
    async def update(self, id: int, post_data: UpdatePostRequest, current_user: User):
        post = await self.post_service.get_by_id(id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        updated_post = await self.post_service.update(id, post_data.dict())
        return {"post": updated_post}
    
    @Route("/api/posts/{id}", "api.post.delete", methods=["DELETE"])
    @RequireAuth
    async def delete(self, id: int, current_user: User):
        post = await self.post_service.get_by_id(id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        await self.post_service.delete(id)
        return {"message": "Post deleted successfully"}
```

## File Uploads

### Handling File Uploads

Manage file uploads securely and efficiently:

```python
from fastapi import UploadFile, File
import os
import uuid

class FileController(AbstractController):
    def __init__(self, settings: Settings):
        self.upload_dir = settings.upload_directory
        self.max_file_size = settings.max_file_size
    
    @Route("/upload", "file.upload", methods=["POST"])
    @RequireAuth
    async def upload(self, file: UploadFile = File(...), current_user: User = None):
        # Validate file size
        if file.size > self.max_file_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Save file info to database
        file_record = await self.file_service.create({
            "filename": unique_filename,
            "original_name": file.filename,
            "size": file.size,
            "content_type": file.content_type,
            "uploaded_by": current_user.id
        })
        
        return {"file": file_record, "message": "File uploaded successfully"}
```

## Testing Controllers

### Unit Testing with Mocks

```python
import pytest
from unittest.mock import AsyncMock, Mock
from src.controllers.user_controller import UserController

class TestUserController:
    @pytest.fixture
    def controller(self):
        controller = UserController()
        controller.user_service = AsyncMock()
        controller.email_service = AsyncMock()
        return controller
    
    @pytest.mark.asyncio
    async def test_show_user_success(self, controller):
        """Test successful user display."""
        # Arrange
        user_data = {"id": 1, "name": "Test User", "email": "test@example.com"}
        controller.user_service.get_by_id.return_value = user_data
        controller.render = Mock(return_value="rendered_template")
        
        # Act
        result = await controller.show(1)
        
        # Assert
        controller.user_service.get_by_id.assert_called_once_with(1)
        controller.render.assert_called_once_with(
            "users/show.html", 
            {"user": user_data}
        )
        assert result == "rendered_template"
    
    @pytest.mark.asyncio
    async def test_show_user_not_found(self, controller):
        """Test user not found handling."""
        # Arrange
        controller.user_service.get_by_id.return_value = None
        controller.flash = Mock()
        controller.redirect = Mock(return_value="redirect_response")
        controller.generate_url = Mock(return_value="/users")
        
        # Act
        result = await controller.show(999)
        
        # Assert
        controller.flash.assert_called_once_with("error", "User not found")
        controller.generate_url.assert_called_once_with("user.index")
        controller.redirect.assert_called_once_with("/users")
        assert result == "redirect_response"
```

### Integration Testing

```python
import pytest
from fastapi.testclient import TestClient
from main import app

class TestUserControllerIntegration:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_user_index_page(self, client):
        """Test user index page loads correctly."""
        response = client.get("/users")
        assert response.status_code == 200
        assert "Users" in response.text
    
    def test_user_creation_flow(self, client):
        """Test complete user creation flow."""
        # Get creation form
        response = client.get("/users/create")
        assert response.status_code == 200
        
        # Submit form data
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "secure_password"
        }
        response = client.post("/users", data=user_data)
        
        # Should redirect to user profile
        assert response.status_code == 302
        assert "/users/" in response.headers["location"]
```

:::info[Testing Strategy]
Implement comprehensive testing:
- **Unit Tests**: Test individual controller methods with mocked dependencies
- **Integration Tests**: Test complete request/response cycles
- **Functional Tests**: Test user workflows end-to-end
- **Security Tests**: Verify authentication and authorization
- **Performance Tests**: Ensure controllers handle load appropriately
:::

This completes the comprehensive documentation of Framefox controllers with detailed explanations, verbose examples, and helpful information boxes throughout.
