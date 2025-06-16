---
title: File Upload Handling
description: Learn how to handle file uploads safely and efficiently in Framefox controllers with validation and processing patterns.
---

File uploads require special handling to manage multipart form data, validate file types, and process file content safely.

```python
@Route("/upload", "file.upload", methods=["POST"])
async def upload_file(self, request: Request):
    # Check if request contains file uploads
    content_type = request.headers.get("content-type", "")
    if not content_type.startswith("multipart/form-data"):
        return self.json({
            "error": "Request must be multipart/form-data for file uploads"
        }, status=400)
    
    try:
        form_data = await request.form()
    except Exception:
        return self.json({
            "error": "Failed to parse form data"
        }, status=400)
    
    # Validate file field exists
    uploaded_file = form_data.get("file")
    if not uploaded_file or not hasattr(uploaded_file, 'filename'):
        return self.json({
            "error": "No file provided"
        }, status=400)
    
    # Validate file properties
    if not uploaded_file.filename:
        return self.json({
            "error": "Empty filename"
        }, status=400)
    
    # Check file size
    file_content = await uploaded_file.read()
    file_size = len(file_content)
    max_size = 5 * 1024 * 1024  # 5MB
    
    if file_size > max_size:
        return self.json({
            "error": f"File too large. Maximum size is {max_size} bytes"
        }, status=413)
    
    # Process file
    file_path = await self.file_service.save_upload(uploaded_file, file_content)
    
    return self.json({
        "message": "File uploaded successfully",
        "file_path": file_path,
        "file_size": file_size
    })
```

## File Upload Best Practices

### Content Type Validation
Always validate that the request uses `multipart/form-data` content type, which is required for file uploads.

### File Validation
Implement comprehensive file validation:
- **File existence**: Check that a file was actually uploaded
- **Filename validation**: Ensure the filename is not empty
- **File size limits**: Prevent uploads that are too large
- **File type validation**: Check file extensions and MIME types
- **Content validation**: Scan file content for security threats

### Security Considerations
- **File type restrictions**: Only allow specific file types
- **Virus scanning**: Scan uploaded files for malware
- **Storage location**: Store uploads outside the web root
- **Filename sanitization**: Clean filenames to prevent directory traversal
- **Access controls**: Implement proper authentication and authorization

### Error Handling
Provide clear error messages for common upload issues:
- `400` - Bad Request (malformed form data)
- `413` - Payload Too Large (file size exceeded)
- `415` - Unsupported Media Type (wrong content type)
- `422` - Unprocessable Entity (invalid file type)

### Storage Strategies
Consider different storage approaches:
- **Local filesystem**: Simple but not scalable
- **Cloud storage**: AWS S3, Google Cloud Storage, Azure Blob
- **CDN integration**: For fast content delivery
- **Database storage**: For small files (generally not recommended)

## Advanced File Handling

### Multiple File Uploads
```python
@Route("/upload/multiple", "file.upload.multiple", methods=["POST"])
async def upload_multiple_files(self, request: Request):
    form_data = await request.form()
    uploaded_files = form_data.getlist("files")
    
    if not uploaded_files:
        return self.json({"error": "No files provided"}, status=400)
    
    results = []
    for file in uploaded_files:
        # Process each file individually
        result = await self.process_single_file(file)
        results.append(result)
    
    return self.json({"files": results})
```

### File Type Validation
```python
def validate_file_type(self, filename: str, allowed_types: list) -> bool:
    """Validate file extension against allowed types."""
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_types
```
