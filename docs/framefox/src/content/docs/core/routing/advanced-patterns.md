---
title: Advanced Routing Patterns
description: Learn advanced routing techniques, middleware integration, and complex URL patterns in Framefox.
---


This guide covers advanced routing techniques for complex applications, including middleware integration, conditional routes, and sophisticated URL patterns.

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

## Complex URL Patterns

### UUID Routes for Security

Use UUID constraints to prevent ID enumeration attacks:

```python
from uuid import UUID

@Route("/api/resources/{resource_uuid:uuid}", "api.resource.show", methods=["GET"])
async def show_resource(self, resource_uuid: UUID):
    """Only matches valid UUIDs: prevents ID enumeration attacks."""
    resource = await self.resource_service.get_by_uuid(resource_uuid)
    if not resource:
        return self.json({"error": "Resource not found"}, status=404)
    return self.json({"resource": resource.to_dict()})
```

### Date-Based URLs

Create SEO-friendly date-based blog URLs:

```python
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
```

### Multi-Format Endpoints

Support multiple output formats in a single route:

```python
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

## Geographic and Coordinate Routes

Handle geographic data with precise routing patterns:

```python
@Route("/api/coordinates/{lat:float}/{lng:float}", "api.location", methods=["GET"])
async def get_location(self, lat: float, lng: float):
    """Matches decimal coordinates: /api/coordinates/40.7128/-74.0060"""
    # Validate coordinate ranges
    if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
        return self.json({"error": "Invalid coordinates"}, status=400)
    
    location_data = await self.geo_service.get_location_info(lat, lng)
    return self.json({"location": location_data})

@Route("/api/places/{country}/{state}/{city}", "api.place.show", methods=["GET"])
async def show_place(self, country: str, state: str, city: str):
    """Hierarchical geographic routing"""
    place = await self.place_service.find_by_hierarchy(country, state, city)
    if not place:
        return self.json({"error": "Place not found"}, status=404)
    
    return self.json({
        "place": place.to_dict(),
        "weather": await self.weather_service.get_current(place.coordinates),
        "timezone": place.timezone
    })
```

## File Serving with Path Constraints

Securely serve files using path constraints:

```python
@Route("/files/{filepath:path}", "file.serve", methods=["GET"])
async def serve_file(self, filepath: str):
    """Securely serve files with path validation"""
    # Security: Prevent directory traversal
    if '..' in filepath or filepath.startswith('/'):
        return self.json({"error": "Invalid file path"}, status=400)
    
    # Validate file exists and is allowed
    full_path = await self.file_service.get_safe_path(filepath)
    if not full_path:
        return self.json({"error": "File not found"}, status=404)
    
    return await self.file_service.serve_file(full_path)
```

## Best Practices for Advanced Routes

### 1. Security Considerations

Always validate and sanitize route parameters:

```python
# ✅ Good - Proper validation
@Route("/api/users/{id:int}", "api.user.show", methods=["GET"])
async def show_user(self, id: int):
    if id <= 0:
        return self.json({"error": "Invalid user ID"}, status=400)
    # Continue with logic...

# ❌ Bad - No validation
@Route("/api/users/{id}", "api.user.show", methods=["GET"])
async def show_user(self, id):
    # Direct use without validation
    user = await self.user_service.get_by_id(id)
```

### 2. Performance Optimization

Use appropriate HTTP methods and caching strategies:

```python
@Route("/api/users/{id}", "api.user.show", methods=["GET"])
async def show_user(self, id: int):
    # Add caching headers for GET requests
    response = await self.get_user_response(id)
    response.headers["Cache-Control"] = "public, max-age=300"
    return response
```

### 3. Error Handling

Implement comprehensive error handling:

```python
@Route("/api/complex/{param1}/{param2:int}", "api.complex", methods=["GET"])
async def complex_route(self, param1: str, param2: int):
    try:
        # Complex business logic
        result = await self.complex_service.process(param1, param2)
        return self.json({"result": result})
    except ValidationError as e:
        return self.json({"error": "Validation failed", "details": str(e)}, status=422)
    except NotFoundError:
        return self.json({"error": "Resource not found"}, status=404)
    except Exception as e:
        logger.error(f"Unexpected error in complex_route: {e}")
        return self.json({"error": "Internal server error"}, status=500)
```


