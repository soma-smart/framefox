---
title: RESTful API Routes
description: Learn how to build complete RESTful APIs with CRUD operations and proper HTTP conventions in Framefox.
---


This guide covers building complete RESTful APIs following HTTP conventions and industry standards for modern web applications.

## RESTful Principles

RESTful APIs follow established conventions for resource management:
- **Resources** are represented by URLs (e.g., `/users`, `/posts`)
- **HTTP methods** define actions (GET, POST, PUT, PATCH, DELETE)
- **Status codes** indicate operation results (200, 201, 404, 500)
- **Consistent responses** provide predictable data structures

## Complete REST Controller

Build a full RESTful API controller following HTTP conventions:

```bash
framefox create crud
```

```python
class UserController(AbstractController):
    def __init__(self, entityManager: EntityManagerInterface):
        self.entity_manager = entityManager
        self.repository = UserRepository()

    # GET /users - List all users
    @Route("/users", "user.index", methods=["GET"])
    async def index(self):
        """GET /users - Retrieve all user resources"""
        try:
            items = self.repository.find_all()
            return self.json({
                "users": [item.dict() for item in items],
                "total": len(items),
                "status": "success"
            }, status=200)
        except Exception as e:
            return self.json({
                "error": "Failed to retrieve users",
                "message": str(e),
                "status": "error"
            }, status=500)

    # GET /users/{id} - Show a single user
    @Route("/users/{id}", "user.show", methods=["GET"])
    async def show(self, id: int):
        """GET /users/{id} - Retrieve a specific user resource"""
        try:
            item = self.repository.find(id)
            if not item:
                return self.json({
                    "error": "User not found",
                    "status": "not_found"
                }, status=404)

            return self.json({
                "user": item.dict(),
                "status": "success"
            }, status=200)
        except Exception as e:
            return self.json({
                "error": "Failed to retrieve user",
                "message": str(e),
                "status": "error"
            }, status=500)

    # POST /users - Create a new user
    @Route("/users", "user.create", methods=["POST"])
    async def create(self, data: User.generate_create_model()):
        """POST /users - Create a new user resource"""
        try:
            user = self.repository.model(**data.dict())
            self.entity_manager.persist(user)
            self.entity_manager.commit()
            self.entity_manager.refresh(user)

            return self.json({
                "user": user.dict(),
                "message": "User created successfully",
                "status": "created"
            }, status=201)
        except Exception as e:
            return self.json({
                "error": "Failed to create user",
                "message": str(e),
                "status": "error"
            }, status=400)

    # PUT /users/{id} - Update a user completely
    @Route("/users/{id}", "user.update", methods=["PUT"])
    async def update(self, id: int, data: User.generate_create_model()):
        """PUT /users/{id} - Replace the entire user resource"""
        try:
            user = self.repository.find(id)
            if not user:
                return self.json({
                    "error": "User not found",
                    "status": "not_found"
                }, status=404)

            # Complete replacement of the resource
            update_data = data.dict()
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            self.entity_manager.persist(user)
            self.entity_manager.commit()
            self.entity_manager.refresh(user)

            return self.json({
                "user": user.dict(),
                "message": "User updated successfully",
                "status": "updated"
            }, status=200)
        except Exception as e:
            return self.json({
                "error": "Failed to update user",
                "message": str(e),
                "status": "error"
            }, status=400)

    # PATCH /users/{id} - Partially update a user
    @Route("/users/{id}", "user.patch", methods=["PATCH"])
    async def patch(self, id: int, data: User.generate_patch_model()):
        """PATCH /users/{id} - Partially update a user resource"""
        try:
            user = self.repository.find(id)
            if not user:
                return self.json({
                    "error": "User not found",
                    "status": "not_found"
                }, status=404)

            update_data = data.dict(exclude_unset=True)

            # Partial update - only modify provided fields
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            self.entity_manager.persist(user)
            self.entity_manager.commit()
            self.entity_manager.refresh(user)

            return self.json({
                "user": user.dict(),
                "message": "User partially updated successfully",
                "status": "updated"
            }, status=200)
        except Exception as e:
            return self.json({
                "error": "Failed to patch user",
                "message": str(e),
                "status": "error"
            }, status=400)

    # DELETE /users/{id} - Delete a user
    @Route("/users/{id}", "user.destroy", methods=["DELETE"])
    async def destroy(self, id: int):
        """DELETE /users/{id} - Delete a user resource"""
        try:
            user = self.repository.find(id)
            if not user:
                return self.json({
                    "error": "User not found",
                    "status": "not_found"
                }, status=404)

            self.entity_manager.delete(user)
            self.entity_manager.commit()

            return self.json({
                "message": "User deleted successfully",
                "status": "deleted"
            }, status=204)
        except Exception as e:
            return self.json({
                "error": "Failed to delete user",
                "message": str(e),
                "status": "error"
            }, status=500)
```

## HTTP Methods and Their Uses

### GET - Retrieve Resources

Use GET for safe, idempotent operations that don't modify data:

```python
# List resources with pagination
@Route("/posts", "post.index", methods=["GET"])
async def index(self, page: int = 1, per_page: int = 10):
    posts = await self.post_service.get_paginated(page, per_page)
    return self.json({
        "posts": [post.dict() for post in posts.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": posts.total,
            "pages": posts.pages
        }
    })

# Get single resource
@Route("/posts/{id}", "post.show", methods=["GET"])
async def show(self, id: int):
    post = await self.post_service.get_by_id(id)
    if not post:
        return self.json({"error": "Post not found"}, status=404)
    return self.json({"post": post.dict()})
```

### POST - Create New Resources

Use POST for creating new resources:

```python
@Route("/posts", "post.create", methods=["POST"])
async def create(self, data: PostCreateModel):
    try:
        post = await self.post_service.create(data.dict())
        return self.json({
            "post": post.dict(),
            "message": "Post created successfully"
        }, status=201)
    except ValidationError as e:
        return self.json({"error": "Validation failed", "details": e.errors()}, status=422)
```

### PUT - Complete Resource Replacement

Use PUT for complete resource updates:

```python
@Route("/posts/{id}", "post.update", methods=["PUT"])
async def update(self, id: int, data: PostUpdateModel):
    try:
        post = await self.post_service.update_complete(id, data.dict())
        if not post:
            return self.json({"error": "Post not found"}, status=404)
        return self.json({
            "post": post.dict(),
            "message": "Post updated successfully"
        })
    except ValidationError as e:
        return self.json({"error": "Validation failed", "details": e.errors()}, status=422)
```

### PATCH - Partial Resource Updates

Use PATCH for partial resource updates:

```python
@Route("/posts/{id}", "post.patch", methods=["PATCH"])
async def patch(self, id: int, data: PostPatchModel):
    try:
        post = await self.post_service.update_partial(id, data.dict(exclude_unset=True))
        if not post:
            return self.json({"error": "Post not found"}, status=404)
        return self.json({
            "post": post.dict(),
            "message": "Post updated successfully"
        })
    except ValidationError as e:
        return self.json({"error": "Validation failed", "details": e.errors()}, status=422)
```

### DELETE - Remove Resources

Use DELETE for resource removal:

```python
@Route("/posts/{id}", "post.destroy", methods=["DELETE"])
async def destroy(self, id: int):
    success = await self.post_service.delete(id)
    if not success:
        return self.json({"error": "Post not found"}, status=404)
    
    return self.json({
        "message": "Post deleted successfully"
    }, status=204)
```

## Nested Resources

Handle relationships between resources:

```python
# Get all comments for a post
@Route("/posts/{post_id}/comments", "post.comments.index", methods=["GET"])
async def post_comments(self, post_id: int):
    post = await self.post_service.get_by_id(post_id)
    if not post:
        return self.json({"error": "Post not found"}, status=404)
    
    comments = await self.comment_service.get_by_post(post_id)
    return self.json({
        "comments": [comment.dict() for comment in comments],
        "post": {"id": post.id, "title": post.title}
    })

# Create a comment for a post
@Route("/posts/{post_id}/comments", "post.comments.create", methods=["POST"])
async def create_comment(self, post_id: int, data: CommentCreateModel):
    post = await self.post_service.get_by_id(post_id)
    if not post:
        return self.json({"error": "Post not found"}, status=404)
    
    comment_data = data.dict()
    comment_data['post_id'] = post_id
    
    comment = await self.comment_service.create(comment_data)
    return self.json({
        "comment": comment.dict(),
        "message": "Comment created successfully"
    }, status=201)
```

## API Versioning

Implement API versioning for backward compatibility:

```python
# Version 1 API
@Route("/api/v1/users", "api.v1.user.index", methods=["GET"])
async def users_v1(self):
    users = await self.user_service.get_all()
    return self.json({
        "users": [{"id": u.id, "name": u.name} for u in users]
    })

# Version 2 API with additional fields
@Route("/api/v2/users", "api.v2.user.index", methods=["GET"])
async def users_v2(self):
    users = await self.user_service.get_all()
    return self.json({
        "users": [u.dict() for u in users],
        "meta": {
            "version": "2.0",
            "total": len(users)
        }
    })
```

## Error Handling Standards

Implement consistent error responses:

```python
@Route("/api/users/{id}", "api.user.show", methods=["GET"])
async def show_user(self, id: int):
    try:
        user = await self.user_service.get_by_id(id)
        if not user:
            return self.json({
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": "User not found",
                    "details": f"No user exists with ID {id}"
                }
            }, status=404)
        
        return self.json({
            "data": user.dict(),
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
        })
    except Exception as e:
        return self.json({
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(e) if self.debug_mode else "Contact support"
            }
        }, status=500)
```

## Best Practices for RESTful APIs

### 1. Consistent Response Format

Maintain consistent response structures:

```python
# Success response format
{
    "data": {...},           # Resource data
    "meta": {...},          # Metadata
    "links": {...}          # HATEOAS links
}

# Error response format
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "details": "Additional details"
    }
}
```

### 2. Proper HTTP Status Codes

Use appropriate status codes:

- **200** - OK (successful GET, PUT, PATCH)
- **201** - Created (successful POST)
- **204** - No Content (successful DELETE)
- **400** - Bad Request (malformed request)
- **401** - Unauthorized (authentication required)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found (resource doesn't exist)
- **422** - Unprocessable Entity (validation errors)
- **500** - Internal Server Error (server errors)

### 3. Resource Naming

Follow RESTful naming conventions:

```python
# ✅ Good - Plural nouns for collections
@Route("/users", "user.index", methods=["GET"])
@Route("/posts", "post.index", methods=["GET"])

# ❌ Bad - Verbs or inconsistent naming
@Route("/get-users", "get.users", methods=["GET"])
@Route("/user", "user.list", methods=["GET"])
```

### 4. Content Negotiation

Support multiple content types:

```python
@Route("/api/users/{id}", "api.user.show", methods=["GET"])
async def show_user(self, request: Request, id: int):
    user = await self.user_service.get_by_id(id)
    
    accept_header = request.headers.get("accept", "application/json")
    
    if "application/xml" in accept_header:
        return Response(user.to_xml(), media_type="application/xml")
    else:
        return self.json({"user": user.dict()})
```

