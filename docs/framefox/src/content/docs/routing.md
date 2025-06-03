---
title: Routing System
description: Complete guide to the routing system in Framefox
---

# Routing System

Framefox's routing system provides an elegant and powerful way to define how your application responds to different HTTP requests. Built on top of FastAPI, it offers exceptional flexibility while maintaining clean, readable syntax that makes route definition intuitive and maintainable.

The routing system is the backbone of your web application, determining which controller methods handle specific URL patterns and HTTP methods. Whether you're building a simple website or a complex API, Framefox's routing capabilities scale with your needs.

:::info[FastAPI Integration]
Framefox routing leverages FastAPI's robust routing engine, providing:
- High-performance request handling
- Automatic OpenAPI documentation generation
- Built-in request validation and serialization
- WebSocket support and async/await compatibility
- Industry-standard HTTP compliance
:::

:::tip[Performance Benefits]
The routing system is optimized for production use:
- **Fast Route Matching**: O(1) lookup time for most routes
- **Automatic Caching**: Route patterns are compiled and cached
- **Memory Efficient**: Minimal overhead per route definition
- **Concurrent Safe**: Thread-safe route resolution
:::

## The @Route Decorator

The `@Route` decorator is the primary way to define routes in Framefox. It transforms regular controller methods into HTTP endpoints, automatically handling request routing, parameter extraction, and response formatting.

```python
from framefox.core.routing.decorator.route import Route

@Route(path="/users", name="user.index", methods=["GET"])
async def index(self):
    return {"users": []}
```

This simple decorator call creates a complete HTTP endpoint that responds to GET requests at the `/users` path, with the unique identifier `user.index` for URL generation and reference.

### Decorator Parameters Deep Dive

Understanding each parameter helps you create more precise and maintainable routes:

- **path** (str, required): The URL pattern that triggers this route
  - Static paths: `/users`, `/about`, `/api/health`
  - Dynamic paths: `/users/{id}`, `/posts/{slug}/comments/{comment_id}`
  - Wildcard paths: `/files/{filepath:path}` (captures remaining path segments)

- **name** (str, required): A unique identifier for the route
  - Used for URL generation: `generate_url("user.index")`
  - Enables reverse routing and refactoring safety
  - Convention: `{resource}.{action}` (e.g., `user.show`, `post.create`)

- **methods** (list, optional): HTTP methods this route accepts
  - Defaults to `["GET"]` if not specified
  - Common values: `["GET"]`, `["POST"]`, `["PUT", "PATCH"]`, `["DELETE"]`
  - Multiple methods: `["GET", "POST"]` for form handling

:::warning[Route Name Uniqueness]
Route names must be unique across your entire application:
```python
# ❌ Conflict: Same name used twice
@Route("/users", "user.index", methods=["GET"])
@Route("/api/users", "user.index", methods=["GET"])  # Error!

# ✅ Correct: Different names
@Route("/users", "user.index", methods=["GET"])
@Route("/api/users", "api.user.index", methods=["GET"])
```
:::

## Route Types & Patterns

### Static Routes

Static routes handle fixed URL patterns without any dynamic parameters. They're perfect for pages like home, about, contact, or any content that doesn't require URL parameters.

```python
@Route("/", "home.index", methods=["GET"])
async def home(self):
    """Homepage - most visited route."""
    return self.render("home.html", {
        "featured_posts": await self.post_service.get_featured(),
        "site_stats": await self.analytics_service.get_public_stats()
    })

@Route("/about", "about.page", methods=["GET"])
async def about(self):
    """About page with company information."""
    return self.render("about.html", {
        "team_members": await self.team_service.get_public_members(),
        "company_history": await self.content_service.get_about_content()
    })

@Route("/contact", "contact.page", methods=["GET"])
async def contact(self):
    """Contact page with form."""
    return self.render("contact.html", {
        "contact_form": self.create_form(ContactType, Contact()),
        "office_locations": await self.location_service.get_offices()
    })

# API health check endpoint
@Route("/health", "health.check", methods=["GET"])
async def health_check(self):
    """System health check for monitoring."""
    return self.json({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "database": await self.db_service.check_connection(),
        "redis": await self.cache_service.check_connection()
    })
```

:::tip[Static Route Best Practices]
- Keep static routes simple and focused
- Use descriptive route names for maintenance
- Include SEO-friendly meta information in templates
- Consider caching for frequently accessed static content
- Add proper HTTP headers for static assets
:::

### Parameterized Routes

Parameterized routes capture dynamic segments from the URL and pass them as arguments to your controller methods. This enables you to build flexible, data-driven applications that can handle variable content based on URL parameters.

:::info[Parameter Extraction]
Framefox automatically extracts URL parameters and converts them to the appropriate Python types based on your method signature. This provides type safety and eliminates manual parsing.
:::

**Single Parameter Routes:**
```python
@Route("/users/{id}", "user.show", methods=["GET"])
async def show_user(self, id: int):
    """Display a specific user by ID."""
    try:
        user = await self.user_service.get_by_id(id)
        if not user:
            return self.json({"error": "User not found"}, status=404)
        
        return self.render("users/show.html", {
            "user": user,
            "edit_url": self.generate_url("user.edit", id=user.id),
            "delete_url": self.generate_url("user.delete", id=user.id)
        })
    except ValueError:
        # Invalid ID format
        self.flash("error", "Invalid user ID")
        return self.redirect(self.generate_url("user.index"))

@Route("/posts/{slug}", "post.show", methods=["GET"])
async def show_post(self, slug: str):
    """Display a post by URL slug."""
    post = await self.post_service.get_by_slug(slug)
    if not post:
        return self.json({"error": "Post not found"}, status=404)
    
    # Track view count
    await self.analytics_service.track_post_view(post.id)
    
    return self.render("posts/show.html", {
        "post": post,
        "related_posts": await self.post_service.get_related(post),
        "comments": await self.comment_service.get_by_post(post.id)
    })
```

**Multiple Parameter Routes:**
```python
@Route("/users/{user_id}/posts/{post_id}", "user.post.show", methods=["GET"])
async def show_user_post(self, user_id: int, post_id: int):
    """Display a specific post by a specific user."""
    # Verify user exists
    user = await self.user_service.get_by_id(user_id)
    if not user:
        return self.json({"error": "User not found"}, status=404)
    
    # Verify post exists and belongs to user
    post = await self.post_service.get_by_id_and_user(post_id, user_id)
    if not post:
        return self.json({"error": "Post not found or doesn't belong to user"}, status=404)
    
    return self.render("posts/user_post.html", {
        "user": user,
        "post": post,
        "breadcrumb": [
            {"title": "Users", "url": self.generate_url("user.index")},
            {"title": user.name, "url": self.generate_url("user.show", id=user.id)},
            {"title": "Posts", "url": self.generate_url("user.posts", user_id=user.id)},
            {"title": post.title, "url": None}
        ]
    })

@Route("/api/v1/categories/{category}/posts/{post_id}/comments/{comment_id}", 
       "api.comment.show", methods=["GET"])
async def show_nested_comment(self, category: str, post_id: int, comment_id: int):
    """API endpoint for deeply nested resource access."""
    # Validate the entire hierarchy
    post = await self.post_service.get_by_id_and_category(post_id, category)
    if not post:
        return self.json({"error": "Post not found in category"}, status=404)
    
    comment = await self.comment_service.get_by_id_and_post(comment_id, post_id)
    if not comment:
        return self.json({"error": "Comment not found"}, status=404)
    
    return self.json({
        "comment": comment.to_dict(),
        "post": {"id": post.id, "title": post.title},
        "category": category,
        "links": {
            "post": self.generate_url("api.post.show", category=category, post_id=post_id),
            "all_comments": self.generate_url("api.post.comments", category=category, post_id=post_id)
        }
    })
```

**Optional Parameters with Defaults:**
```python
@Route("/posts", "post.index", methods=["GET"])
@Route("/posts/{category}", "post.by_category", methods=["GET"])
async def posts_by_category(self, category: str = "general"):
    """Display posts, optionally filtered by category."""
    # Handle both /posts and /posts/technology URLs
    posts = await self.post_service.get_by_category(category)
    categories = await self.category_service.get_all()
    
    return self.render("posts/index.html", {
        "posts": posts,
        "current_category": category,
        "categories": categories,
        "title": f"Posts in {category.title()}" if category != "general" else "All Posts"
    })

@Route("/search", "search.results", methods=["GET"])
async def search(self, q: str = "", page: int = 1, per_page: int = 10):
    """Search with optional pagination parameters."""
    if not q:
        return self.render("search/form.html", {
            "query": "",
            "message": "Enter a search term to begin"
        })
    
    # Validate pagination parameters
    page = max(1, page)
    per_page = min(100, max(1, per_page))  # Limit to prevent abuse
    
    results = await self.search_service.search(
        query=q,
        page=page,
        per_page=per_page
    )
    
    return self.render("search/results.html", {
        "query": q,
        "results": results,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": results.total,
            "has_next": results.has_next,
            "has_prev": results.has_prev
        }
    })
```

:::warning[Parameter Validation]
Always validate URL parameters in your controller methods:
```python
@Route("/users/{id}", "user.show", methods=["GET"])
async def show_user(self, id: int):
    # ❌ Dangerous: No validation
    user = await self.user_service.get_by_id(id)
    
    # ✅ Better: Validate range
    if id <= 0:
        return self.json({"error": "Invalid user ID"}, status=400)
    
    # ✅ Best: Use service layer validation
    try:
        user = await self.user_service.get_by_id(id)
    except InvalidIdError:
        return self.json({"error": "Invalid user ID"}, status=400)
```
:::

### Type-Constrained Routes & Advanced Patterns

Framefox leverages FastAPI's powerful type system to provide automatic parameter validation and conversion. This ensures that only valid data types can match routes and provides cleaner error handling.

**Supported Type Constraints:**
```python
# Integer constraints
@Route("/users/{id:int}", "user.show", methods=["GET"])
async def show_user(self, id: int):
    """Only matches numeric IDs: /users/123 ✅, /users/abc ❌"""
    pass

# String constraints (default)
@Route("/posts/{slug:str}", "post.show", methods=["GET"])
async def show_post(self, slug: str):
    """Matches any string: /posts/my-blog-post ✅"""
    pass

# Path constraints (captures remaining path)
@Route("/files/{filepath:path}", "file.serve", methods=["GET"])
async def serve_file(self, filepath: str):
    """Matches entire remaining path: /files/docs/guide.pdf ✅"""
    # filepath would be "docs/guide.pdf"
    return await self.file_service.serve_file(filepath)

# Float constraints
@Route("/api/coordinates/{lat:float}/{lng:float}", "api.location", methods=["GET"])
async def get_location(self, lat: float, lng: float):
    """Matches decimal coordinates: /api/coordinates/40.7128/-74.0060 ✅"""
    location_data = await self.geo_service.get_location_info(lat, lng)
    return self.json({"location": location_data})
```

**Advanced Path Patterns:**
```python
# UUID constraints for secure resource access
from uuid import UUID

@Route("/api/resources/{resource_uuid:uuid}", "api.resource.show", methods=["GET"])
async def show_resource(self, resource_uuid: UUID):
    """Only matches valid UUIDs: prevents ID enumeration attacks."""
    resource = await self.resource_service.get_by_uuid(resource_uuid)
    if not resource:
        return self.json({"error": "Resource not found"}, status=404)
    return self.json({"resource": resource.to_dict()})

# Regular expression constraints
@Route("/posts/{year:int}/{month:int}/{day:int}/{slug}", "post.by_date", methods=["GET"])
async def show_post_by_date(self, year: int, month: int, day: int, slug: str):
    """Date-based blog post URLs: /posts/2024/03/15/my-blog-post"""
    # Validate date
    try:
        post_date = datetime(year, month, day)
    except ValueError:
        return self.json({"error": "Invalid date"}, status=400)
    
    post = await self.post_service.get_by_date_and_slug(post_date, slug)
    if not post:
        return self.json({"error": "Post not found"}, status=404)
    
    return self.render("posts/show.html", {
        "post": post,
        "canonical_url": self.generate_url("post.by_date", 
                                         year=year, month=month, day=day, slug=slug)
    })

# Multiple format support
@Route("/api/data/{format:str}", "api.data.export", methods=["GET"])
async def export_data(self, format: str):
    """Support multiple export formats with validation."""
    allowed_formats = ["json", "csv", "xml", "xlsx"]
    
    if format not in allowed_formats:
        return self.json({
            "error": f"Unsupported format. Allowed: {', '.join(allowed_formats)}"
        }, status=400)
    
    data = await self.data_service.get_export_data()
    
    if format == "json":
        return self.json({"data": data})
    elif format == "csv":
        csv_content = await self.export_service.to_csv(data)
        return Response(content=csv_content, media_type="text/csv")
    elif format == "xml":
        xml_content = await self.export_service.to_xml(data)
        return Response(content=xml_content, media_type="application/xml")
    elif format == "xlsx":
        xlsx_content = await self.export_service.to_xlsx(data)
        return Response(content=xlsx_content, 
                       media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
```

:::tip[Type Safety Benefits]
Using type constraints provides several advantages:
- **Automatic Validation**: Invalid types return 422 errors automatically
- **IDE Support**: Better autocomplete and error detection
- **Documentation**: Self-documenting API with clear parameter types
- **Security**: Prevents injection attacks through type validation
- **Performance**: Faster route matching with type hints
:::

:::danger[Common Type Pitfalls]
Avoid these common mistakes with route parameters:
```python
# ❌ Wrong: Mismatch between route and method signature
@Route("/users/{id:str}", "user.show", methods=["GET"])
async def show_user(self, id: int):  # Expects int but route provides str
    pass

# ❌ Wrong: Missing parameter in method signature
@Route("/users/{id}/posts/{post_id}", "user.post.show", methods=["GET"])
async def show_user_post(self, id: int):  # Missing post_id parameter
    pass

# ✅ Correct: Types match between route and method
@Route("/users/{id:int}", "user.show", methods=["GET"])
async def show_user(self, id: int):
    pass
```
:::

```python
# Integer constraint
@Route("/users/{id:int}", "user.show", methods=["GET"])
async def show_user(self, id: int):
    # id is guaranteed to be an integer
    return {"user_id": id}

# String constraint
@Route("/posts/{slug:str}", "post.show", methods=["GET"])
async def show_post(self, slug: str):
    # slug is guaranteed to be a string
    return {"post_slug": slug}

# Path constraint (captures slashes)
@Route("/files/{filepath:path}", "file.serve", methods=["GET"])
async def serve_file(self, filepath: str):
    # filepath can contain slashes
    return {"filepath": filepath}
```

## HTTP Methods

### Standard HTTP Methods

Framefox supports all standard HTTP methods, allowing you to build RESTful APIs and web applications that follow HTTP conventions.

```python
# GET - Retrieve data
@Route("/users", "user.index", methods=["GET"])
async def get_users(self):
    return {"users": []}

# POST - Create new data
@Route("/users", "user.create", methods=["POST"])
async def create_user(self, request: Request):
    data = await request.json()
    return {"created": True}

# PUT - Complete update
@Route("/users/{id}", "user.update", methods=["PUT"])
async def update_user(self, id: int, request: Request):
    return {"updated": True}

# PATCH - Partial update
@Route("/users/{id}", "user.patch", methods=["PATCH"])
async def patch_user(self, id: int, request: Request):
    return {"patched": True}

# DELETE - Remove data
@Route("/users/{id}", "user.delete", methods=["DELETE"])
async def delete_user(self, id: int):
    return {"deleted": True}
```

### Multiple Methods

A single method can handle multiple HTTP verbs, useful for form handling or creating flexible endpoints:

```python
@Route("/contact", "contact.form", methods=["GET", "POST"])
async def contact(self, request: Request):
    if request.method == "GET":
        return self.render("contact/form.html")
    elif request.method == "POST":
        # Process the form submission
        return self.redirect("contact.success")
```

## Route Naming

### Naming Conventions

Consistent route naming makes your application more maintainable and enables powerful features like URL generation and reverse routing:

```python
# Format: resource.action
@Route("/users", "user.index", methods=["GET"])          # List all
@Route("/users/create", "user.create", methods=["GET"])  # Creation form
@Route("/users", "user.store", methods=["POST"])         # Store new
@Route("/users/{id}", "user.show", methods=["GET"])      # Show single
@Route("/users/{id}/edit", "user.edit", methods=["GET"]) # Edit form
@Route("/users/{id}", "user.update", methods=["PUT"])    # Update
@Route("/users/{id}", "user.delete", methods=["DELETE"]) # Delete
```

### Grouped Routes

For APIs or modular applications, use prefixed naming to organize routes logically:

```python
# API routes
@Route("/api/users", "api.user.index", methods=["GET"])
@Route("/api/users/{id}", "api.user.show", methods=["GET"])

# Admin routes
@Route("/admin/users", "admin.user.index", methods=["GET"])
@Route("/admin/users/{id}", "admin.user.show", methods=["GET"])

# Versioned API
@Route("/api/v1/posts", "api.v1.post.index", methods=["GET"])
@Route("/api/v2/posts", "api.v2.post.index", methods=["GET"])
```

## URL Generation

### In Controllers

Generate URLs dynamically in your controller methods for redirects and responses:

```python
# Redirect to a named route
return self.redirect(self.generate_url("user.show", id=123))

# Generate URL for templates or responses
url = self.generate_url("user.edit", id=user.id)
profile_url = self.generate_url("user.profile", username=user.username)
```

### In Templates

Use the `url_for` function in your templates to generate type-safe URLs:

```html
<!-- Simple link -->
<a href="{{ url_for('user.index') }}">All Users</a>

<!-- Link with parameters -->
<a href="{{ url_for('user.show', id=user.id) }}">View {{ user.name }}</a>

<!-- Link with multiple parameters -->
<a href="{{ url_for('user.post.show', user_id=user.id, post_id=post.id) }}">
    View Post
</a>

<!-- External links with query parameters -->
<a href="{{ url_for('search.results', q='python', category='programming') }}">
    Python Programming
</a>
```

## Query Parameters

### Accessing Query Parameters

Query parameters provide additional data to your routes without affecting the URL structure:

```python
from fastapi import Request

@Route("/search", "search.index", methods=["GET"])
async def search(self, request: Request):
    query = request.query_params.get("q", "")
    page = int(request.query_params.get("page", 1))
    per_page = int(request.query_params.get("per_page", 10))
    
    return {
        "query": query,
        "page": page,
        "per_page": per_page,
        "results": []
    }
```

### Using Pydantic Models

For better validation and type safety, use Pydantic models to handle query parameters:

```python
from pydantic import BaseModel
from typing import Optional

class SearchQuery(BaseModel):
    q: str = ""
    page: int = 1
    per_page: int = 10
    sort: Optional[str] = None
    order: str = "asc"

@Route("/search", "search.index", methods=["GET"])
async def search(self, query: SearchQuery):
    return {
        "query": query.q,
        "page": query.page,
        "per_page": query.per_page,
        "sort": query.sort,
        "order": query.order,
        "results": []
    }
```

## Route Organization

### Modular Controllers

Organize routes by functionality using separate controller classes:

```python
# src/controllers/api/user_controller.py
class UserApiController(AbstractController):
    @Route("/api/v1/users", "api.v1.user.index", methods=["GET"])
    async def index(self):
        return {"users": []}
    
    @Route("/api/v1/users/{id}", "api.v1.user.show", methods=["GET"])
    async def show(self, id: int):
        return {"user": {}}

# src/controllers/web/user_controller.py
class UserWebController(AbstractController):
    @Route("/users", "user.index", methods=["GET"])
    async def index(self):
        return self.render("users/index.html")
    
    @Route("/users/{id}", "user.show", methods=["GET"])
    async def show(self, id: int):
        return self.render("users/show.html", {"user_id": id})
```

### Route Prefixes

Reduce repetition by using class constants for common prefixes:

```python
class UserApiController(AbstractController):
    BASE_ROUTE = "/api/v1/users"
    
    @Route(f"{BASE_ROUTE}", "api.v1.user.index", methods=["GET"])
    async def index(self):
        return {"users": []}
    
    @Route(f"{BASE_ROUTE}/{{id}}", "api.v1.user.show", methods=["GET"])
    async def show(self, id: int):
        return {"user": {}}
    
    @Route(f"{BASE_ROUTE}/{{id}}/posts", "api.v1.user.posts", methods=["GET"])
    async def user_posts(self, id: int):
        return {"posts": []}
```

## Advanced Routing

### Conditional Routes

Create routes that are only available under certain conditions:

```python
from framefox.core.config.settings import Settings

class DebugController(AbstractController):
    def __init__(self, settings: Settings):
        self.settings = settings
    
    @Route("/debug/info", "debug.info", methods=["GET"])
    async def debug_info(self):
        if self.settings.app_env != "development":
            raise HTTPException(status_code=404)
        return {"debug": "info", "environment": self.settings.app_env}
```

### Fallback Routes

Handle unmatched routes gracefully with catch-all patterns:

```python
@Route("/{path:path}", "fallback", methods=["GET"])
async def fallback(self, path: str):
    # Handle all undefined routes
    return self.render("errors/404.html", {"path": path}), 404
```

### Route Middleware

Apply middleware to specific routes for authentication, validation, or other cross-cutting concerns:

```python
from framefox.core.security.decorators import RequireAuth

@Route("/profile", "user.profile", methods=["GET"])
@RequireAuth
async def profile(self):
    return self.render("user/profile.html")

@Route("/admin/dashboard", "admin.dashboard", methods=["GET"])
@RequireAuth(roles=["admin"])
async def admin_dashboard(self):
    return self.render("admin/dashboard.html")
```

## RESTful API Routes

### Complete REST Controller

Build a full RESTful API controller following HTTP conventions:

```python
class ProductController(AbstractController):
    # GET /products - List all products
    @Route("/products", "product.index", methods=["GET"])
    async def index(self, request: Request):
        page = int(request.query_params.get("page", 1))
        return {"products": [], "page": page}
    
    # POST /products - Create a new product
    @Route("/products", "product.store", methods=["POST"])
    async def store(self, request: Request):
        data = await request.json()
        return {"created": True, "product": data}
    
    # GET /products/{id} - Show a single product
    @Route("/products/{id}", "product.show", methods=["GET"])
    async def show(self, id: int):
        return {"product": {"id": id}}
    
    # PUT /products/{id} - Update a product completely
    @Route("/products/{id}", "product.update", methods=["PUT"])
    async def update(self, id: int, request: Request):
        data = await request.json()
        return {"updated": True, "product": data}
    
    # PATCH /products/{id} - Partially update a product
    @Route("/products/{id}", "product.patch", methods=["PATCH"])
    async def patch(self, id: int, request: Request):
        data = await request.json()
        return {"patched": True, "changes": data}
    
    # DELETE /products/{id} - Delete a product
    @Route("/products/{id}", "product.destroy", methods=["DELETE"])
    async def destroy(self, id: int):
        return {"deleted": True, "product_id": id}
```

## Debugging and Development

### Route Inspection

List all registered routes in your application for debugging:

```bash
framefox debug router
```

This command displays:
- Route path patterns
- Route names
- Accepted HTTP methods
- Associated controller and method names
- Parameter constraints

### Web Profiler

In development mode, access the web profiler at `/_profiler` to see:
- All matched routes for each request
- Route matching performance
- Parameter values and types
- Response times and status codes

## Best Practices

### 1. Consistent Naming

Use a consistent naming convention across your application:

```python
# ✅ Good - Consistent resource.action pattern
@Route("/users", "user.index", methods=["GET"])
@Route("/users/{id}", "user.show", methods=["GET"])
@Route("/posts", "post.index", methods=["GET"])
@Route("/posts/{id}", "post.show", methods=["GET"])

# ❌ Bad - Inconsistent naming
@Route("/users", "list_users", methods=["GET"])
@Route("/users/{id}", "show_user_detail", methods=["GET"])
@Route("/posts", "all_posts", methods=["GET"])
@Route("/posts/{id}", "post_details", methods=["GET"])
```

### 2. Logical Controller Organization

Group related routes in the same controller:

```python
# ✅ Good - Related functionality grouped
class UserController(AbstractController):
    # All user-related routes here
    pass

class PostController(AbstractController):
    # All post-related routes here
    pass

# ❌ Bad - Mixed functionality
class MixedController(AbstractController):
    # User routes mixed with post routes
    pass
```

### 3. Parameter Validation

Always use type hints for automatic validation:

```python
# ✅ Good - Type validation
@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):  # FastAPI validates automatically
    pass

# ❌ Bad - No validation
@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id):  # Any value accepted
    pass
```

### 4. Error Handling

Implement proper error handling for missing resources:

```python
from fastapi import HTTPException

@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):
    user = self.user_service.find(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user}
```

### 5. Documentation

Document your routes clearly, especially for APIs:

```python
@Route("/users/{id}", "user.show", methods=["GET"])
async def show(self, id: int):
    """
    Retrieve a specific user by ID.
    
    Args:
        id: The unique identifier for the user
        
    Returns:
        User data object or 404 if not found
        
    Raises:
        HTTPException: When user is not found
    """
    pass
```

The routing system in Framefox provides the flexibility of FastAPI with the convenience of a high-level framework. By following these patterns and best practices, you can build maintainable, scalable web applications with clean, expressive routing.
