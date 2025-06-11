---
title: Forms and Validation
description: Create and validate forms easily with Framefox
---

Working with forms is part of every web application. Framefox makes it straightforward to create forms, validate user input, and handle data safely.

You define your forms as Python classes, specify validation rules, and let Framefox handle the rest - including CSRF protection and error handling.

:::tip[Framework Architecture]
Framefox forms follow the builder pattern with a clear separation between form definition (FormTypeInterface), form building (FormBuilder), and form rendering (FormView). This architecture ensures maintainable, testable, and reusable form components throughout your application.
:::

## Creating Forms

### Basic Form Structure

Forms in Framefox are created by implementing the `FormTypeInterface` and defining fields using the `FormBuilder`:

```python title="src/forms/user_type.py"
from framefox.core.form.type.form_type_interface import FormTypeInterface
from framefox.core.form.form_builder import FormBuilder
from framefox.core.form.type.text_type import TextType
from framefox.core.form.type.email_type import EmailType
from framefox.core.form.type.password_type import PasswordType

class UserType(FormTypeInterface):
    """Form type for user registration and updates."""
    
    def build_form(self, builder: FormBuilder) -> None:
        """Configure form fields with validation rules."""
        builder.add('name', TextType, {
            'required': True,
            'label': 'Full Name',
            'attr': {'placeholder': 'Enter your full name'}
        })
        
        builder.add('email', EmailType, {
            'required': True,
            'label': 'Email Address',
            'attr': {'placeholder': 'user@example.com'}
        })
        
        builder.add('password', PasswordType, {
            'required': True,
            'label': 'Password',
            'attr': {'placeholder': 'Minimum 8 characters'}
        })
        
    def get_options(self) -> dict:
        """Return form-level options and attributes."""
        return {
            'attr': {'class': 'needs-validation', 'novalidate': 'novalidate'}
        }
```

:::note[Form Interface]
All forms must implement `FormTypeInterface` with the `build_form()` method. This ensures consistent form structure and enables automatic form generation features in Framefox.
:::

### Form Options and Attributes

Forms support various configuration options for enhanced functionality:

```python title="src/forms/contact_type.py"
from framefox.core.form.type.textarea_type import TextareaType

class ContactType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        builder.add('subject', TextType, {
            'required': True,
            'label': 'Subject',
            'attr': {
                'class': 'form-control',
                'maxlength': '100'
            },
            'help': 'Brief description of your inquiry'
        })
        
        builder.add('message', TextareaType, {
            'required': True,
            'label': 'Message',
            'attr': {
                'rows': 5,
                'placeholder': 'Enter your message here...'
            }
        })
        
    def get_options(self) -> dict:
        return {
            'attr': {
                'class': 'contact-form',
                'data-validate': 'true'
            },
            'method': 'POST'
        }
```

## Controller Integration

### Using Forms in Controllers

Forms integrate seamlessly with Framefox controllers through the `create_form()` method:

```python title="src/controllers/user_controller.py"
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from fastapi import Request

from src.forms.user_type import UserType
from src.entity.user import User

class UserController(AbstractController):
    @Route("/register", "user.register", methods=["GET", "POST"])
    async def register(self, request: Request):
        # Create form instance with optional data binding
        form = self.create_form(UserType)
        
        if request.method == "POST":
            # Handle form submission with automatic validation
            await form.handle_request(request)
            
            if form.is_valid():
                # Extract validated data
                data = form.get_data()
                
                # Create new user entity
                user = User()
                user.name = data["name"]
                user.email = data["email"]
                user.password = self.hash_password(data["password"])
                
                # Save to database
                await self.get_entity_manager().persist(user)
                await self.get_entity_manager().flush()
                
                # Flash success message and redirect
                self.add_flash("success", "Account created successfully!")
                return self.redirect("user.dashboard")
            else:
                # Form has validation errors
                self.add_flash("error", "Please correct the errors below.")
        
        # Render form (GET request or validation errors)
        return self.render("user/register.html", {"form": form})
```

:::note[Form Lifecycle]
The form lifecycle in Framefox follows this pattern:
1. **Creation**: Form is instantiated with `create_form()`
2. **Submission**: Request data is processed with `handle_request()`
3. **Validation**: Built-in and custom validators are executed
4. **Processing**: Valid data is extracted and processed
5. **Response**: Success redirect or error display
:::

### Form Data Binding

Forms can be pre-populated with existing entity data for edit operations:

```python title="src/controllers/user_controller.py"
@Route("/user/{user_id}/edit", "user.edit", methods=["GET", "POST"])
async def edit(self, request: Request, user_id: int):
    # Load existing user
    user = await self.get_repository("user").find(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create form with pre-populated data
    form = self.create_form(UserType, data=user)
    
    if request.method == "POST":
        await form.handle_request(request)
        
        if form.is_valid():
            # Update existing entity with form data
            updated_data = form.get_data()
            user.name = updated_data["name"]
            user.email = updated_data["email"]
            
            await self.get_entity_manager().flush()
            
            self.add_flash("success", "User updated successfully!")
            return self.redirect("user.show", user_id=user.id)
    
    return self.render("user/edit.html", {"form": form, "user": user})
```

### Error Handling and Flash Messages

Forms provide comprehensive error handling with field-level and form-level validation:

```python title="src/controllers/contact_controller.py"
@Route("/contact", "contact.submit", methods=["GET", "POST"])
async def contact(self, request: Request):
    form = self.create_form(ContactType)
    
    if request.method == "POST":
        await form.handle_request(request)
        
        if form.is_valid():
            try:
                # Process form data
                await self.get_service("email").send_contact_email(form.get_data())
                self.add_flash("success", "Message sent successfully!")
                return self.redirect("contact.thanks")
                
            except Exception as e:
                # Handle business logic errors
                self.add_flash("error", "Failed to send message. Please try again.")
                form.add_error("general", str(e))
        else:
            # Validation errors are automatically available in template
            self.add_flash("error", "Please correct the errors below.")
    
    return self.render("contact/form.html", {"form": form})
```

## Template Rendering

### Form Rendering Functions

Framefox provides powerful template functions for rendering forms with automatic CSRF protection and error handling:

```html title="templates/user/register.html"
<!DOCTYPE html>
<html>
<head>
    <title>User Registration</title>
    <link href="{{ asset('css/forms.css') }}" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1>Create Account</h1>
        
        {{ form_start(form, {'action': url_for('user.register')}) }}
            {{ csrf_token() }}
            
            <!-- Render complete field with label, input, and errors -->
            {{ form_row(form, 'name') }}
            {{ form_row(form, 'email') }}
            {{ form_row(form, 'password') }}
            
            <div class="form-actions">
                <button type="submit" class="btn btn-primary">
                    Create Account
                </button>
                <a href="{{ url_for('home') }}" class="btn btn-secondary">
                    Cancel
                </a>
            </div>
        {{ form_end(form) }}
    </div>
</body>
</html>
```

### Individual Field Rendering

For more control over form layout, render individual components:

```html title="templates/user/custom_form.html"
<!-- Custom form layout with individual components -->
<form method="POST" action="{{ url_for('user.register') }}">
    {{ csrf_token() }}
    
    <div class="row">
        <div class="col-md-6">
            <div class="form-group">
                {{ form_label(form, 'name') }}
                {{ form_widget(form, 'name', {'attr': {'class': 'form-control'}}) }}
                {{ form_errors(form, 'name') }}
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="form-group">
                {{ form_label(form, 'email') }}
                {{ form_widget(form, 'email') }}
                {{ form_errors(form, 'email') }}
            </div>
        </div>
    </div>
    
    <div class="form-group">
        {{ form_label(form, 'password') }}
        {{ form_widget(form, 'password') }}
        {{ form_errors(form, 'password') }}
        <small class="form-text text-muted">
            Must be at least 8 characters long
        </small>
    </div>
    
    <button type="submit" class="btn btn-primary">Register</button>
</form>
```

:::note[CSRF Protection]
The `csrf_token()` function automatically generates and includes CSRF protection tokens. This is mandatory for all forms and is automatically validated during form submission following [OWASP CSRF Prevention guidelines](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).
:::

### Form Rendering Functions Reference

| Function                    | Purpose                              | Example                                |
| --------------------------- | ------------------------------------ | -------------------------------------- |
| `form_start(form, options)` | Opens form tag with attributes       | `form_start(form, {'method': 'POST'})` |
| `form_end(form)`            | Closes form tag                      | `form_end(form)`                       |
| `form_row(form, field)`     | Complete field with label and errors | `form_row(form, 'email')`              |
| `form_label(form, field)`   | Field label only                     | `form_label(form, 'name')`             |
| `form_widget(form, field)`  | Field input only                     | `form_widget(form, 'password')`        |
| `form_errors(form, field)`  | Field errors only                    | `form_errors(form, 'email')`           |

## Available Field Types

### Basic Field Types

Framefox provides comprehensive field types for all common form inputs:

| Type           | Purpose             | Features                                      |
| -------------- | ------------------- | --------------------------------------------- |
| `TextType`     | Basic text input    | String validation, length constraints         |
| `EmailType`    | Email address input | Built-in email format validation              |
| `PasswordType` | Password input      | Masked input, strength validation             |
| `NumberType`   | Numeric input       | Integer/float validation, min/max constraints |
| `TextareaType` | Multi-line text     | Configurable rows, character limits           |
| `CheckboxType` | Boolean checkbox    | True/false values                             |
| `DateTimeType` | Date/time picker    | Native HTML5 datetime-local support           |

### Choice and Selection Types

```python title="src/forms/profile_type.py"
from framefox.core.form.type.select_type import SelectType
from framefox.core.form.type.choice_type import ChoiceType

class ProfileType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        # Dropdown selection
        builder.add('country', SelectType, {
            'required': True,
            'label': 'Country',
            'choices': {
                'us': 'United States',
                'ca': 'Canada',
                'uk': 'United Kingdom',
                'fr': 'France'
            },
            'empty_label': 'Select your country...'
        })
        
        # Radio buttons (expanded choice)
        builder.add('gender', ChoiceType, {
            'required': False,
            'label': 'Gender',
            'choices': {
                'male': 'Male',
                'female': 'Female',
                'other': 'Other'
            },
            'expanded': True,  # Renders as radio buttons
            'multiple': False
        })
        
        # Multiple checkboxes
        builder.add('interests', ChoiceType, {
            'required': False,
            'label': 'Interests',
            'choices': {
                'tech': 'Technology',
                'sports': 'Sports',
                'music': 'Music',
                'travel': 'Travel'
            },
            'expanded': True,  # Renders as checkboxes
            'multiple': True   # Allows multiple selections
        })
```

### File Upload Type

The `FileType` provides secure file upload functionality with validation:

```python title="src/forms/document_type.py"
from framefox.core.form.type.file_type import FileType

class DocumentType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        builder.add('title', TextType, {
            'required': True,
            'label': 'Document Title'
        })
        
        builder.add('document', FileType, {
            'required': True,
            'label': 'Upload File',
            'accept': 'image/*,.pdf,.doc,.docx',
            'allowed_extensions': ['.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'],
            'max_file_size': 5 * 1024 * 1024,  # 5MB
            'storage_path': 'public/documents',
            'rename': True,  # Generate unique filename
            'help': 'Accepted formats: Images, PDF, Word documents. Max size: 5MB'
        })
```

:::caution[File Security]
Always validate file uploads on both client and server side. The `FileType` automatically validates file extensions, MIME types, and file sizes to prevent security vulnerabilities.
:::

### Entity Relationship Type

The `EntityType` enables forms to work directly with database entities:

```python title="src/forms/order_type.py"
from framefox.core.form.type.entity_type import EntityType

class OrderType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        # Single entity selection
        builder.add('customer', EntityType, {
            'class': 'Customer',
            'required': True,
            'label': 'Customer',
            'choice_label': 'name',  # Display customer name
            'show_id': False         # Hide ID in display
        })
        
        # Multiple entity selection
        builder.add('products', EntityType, {
            'class': 'Product',
            'multiple': True,
            'required': False,
            'label': 'Products',
            'choice_label': 'name',
            'show_id': True
        })
```

### Collection Type

Handle dynamic collections of form data:

```python title="src/forms/invoice_type.py"
from framefox.core.form.type.collection_type import CollectionType

class InvoiceType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        builder.add('invoice_number', TextType, {
            'required': True,
            'label': 'Invoice Number'
        })
        
        # Collection of line items
        builder.add('line_items', CollectionType, {
            'entry_type': TextType,
            'entry_options': {
                'label': 'Item Description'
            },
            'allow_add': True,
            'allow_delete': True,
            'label': 'Line Items'
        })
```

## Form Validation

### Built-in Validation

Forms automatically validate field types and constraints:

```python title="src/forms/registration_type.py"
class RegistrationType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        builder.add('username', TextType, {
            'required': True,
            'label': 'Username',
            'attr': {
                'minlength': '3',
                'maxlength': '20',
                'pattern': '[a-zA-Z0-9_]+'
            }
        })
        
        builder.add('age', NumberType, {
            'required': True,
            'label': 'Age',
            'attr': {
                'min': '18',
                'max': '120',
                'step': '1'
            }
        })
        
        builder.add('email', EmailType, {
            'required': True,
            'label': 'Email Address'
            # Automatic email format validation
        })
```

### Custom Field Validation

Implement custom validation logic for specific business rules:

```python title="src/forms/types/custom_password_type.py"
from framefox.core.form.type.text_type import TextType

class CustomPasswordType(TextType):
    """Custom password field with strength validation."""
    
    def transform_to_model(self, value):
        """Validate password strength before transformation."""
        if not value:
            return value
            
        # Check password strength
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
            
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter")
            
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit")
            
        if not any(not c.isalnum() for c in value):
            raise ValueError("Password must contain at least one special character")
            
        return value
    
    def get_block_prefix(self) -> str:
        return "password"

# Use custom field type
class SecureUserType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        builder.add('password', CustomPasswordType, {
            'required': True,
            'label': 'Secure Password'
        })
```

### Form-Level Validation

Implement cross-field validation at the form level:

```python title="src/forms/password_change_type.py"
class PasswordChangeType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        builder.add('current_password', PasswordType, {
            'required': True,
            'label': 'Current Password'
        })
        
        builder.add('new_password', PasswordType, {
            'required': True,
            'label': 'New Password'
        })
        
        builder.add('confirm_password', PasswordType, {
            'required': True,
            'label': 'Confirm New Password'
        })
    
    def validate(self, form) -> bool:
        """Custom form validation."""
        if not super().validate(form):
            return False
            
        data = form.get_data()
        
        # Check if new passwords match
        if data['new_password'] != data['confirm_password']:
            form.add_error('confirm_password', 'Passwords do not match')
            return False
            
        # Check if new password is different from current
        if data['current_password'] == data['new_password']:
            form.add_error('new_password', 'New password must be different from current password')
            return False
            
        return True
```

## File Upload Handling

### Controller File Processing

Handle uploaded files securely in your controllers:

```python title="src/controllers/document_controller.py"
from fastapi import UploadFile
import os

@Route("/upload", "document.upload", methods=["GET", "POST"])
async def upload_document(self, request: Request):
    form = self.create_form(DocumentType)
    
    if request.method == "POST":
        await form.handle_request(request)
        
        if form.is_valid():
            data = form.get_data()
            uploaded_file = data["document"]
            
            if uploaded_file:
                try:
                    # File is automatically saved by FileType
                    # Get the saved file path
                    file_path = uploaded_file  # FileType returns the saved path
                    
                    # Save file metadata to database
                    document = Document()
                    document.title = data["title"]
                    document.file_path = file_path
                    document.original_name = uploaded_file.filename
                    document.file_size = uploaded_file.size
                    document.content_type = uploaded_file.content_type
                    
                    await self.get_entity_manager().persist(document)
                    await self.get_entity_manager().flush()
                    
                    self.add_flash("success", "Document uploaded successfully!")
                    return self.redirect("document.list")
                    
                except Exception as e:
                    self.add_flash("error", f"Upload failed: {str(e)}")
    
    return self.render("document/upload.html", {"form": form})
```

### File Upload Configuration

Configure file uploads with security best practices:

```python title="src/forms/avatar_upload_type.py"
class AvatarUploadType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        builder.add('avatar', FileType, {
            'required': False,
            'label': 'Profile Picture',
            'accept': 'image/*',
            'allowed_extensions': ['.jpg', '.jpeg', '.png', '.gif'],
            'max_file_size': 2 * 1024 * 1024,  # 2MB
            'storage_path': 'public/avatars',
            'rename': True,
            'attr': {
                'class': 'form-control-file'
            },
            'help': 'Upload a profile picture (JPG, PNG, GIF). Max size: 2MB.'
        })
```

:::note[File Storage]
Framefox automatically handles file storage, validation, and security. Files are validated for:
- **File size limits**: Prevent large file uploads
- **Extension validation**: Only allowed file types
- **MIME type checking**: Additional security layer
- **Unique naming**: Prevent filename conflicts
:::

## CRUD Generation

### Using the Create CRUD Command

Framefox can automatically generate complete CRUD forms based on your entities:

```bash title="Terminal"
framefox create crud
```

This interactive command will:

1. **Select Entity**: Choose from existing entities in your project
2. **Generate Form Type**: Create a form class with all entity fields
3. **Create Controller**: Generate CRUD controller with form handling
4. **Generate Templates**: Create complete view templates for all operations

:::tip[Entity-Based Forms]
The CRUD generator analyzes your entity properties and automatically selects appropriate field types:
- String properties → `TextType`
- Email properties → `EmailType`
- Password properties → `PasswordType`
- Boolean properties → `CheckboxType`
- DateTime properties → `DateTimeType`
- File properties → `FileType`
- Entity relationships → `EntityType`
:::

### Generated Form Example

When you run `framefox create crud` on a `User` entity, it generates:

```python title="src/forms/user_type.py"
from framefox.core.form.type.form_type_interface import FormTypeInterface
from framefox.core.form.form_builder import FormBuilder
from framefox.core.form.type.text_type import TextType
from framefox.core.form.type.email_type import EmailType
from framefox.core.form.type.checkbox_type import CheckboxType
from framefox.core.form.type.entity_type import EntityType

class UserType(FormTypeInterface):
    """Form for User entity."""
    
    def build_form(self, builder: FormBuilder) -> None:
        """Configure form fields."""
        builder.add('name', TextType, {
            'required': True,
            'label': 'Name',
        })
        
        builder.add('email', EmailType, {
            'required': True,
            'label': 'Email',
        })
        
        builder.add('active', CheckboxType, {
            'required': False,
            'label': 'Active',
        })
        
        builder.add('role', EntityType, {
            'class': 'Role',
            'required': True,
            'label': 'Role',
            'choice_label': 'name',
            'show_id': True,
        })
        
    def get_options(self) -> dict:
        return {
            'attr': {'class': 'needs-validation', 'novalidate': 'novalidate'}
        }
```

### Generated Controller with Forms

The CRUD command also generates a complete controller with form handling:

```python title="src/controllers/user_controller.py"
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController
from fastapi import Request

from src.forms.user_type import UserType
from src.entity.user import User

class UserController(AbstractController):
    @Route("/user/create", "user.create", methods=["GET", "POST"])
    async def create(self, request: Request):
        form = self.create_form(UserType)
        
        if request.method == "POST":
            await form.handle_request(request)
            
            if form.is_valid():
                data = form.get_data()
                user = User()
                
                # Map form data to entity
                for field_name, value in data.items():
                    setattr(user, field_name, value)
                
                await self.get_entity_manager().persist(user)
                await self.get_entity_manager().flush()
                
                self.add_flash("success", "User created successfully!")
                return self.redirect("user.index")
        
        return self.render("user/create.html", {"form": form})
    
    @Route("/user/{user_id}/edit", "user.edit", methods=["GET", "POST"])
    async def edit(self, request: Request, user_id: int):
        user = await self.get_repository("user").find(user_id)
        if not user:
            raise HTTPException(status_code=404)
        
        form = self.create_form(UserType, data=user)
        
        if request.method == "POST":
            await form.handle_request(request)
            
            if form.is_valid():
                data = form.get_data()
                
                # Update entity with form data
                for field_name, value in data.items():
                    setattr(user, field_name, value)
                
                await self.get_entity_manager().flush()
                
                self.add_flash("success", "User updated successfully!")
                return self.redirect("user.index")
        
        return self.render("user/edit.html", {"form": form, "user": user})
```

## Advanced Form Features

### Dynamic Form Fields

Create forms that adapt based on user input or conditions:

```python title="src/forms/conditional_form_type.py"
class ConditionalFormType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        builder.add('user_type', SelectType, {
            'required': True,
            'label': 'User Type',
            'choices': {
                'individual': 'Individual',
                'business': 'Business'
            }
        })
        
        builder.add('name', TextType, {
            'required': True,
            'label': 'Full Name'
        })
        
        # Conditional fields based on user type
        # These would be shown/hidden via JavaScript
        builder.add('company_name', TextType, {
            'required': False,
            'label': 'Company Name',
            'attr': {
                'data-show-when': 'user_type=business'
            }
        })
        
        builder.add('tax_id', TextType, {
            'required': False,
            'label': 'Tax ID',
            'attr': {
                'data-show-when': 'user_type=business'
            }
        })
```

### Form Themes and Customization

Customize form rendering with themes and custom templates:

```html title="templates/forms/custom_theme.html"
<!-- Custom form theme template -->
<!-- templates/forms/custom_theme.html -->

{% macro form_row(form, field_name) %}
    {% set field = form.get_field(field_name) %}
    <div class="custom-form-group {{ 'has-error' if field.has_errors() else '' }}">
        <label for="{{ field.get_id() }}" class="custom-label">
            {{ field.options.label }}
            {% if field.options.required %}
                <span class="required-indicator">*</span>
            {% endif %}
        </label>
        
        <div class="custom-input-wrapper">
            {{ form_widget(form, field_name) }}
            {% if field.options.help %}
                <small class="custom-help-text">{{ field.options.help }}</small>
            {% endif %}
        </div>
        
        {% if field.has_errors() %}
            <div class="custom-error-messages">
                {% for error in field.get_errors() %}
                    <span class="custom-error">{{ error }}</span>
                {% endfor %}
            </div>
        {% endif %}
    </div>
{% endmacro %}
```

:::note[Form Security Best Practices]
Always implement these security measures in your forms:
- **CSRF Protection**: Use `csrf_token()` in all forms
- **Input Validation**: Validate both client-side and server-side
- **File Upload Security**: Restrict file types, sizes, and storage locations
- **SQL Injection Prevention**: Use ORM methods for database operations
- **XSS Prevention**: Escape all user input in templates
- **Data Sanitization**: Clean and validate all form inputs
:::

## Best Practices

### Form Organization

Structure your forms for maintainability and reusability:

```python title="src/forms/base/base_form.py"
# src/forms/base/base_form.py
class BaseFormType(FormTypeInterface):
    """Base form with common functionality."""
    
    def get_options(self) -> dict:
        return {
            'attr': {
                'class': 'needs-validation',
                'novalidate': 'novalidate'
            }
        }

# src/forms/user/user_registration_type.py
class UserRegistrationType(BaseFormType):
    """Specific form for user registration."""
    
    def build_form(self, builder: FormBuilder) -> None:
        # Registration-specific fields
        pass

# src/forms/user/user_profile_type.py  
class UserProfileType(BaseFormType):
    """Form for user profile editing."""
    
    def build_form(self, builder: FormBuilder) -> None:
        # Profile-specific fields
        pass
```

### Performance Optimization

Optimize forms for better performance:

```python title="src/forms/optimized_form_type.py"
class OptimizedFormType(FormTypeInterface):
    def build_form(self, builder: FormBuilder) -> None:
        # Use lazy loading for entity choices
        builder.add('category', EntityType, {
            'class': 'Category',
            'choice_label': 'name',
            'query_builder': self._get_category_query  # Custom query
        })
    
    def _get_category_query(self):
        """Custom query for better performance."""
        return self.get_repository('category').createQueryBuilder('c').where('c.active = :active').setParameter('active', True)
```

### Testing Forms

Write comprehensive tests for your forms:

```python title="src/tests/test_user_type.py"
import pytest
from src.forms.user_type import UserType

class TestUserType:
    def test_form_validation_success(self):
        """Test successful form validation."""
        form = UserType()
        form_builder = FormBuilder()
        form.build_form(form_builder)
        
        # Simulate valid form data
        form_instance = form_builder.get_form()
        form_instance.fields['name'].set_value('John Doe')
        form_instance.fields['email'].set_value('john@example.com')
        form_instance.fields['password'].set_value('SecurePass123!')
        
        assert form_instance.validate() == True
    
    def test_form_validation_failure(self):
        """Test form validation with invalid data."""
        form = UserType()
        form_builder = FormBuilder()
        form.build_form(form_builder)
        
        form_instance = form_builder.get_form()
        form_instance.fields['email'].set_value('invalid-email')
        
        assert form_instance.validate() == False
        assert len(form_instance.fields['email'].errors) > 0
```

Forms in Framefox provide a robust, secure, and flexible foundation for handling user input in your web applications. By following the patterns and best practices outlined in this guide, you can create maintainable and secure forms that scale with your application's needs.