---
title: Request Validation and Error Handling
description: Learn how to implement comprehensive request validation and error handling patterns in Framefox controllers.
---


Proper request validation ensures data integrity and provides meaningful error messages to clients. The following patterns demonstrate comprehensive validation techniques for different types of request data.

```python
@Route("/api/users", "api.user.create", methods=["POST"])
async def create_user(self, request: Request):
    # Validate content type
    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("application/json"):
        return self.json({
            "error": "Content-Type must be application/json"
        }, status=415)
    
    # Parse and validate JSON
    try:
        user_data = await request.json()
    except Exception:
        return self.json({
            "error": "Invalid JSON payload"
        }, status=400)
    
    # Validate required fields
    required_fields = ["name", "email", "password"]
    missing_fields = [field for field in required_fields if not user_data.get(field)]
    
    if missing_fields:
        return self.json({
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }, status=422)
    
    # Process validated data
    try:
        user = await self.user_service.create(user_data)
        return self.json({
            "user": user.to_dict(),
            "message": "User created successfully"
        }, status=201)
    except Exception as e:
        return self.json({
            "error": "Failed to create user",
            "details": str(e)
        }, status=500)
```

## Validation Best Practices

### Content Type Validation
Always validate the `Content-Type` header to ensure the request format matches your expectations. This prevents parsing errors and provides clear feedback to clients.

### JSON Parsing
Wrap JSON parsing in try-catch blocks to handle malformed data gracefully and return appropriate error responses.

### Field Validation
Implement comprehensive field validation that checks for:
- Required fields presence
- Data type validation
- Value range validation
- Format validation (email, phone, etc.)

### Error Response Structure
Maintain consistent error response structures with:
- Clear error messages
- Specific error details
- Appropriate HTTP status codes
- Additional context when helpful

### HTTP Status Codes
Use appropriate HTTP status codes:
- `400` - Bad Request (malformed data)
- `415` - Unsupported Media Type (wrong content type)
- `422` - Unprocessable Entity (validation errors)
- `500` - Internal Server Error (server-side issues)
