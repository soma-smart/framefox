---
title: Templates and Views
description: Complete guide to Jinja2 template system in Framefox
---

# Templates and Views

Framefox uses **Jinja2** as its template engine, allowing you to create dynamic and reusable views. The system is integrated with numerous Framefox-specific features and provides a powerful foundation for building modern web applications.

Templates in Framefox serve as the presentation layer of your application, handling how data is displayed to users. The template system includes built-in security features, asset management, URL generation, and seamless integration with the framework's core components.

:::tip[Template Organization]
Organize your templates logically to maintain scalability and readability. Use descriptive names and group related templates in folders that match your application's structure.
:::

:::note[Framework Integration]
Framefox's template system provides automatic integration with:
- **CSRF Protection**: Built-in token generation for forms
- **Asset Management**: Versioned static file URLs with cache busting
- **URL Generation**: Type-safe route URL generation
- **Flash Messages**: Session-based user notifications
- **User Authentication**: Current user context in templates
:::

## Template Structure

Template structure in Framefox is crucial for maintaining clean, scalable code. A well-organized template hierarchy promotes code reusability, easier maintenance, and consistent user interface across your application. The framework encourages separation of concerns by organizing templates into logical groups that mirror your application's functionality.

### File Organization

The recommended template structure follows MVC conventions and promotes maintainability. This organization ensures that developers can quickly locate and modify templates while maintaining consistency across the application:

```
src/templates/
├── base.html              # Base template with common HTML structure
├── layouts/
│   ├── app.html          # Main application layout for user interface
│   └── admin.html        # Admin panel layout with specialized navigation
├── components/
│   ├── navbar.html       # Reusable navigation component
│   └── footer.html       # Site footer component
├── user/
│   ├── index.html        # User listing page
│   ├── show.html         # Individual user details page
│   └── edit.html         # User editing interface
└── errors/
    ├── 404.html          # Custom 404 error page
    └── 500.html          # Custom 500 error page
```

## Base Template

The base template serves as the foundation for all pages in your application. It defines the common HTML structure, includes essential meta tags, loads global assets, and provides block definitions that child templates can override. This approach ensures consistency while allowing flexibility for specific page requirements.

### base.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My Framefox Application{% endblock %}</title>
    
    <!-- CSS -->
    <link href="{{ asset('css/app.css') }}" rel="stylesheet">
    {% block stylesheets %}{% endblock %}
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <a class="brand" href="{{ url_for('home.index') }}">
                My App
            </a>
            
            <div class="nav-links">
                {% if current_user %}
                    <a class="nav-link" href="{{ url_for('user.profile') }}">
                        {{ current_user.name }}
                    </a>
                    <a class="nav-link" href="{{ url_for('security.logout') }}">
                        Logout
                    </a>
                {% else %}
                    <a class="nav-link" href="{{ url_for('security.login') }}">
                        Login
                    </a>
                {% endif %}
            </div>
        </div>
    </nav>

    <main class="main-content">
        <!-- Flash messages -->
        {% for message in get_flash_messages() %}
            <div class="alert alert-{{ message.type }}">
                {{ message.content }}
                <button type="button" class="close-btn">×</button>
            </div>
        {% endfor %}

        {% block content %}{% endblock %}
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 My Application. Built with Framefox.</p>
        </div>
    </footer>

    <!-- JavaScript -->
    <script src="{{ asset('js/app.js') }}"></script>
    {% block javascripts %}{% endblock %}
</body>
</html>
```

## Rendering from Controllers

Controllers in Framefox use the `render()` method to process templates and return HTML responses. This method integrates seamlessly with the template engine and automatically injects framework-specific context variables. The rendering process handles template inheritance, includes security features, and provides access to all global template functions.

### render() Method

The primary method for rendering templates from controllers provides a clean interface for passing data to your views:

```python
from framefox.core.controller.abstract_controller import AbstractController

class UserController(AbstractController):
    @Route("/users", "user.index", methods=["GET"])
    async def index(self):
        users = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ]
        
        return self.render("user/index.html", {
            "users": users,
            "page_title": "User List"
        })
```

### With Custom Layout

For specialized sections of your application, you may want to use different layouts while maintaining the same rendering approach:

```python
@Route("/admin/dashboard", "admin.dashboard", methods=["GET"])
async def dashboard(self):
    return self.render("admin/dashboard.html", {
        "stats": {"users": 150, "posts": 340}
    }, layout="layouts/admin.html")
```

## Page Templates

Page templates represent the individual views of your application. They extend the base template and define specific content for each page. These templates use Jinja2's template inheritance system to maintain consistency while allowing for page-specific customizations. Each template focuses on presenting data in a user-friendly format.

### user/index.html

The index template typically displays a list of items with navigation and action buttons:

```html
{% extends "base.html" %}

{% block title %}{{ page_title }} - {{ super() }}{% endblock %}

{% block content %}
<div class="page-header">
    <h1>{{ page_title }}</h1>
    <a href="{{ url_for('user.create') }}" class="btn btn-primary">
        New User
    </a>
</div>

{% if users %}
    <div class="user-list">
        {% for user in users %}
        <div class="user-item">
            <h3>{{ user.name }}</h3>
            <p>{{ user.email }}</p>
            <div class="actions">
                <a href="{{ url_for('user.show', id=user.id) }}">View</a>
                <a href="{{ url_for('user.edit', id=user.id) }}">Edit</a>
            </div>
        </div>
        {% endfor %}
    </div>
{% else %}
    <div class="empty-state">
        <p>No users found.</p>
    </div>
{% endif %}
{% endblock %}
```

### user/show.html

The show template displays detailed information about a single entity, presenting all relevant data in a structured format:

```html
{% extends "base.html" %}

{% block title %}{{ user.name }} - {{ super() }}{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header">
                <h2>{{ user.name }}</h2>
            </div>
            <div class="card-body">
                <dl class="row">
                    <dt class="col-sm-3">ID</dt>
                    <dd class="col-sm-9">{{ user.id }}</dd>
                    
                    <dt class="col-sm-3">Name</dt>
                    <dd class="col-sm-9">{{ user.name }}</dd>
                    
                    <dt class="col-sm-3">Email</dt>
                    <dd class="col-sm-9">{{ user.email }}</dd>
                    
                    <dt class="col-sm-3">Created At</dt>
                    <dd class="col-sm-9">{{ user.created_at|date('d/m/Y H:i') }}</dd>
                </dl>
            </div>
            <div class="card-footer">
                <a href="{{ url_for('user.edit', id=user.id) }}" 
                   class="btn btn-primary">
                    Edit
                </a>
                <a href="{{ url_for('user.index') }}" 
                   class="btn btn-secondary">
                    Back to List
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Built-in Framefox Functions

Framefox provides a comprehensive set of built-in template functions that integrate seamlessly with the framework's core features. These functions handle common tasks like URL generation, asset management, security, and user authentication. They are automatically available in all templates without requiring imports or additional configuration.

:::tip[Template Functions]
All Framefox template functions are globally available and provide safe, framework-integrated functionality for your templates.
:::

### URL Generation

The `url_for()` function generates URLs based on your named routes. This approach provides significant advantages over hardcoded URLs and is essential for maintaining flexible applications.

**Why `url_for()` is Essential:**

- **Route Independence**: URLs are generated dynamically from route names, so changing route patterns doesn't break your links
- **Parameter Safety**: Automatic URL encoding and parameter validation prevent malformed URLs
- **Maintainability**: Centralizes URL management, making large applications easier to refactor
- **Environment Flexibility**: Automatically adapts to different base URLs (development, staging, production)
- **Type Safety**: Framework validates route names and required parameters at generation time

```html
<!-- Basic route -->
<a href="{{ url_for('home.index') }}">Home</a>

<!-- Route with parameters -->
<a href="{{ url_for('user.show', id=user.id) }}">View Profile</a>

<!-- Route with query parameters -->
<a href="{{ url_for('posts.index', category='tech', page=2) }}">Tech Posts</a>

<!-- Complex routing with multiple parameters -->
<a href="{{ url_for('admin.user.edit', user_id=user.id, section='profile') }}">
    Edit User Profile
</a>
```

### Asset Management

The `asset()` function manages static file URLs by automatically resolving paths within your application's public directory. This function sources all static resources from the `public/` folder in your project root, providing a centralized location for CSS, JavaScript, images, fonts, and other static content.

**Public Directory Structure:**
```
public/
├── css/
│   ├── app.css
│   └── vendor/
├── js/
│   ├── app.js
│   └── components/
├── images/
│   ├── logo.png
│   └── icons/
└── fonts/
    └── custom-font.woff2
```

The `asset()` function automatically prepends the correct base path and can include versioning for cache management:

```html
<!-- CSS files from public/css/ -->
<link href="{{ asset('css/app.css') }}" rel="stylesheet">
<link href="{{ asset('css/vendor/bootstrap.min.css') }}" rel="stylesheet">

<!-- JavaScript files from public/js/ -->
<script src="{{ asset('js/app.js') }}"></script>
<script src="{{ asset('js/components/modal.js') }}"></script>

<!-- Images from public/images/ -->
<img src="{{ asset('images/logo.png') }}" alt="Company Logo">
<img src="{{ asset('images/icons/user-avatar.svg') }}" alt="User Avatar">

<!-- Fonts from public/fonts/ -->
<link href="{{ asset('fonts/custom-font.woff2') }}" rel="preload" as="font">
```

### Security Integration

Framefox provides robust security features directly integrated into the template system, with CSRF (Cross-Site Request Forgery) protection being a critical component for preventing malicious attacks.

:::note[CSRF Protection & OWASP Guidelines]
CSRF attacks occur when malicious websites trick users into performing unintended actions on sites where they're authenticated. According to the [OWASP Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), implementing token-based CSRF protection is essential for web application security. Framefox automatically generates unique CSRF tokens for each user session and validates them on form submissions.
:::

CSRF token implementation in Framefox templates:

```html
<!-- CSRF protection for forms -->
<form method="POST" action="{{ url_for('user.update', id=user.id) }}">
    {{ csrf_token() }}
    <input type="text" name="name" value="{{ user.name }}" required>
    <button type="submit">Update User</button>
</form>

<!-- CSRF token for AJAX requests -->
<script>
    const csrfToken = '{{ csrf_token() }}';
    fetch('{{ url_for("api.update_data") }}', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
</script>
```

**Authentication Context:**

Access current user information securely throughout your templates:

```html
{% if current_user %}
    <div class="user-info">
        <span>Welcome, {{ current_user.name }}!</span>
        <a href="{{ url_for('auth.logout') }}">Logout</a>
    </div>
{% else %}
    <div class="auth-links">
        <a href="{{ url_for('auth.login') }}">Login</a>
        <a href="{{ url_for('auth.register') }}">Sign Up</a>
    </div>
{% endif %}
```

### Flash Messages

Flash messages provide a powerful mechanism for displaying temporary notifications to users across page requests. They work by storing messages in the user's session and automatically clearing them after display, making them perfect for success confirmations, error notifications, and user feedback.

**How Flash Messages Work:**

1. **Controller Stage**: Controllers add messages to the flash bag using `self.flash()`
2. **Session Storage**: Messages are temporarily stored in the user's session
3. **Template Display**: Templates retrieve and display messages using `get_flash_messages()`
4. **Automatic Cleanup**: Messages are removed from session after being displayed once

**Sending Flash Messages from Controllers:**

```python
# In your controller methods
class UserController(AbstractController):
    async def create(self, request: Request):
        try:
            # Create user logic
            user = await self.create_user(form_data)
            
            # Success message
            self.flash("User created successfully!", "success")
            return self.redirect("user.index")
            
        except ValidationError as e:
            # Error message
            self.flash("Failed to create user: " + str(e), "error")
            return self.redirect("user.create")
            
        except Exception as e:
            # Warning message
            self.flash("Unexpected error occurred. Please try again.", "warning")
            return self.redirect("user.create")
```

**Displaying Messages in Templates:**

```html
<!-- Display all flash messages -->
{% for message in get_flash_messages() %}
    <div class="alert alert-{{ message.type }} alert-dismissible">
        {{ message.content }}
        <button type="button" class="close-btn" data-dismiss="alert">×</button>
    </div>
{% endfor %}

<!-- Filter messages by type -->
{% for message in get_flash_messages() %}
    {% if message.type == 'error' %}
        <div class="error-banner">
            <i class="icon-error"></i>
            {{ message.content }}
        </div>
    {% endif %}
{% endfor %}
```

### Request Context

The `request` object provides direct access to the current HTTP request information within templates, enabling dynamic content generation based on request characteristics, user behavior, and contextual information.

**Why Request Context is Useful:**

- **Conditional Rendering**: Show different content based on request method, headers, or parameters
- **URL Analysis**: Display breadcrumbs, active navigation states, or page-specific information
- **User Agent Detection**: Adapt interface for different devices or browsers
- **Search Functionality**: Maintain search terms and filters across page interactions
- **Debug Information**: Display request details during development for troubleshooting

```html
<!-- Current path and navigation -->
<nav class="breadcrumb">
    <a href="{{ url_for('home.index') }}">Home</a>
    {% if request.url.path.startswith('/admin') %}
        <span>→ <a href="{{ url_for('admin.index') }}">Admin</a></span>
    {% endif %}
    <span>→ {{ page_title }}</span>
</nav>

<!-- Search functionality -->
{% if request.query_params.search %}
    <div class="search-results">
        <p>Search results for: <strong>{{ request.query_params.search }}</strong></p>
        <a href="{{ request.url.path }}">Clear search</a>
    </div>
{% endif %}

<!-- Active navigation highlighting -->
<ul class="nav">
    <li class="nav-item">
        <a href="{{ url_for('home.index') }}" 
           class="nav-link{% if request.url.path == '/' %} active{% endif %}">
            Home
        </a>
    </li>
    <li class="nav-item">
        <a href="{{ url_for('user.index') }}" 
           class="nav-link{% if request.url.path.startswith('/users') %} active{% endif %}">
            Users
        </a>
    </li>
</ul>

<!-- Device-specific content -->
{% if 'Mobile' in request.headers.get('user-agent', '') %}
    <div class="mobile-menu">
        <!-- Simplified mobile navigation -->
    </div>
{% else %}
    <div class="desktop-menu">
        <!-- Full desktop navigation -->
    </div>
{% endif %}

<!-- Development debugging -->
{% if app.debug %}
    <div class="debug-info">
        <details>
            <summary>Request Debug Information</summary>
            <p><strong>Method:</strong> {{ request.method }}</p>
            <p><strong>Path:</strong> {{ request.url.path }}</p>
            <p><strong>Query:</strong> {{ request.url.query }}</p>
            <p><strong>User Agent:</strong> {{ request.headers.get('user-agent', 'Unknown') }}</p>
        </details>
    </div>
{% endif %}
```

## Forms

### Creating Forms

```html
{% extends "base.html" %}

{% block title %}Create User - {{ super() }}{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h3>Create User</h3>
            </div>
            <div class="card-body">
                <form method="POST">
                    {{ csrf_token() }}
                    
                    <div class="mb-3">
                        <label for="name" class="form-label">Full Name</label>
                        <input type="text" 
                               class="form-control" 
                               id="name" 
                               name="name" 
                               value="{{ form.name.value if form.name.value else '' }}"
                               required>
                        {% if form.name.errors %}
                            <div class="text-danger">
                                {% for error in form.name.errors %}
                                    <small>{{ error }}</small>
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" 
                               class="form-control" 
                               id="email" 
                               name="email" 
                               value="{{ form.email.value if form.email.value else '' }}"
                               required>
                        {% if form.email.errors %}
                            <div class="text-danger">
                                {% for error in form.email.errors %}
                                    <small>{{ error }}</small>
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                    
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" 
                               class="form-control" 
                               id="password" 
                               name="password" 
                               required>
                    </div>
                    
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary">
                            Create User
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

## Template Filters

Framefox extends Jinja2's built-in filters with custom functionality for common formatting and data manipulation tasks. These filters enhance template readability by providing clean, reusable transformations that can be applied to any data passed to your templates.

:::note[Filter Chaining]
Filters can be chained together using the pipe operator (`|`) to create complex transformations in a readable way.
:::

### Date and Time Formatting

Format dates and times consistently across your application:

```html
<!-- Standard date formatting -->
<p>Published: {{ post.created_at|date('F j, Y') }}</p>
<p>Last updated: {{ article.updated_at|date('M d, Y H:i') }}</p>

<!-- Relative time -->
<span>{{ comment.created_at|timeago }}</span>
```

### Text Processing

Transform and format text content:

```html
<!-- Text truncation and capitalization -->
<h2>{{ post.title|title }}</h2>
<p>{{ post.excerpt|truncate(100) }}...</p>

<!-- String manipulation -->
<div class="tags">
    {% for tag in "web,design,development"|split(',') %}
        <span class="tag">{{ tag|trim }}</span>
    {% endfor %}
</div>
```

### Number and Data Formatting

Format numeric data and file sizes for better user experience:

```html
<!-- Number formatting -->
<p>Price: ${{ product.price|round(2) }}</p>
<p>Downloads: {{ stats.downloads|format_number }}</p>

<!-- File size -->
<p>Size: {{ document.size|filesizeformat }}</p>

<!-- Lists and arrays -->
<p>Latest item: {{ items|last }}</p>
<p>Total range: {{ values|min }} - {{ values|max }}</p>
```

### Custom Framefox Filters

Specialized filters designed for web development workflows:

```html
<!-- JSON encoding for JavaScript -->
<script>
    const data = {{ python_dict|json_encode|safe }};
</script>

<!-- String slicing -->
<p>Preview: {{ content|slice(0, 50) }}...</p>

<!-- Safe HTML rendering -->
<div class="content">{{ user_content|safe }}</div>
```

## Template Macros

Macros in Framefox templates allow you to create reusable components that encapsulate common UI patterns. They function like functions in programming languages, accepting parameters and generating HTML output. This approach promotes code reuse and maintains consistency across your application's interface.

:::tip[Macro Organization]
Store your macros in dedicated files within a `macros/` directory and import them where needed to keep templates organized.
:::

### Creating Reusable Components

Define macros for common interface elements that appear throughout your application:

```html
<!-- macros/ui.html -->
{% macro button(text, url=none, type="button", class="primary") %}
<a href="{{ url if url else '#' }}" 
   class="btn btn-{{ class }}"
   {% if not url %}type="{{ type }}"{% endif %}>
    {{ text }}
</a>
{% endmacro %}

{% macro card(title, content, footer=none) %}
<div class="card">
    <div class="card-header">
        <h3>{{ title }}</h3>
    </div>
    <div class="card-body">
        {{ content }}
    </div>
    {% if footer %}
    <div class="card-footer">
        {{ footer }}
    </div>
    {% endif %}
</div>
{% endmacro %}
```

### Using Macros in Templates

Import and use macros to build consistent interfaces quickly:

```html
{% from 'macros/ui.html' import button, card %}

{% extends "base.html" %}

{% block content %}
{{ card(
    title="User Profile",
    content="<p>Name: " + user.name + "</p><p>Email: " + user.email + "</p>",
    footer=button("Edit Profile", url_for('user.edit', id=user.id))
) }}
{% endblock %}
```

### Advanced Macro Features

Create more sophisticated macros with conditional logic and nested content:

```html
{% macro alert(message, type="info", dismissible=true) %}
<div class="alert alert-{{ type }}{% if dismissible %} alert-dismissible{% endif %}">
    {{ message }}
    {% if dismissible %}
        <button type="button" class="close-btn">×</button>
    {% endif %}
</div>
{% endmacro %}

{% macro navigation_item(text, route, icon=none, active=false) %}
<li class="nav-item{% if active %} active{% endif %}">
    <a href="{{ url_for(route) }}" class="nav-link">
        {% if icon %}<i class="icon-{{ icon }}"></i>{% endif %}
        {{ text }}
    </a>
</li>
{% endmacro %}
```

## Template Includes and Components

Template includes allow you to break down complex layouts into smaller, manageable components. This modular approach promotes code reuse and makes maintenance easier. Components can be simple static includes or dynamic partials that accept context variables.

:::note[Component Organization]
Organize your includes in a logical structure, typically separating navigation, content components, and layout partials.
:::

## Includes and Components

### Template Inclusion

Include static template fragments to build modular layouts:

```html
<!-- Main layout structure -->
{% include "components/navbar.html" %}

<main class="main-content">
    {% block content %}{% endblock %}
</main>

{% include "components/footer.html" %}
```

### Dynamic Components

Pass variables to included templates for flexible component behavior:

```html
<!-- components/user-card.html -->
<div class="user-card">
    <h3>{{ user.name }}</h3>
    <p>{{ user.email }}</p>
    <span class="join-date">Joined: {{ user.created_at|date('M Y') }}</span>
    {% if show_actions %}
    <div class="actions">
        <a href="{{ url_for('user.show', id=user.id) }}">View</a>
        <a href="{{ url_for('user.edit', id=user.id) }}">Edit</a>
    </div>
    {% endif %}
</div>

<!-- Usage with context variables -->
{% for user in users %}
    {% set show_actions = current_user.is_admin %}
    {% include "components/user-card.html" with context %}
{% endfor %}
```

## Error Pages

Framefox allows you to customize error pages to maintain your application's design consistency even when errors occur. Custom error templates provide better user experience and can include helpful navigation or debugging information in development environments.

:::caution[Error Template Location]
Error templates should be placed in an `errors/` directory and follow the HTTP status code naming convention (404.html, 500.html, etc.).
:::

### 404 Not Found Page

Create user-friendly pages for missing resources:

```html
<!-- errors/404.html -->
{% extends "base.html" %}

{% block title %}Page Not Found{% endblock %}

{% block content %}
<div class="error-page">
    <h1 class="error-code">404</h1>
    <h2>Page Not Found</h2>
    <p>The page you're looking for doesn't exist or has been moved.</p>
    <div class="error-actions">
        <a href="{{ url_for('home.index') }}" class="btn btn-primary">
            Go Home
        </a>
        <a href="javascript:history.back()" class="btn btn-secondary">
            Go Back
        </a>
    </div>
</div>
{% endblock %}
```

### 500 Server Error Page

Handle internal server errors gracefully with optional debug information:

```html
<!-- errors/500.html -->
{% extends "base.html" %}

{% block title %}Server Error{% endblock %}

{% block content %}
<div class="error-page">
    <h1 class="error-code">500</h1>
    <h2>Internal Server Error</h2>
    <p>An unexpected error occurred. Please try again later.</p>
    
    {% if app.debug and error_details %}
    <details class="error-details">
        <summary>Error Details (Debug Mode)</summary>
        <pre>{{ error_details }}</pre>
    </details>
    {% endif %}
    
    <a href="{{ url_for('home.index') }}" class="btn btn-primary">
        Return Home
    </a>
</div>
{% endblock %}
```

## Advanced Template Configuration

Framefox allows you to extend and customize the Jinja2 template engine to add custom functionality that matches your application's specific needs. This includes adding global functions, custom filters, and template tests that can be used throughout your application.

:::tip[Template Extensions]
Register custom template extensions in your application configuration to make them available globally across all templates.
:::

### Custom Global Functions

Add utility functions that can be called from any template:

```python
# config/template_config.py
from jinja2 import Environment
from datetime import datetime

def configure_jinja(env: Environment):
    # Custom global functions
    def format_currency(amount, currency='USD'):
        return f"{currency} {amount:.2f}"
    
    def get_current_year():
        return datetime.now().year
    
    env.globals.update({
        'format_currency': format_currency,
        'current_year': get_current_year
    })
```

### Custom Filters and Tests

Extend Jinja2's functionality with domain-specific filters:

```python
def configure_jinja(env: Environment):
    # Custom filters
    def slugify(text):
        import re
        return re.sub(r'[^\w\s-]', '', text.strip().lower())
    
    # Custom tests
    def is_recent(date_obj, days=7):
        from datetime import timedelta
        return datetime.now() - date_obj < timedelta(days=days)
    
    env.filters['slugify'] = slugify
    env.tests['recent'] = is_recent
```

### Global Template Variables

Provide application-wide context variables:

```python
class TemplateService:
    def get_global_context(self):
        return {
            'app_name': 'My Application',
            'app_version': '1.0.0',
            'navigation_items': [
                {'name': 'Home', 'route': 'home.index'},
                {'name': 'Users', 'route': 'user.index'}
            ]
        }
```

## Performance and Best Practices

Optimizing template performance and following established conventions ensures your Framefox application scales effectively and remains maintainable. These practices cover template organization, caching strategies, and development workflows.

:::tip[Template Performance]
Template caching and asset optimization can significantly improve your application's response times, especially for content-heavy pages.
:::

### Template Organization

Structure your templates logically for easy maintenance and team collaboration:

```
templates/
├── layouts/           # Base templates and layouts
│   ├── app.html      # Main application layout
│   └── admin.html    # Administrative interface layout
├── pages/            # Complete page templates
│   ├── home/
│   └── user/
├── components/       # Reusable UI components
│   ├── navbar.html
│   └── user-card.html
├── macros/           # Jinja2 macros
│   ├── forms.html
│   └── ui.html
└── errors/           # Error page templates
    ├── 404.html
    └── 500.html
```

### Development Best Practices

Follow consistent naming and coding conventions:

```html
<!-- ✅ Good: Descriptive names and clear structure -->
{% extends "layouts/app.html" %}
{% from "macros/ui.html" import button, card %}

{% block content %}
<div class="page-header">
    <h1>{{ page_title }}</h1>
</div>

{% if items %}
    {% for item in items[:10] %}
        {{ card(title=item.name, content=item.description) }}
    {% endfor %}
{% else %}
    {% include "components/empty-state.html" %}
{% endif %}
{% endblock %}
```

### Security and Performance

Implement security best practices and optimize for performance:

```html
<!-- ✅ CSRF protection on forms -->
<form method="POST" action="{{ url_for('user.update', id=user.id) }}">
    {{ csrf_token() }}
    <!-- form fields -->
</form>

<!-- ✅ Proper escaping (automatic by default) -->
<p>User input: {{ user_comment }}</p>

<!-- ✅ Explicit safe only when needed -->
<div class="rich-content">{{ trusted_html_content|safe }}</div>

<!-- ✅ Efficient asset loading -->
<link rel="preload" href="{{ asset('css/critical.css') }}" as="style">
<img src="{{ asset('images/hero.jpg') }}" loading="lazy" alt="Hero">
```

### Debugging Templates

Use debugging features during development:

```html
<!-- Debug information in development -->
{% if app.debug %}
<div class="debug-panel">
    <h4>Template Debug Info</h4>
    <p>Template: {{ self._TemplateReference__context.name }}</p>
    <p>Request: {{ request.method }} {{ request.url.path }}</p>
    {% if current_user %}
        <p>User: {{ current_user.name }} ({{ current_user.id }})</p>
    {% endif %}
</div>
{% endif %}
```


