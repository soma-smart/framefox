<div align="center">

![Framefox Logo](./docs/images/framefox.png)

# 🦊 Framefox
### *Swift, smart, and a bit foxy!*

**The Python web framework that makes development enjoyable and productive**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLModel](https://img.shields.io/badge/SQLModel-0F172A?style=flat&logo=sqlite)](https://sqlmodel.tiangolo.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat&logo=pydantic&logoColor=white)](https://docs.pydantic.dev)
[![GitHub Stars](https://img.shields.io/github/stars/soma-smart/framefox?style=social)](https://github.com/soma-smart/framefox)
[![GitHub Forks](https://img.shields.io/github/forks/soma-smart/framefox?style=social)](https://github.com/soma-smart/framefox)

[🚀 Quick Start](#-quick-start) • 
[📖 Documentation](https://soma-smart.github.io/doc-framefox/) • 
[🎯 Examples](#-examples) • 
[💬 Community](#-community) • 
[🤝 Contributing](#-contributing)

</div>

---

## 🌟 **Why Framefox?**

**Framefox** combines the **speed of FastAPI** with **clean MVC architecture**, **type-safe SQLModel**, **robust Pydantic validation**, and **developer-friendly tooling**. Built for developers who want to ship fast without sacrificing code quality.

### ✨ **What makes it special?**

🎯 **MVC Architecture** - Clean separation with Controllers, Templates, and Repositories  
🏗️ **Interactive CLI** - Generate components instantly with `framefox create`  
⚡ **FastAPI Foundation** - Built on FastAPI with async support out of the box  
🗄️ **SQLModel Integration** - Type-safe database models with automatic validation  
📋 **Pydantic Validation** - Robust data validation and serialization everywhere  
🔒 **Security First** - CSRF protection, XSS prevention, and secure authentication  
🧠 **Developer Friendly** - Jinja2 templates, hot reload, and comprehensive debugging  
📱 **Modern Stack** - Python 3.9+, async/await, dependency injection everywhere  

---
![Demo](./docs/images/demo.gif)

## 🚀 **Quick Start**

Get a full web application running in **30 seconds**:

```bash
# Install Framefox
pip install framefox

# Init your project
framefox init

# Start developing
framefox run
```

**That's it!** 🎉 Your app is running on `http://localhost:8000`

![Demo](./docs/images/start.png)
---

## 🎯 **Examples**

### 💨 **Controllers with Routes**
```python
from framefox.core.routing.decorator.route import Route
from framefox.core.controller.abstract_controller import AbstractController

class UserController(AbstractController):
    
    @Route("/users", "user.index", methods=["GET"])
    async def index(self):
        users = await self.user_repository.find_all()
        return self.render("user/index.html", {"users": users})
    
    @Route("/users/{id}", "user.show", methods=["GET"])
    async def show(self, id: int):
        user = await self.user_repository.find(id)
        return self.render("user/show.html", {"user": user})
```

### 🎨 **Jinja2 Templates with Built-in Functions**
```html
<!-- templates/user/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Users</title>
    <link href="{{ asset('css/app.css') }}" rel="stylesheet">
</head>
<body>
    <h1>Users</h1>
    
    {% for user in users %}
        <div class="user-card">
            <h3>{{ user.name }}</h3>
            <a href="{{ url_for('user.show', id=user.id) }}">View Profile</a>
        </div>
    {% endfor %}
    
    <!-- CSRF Protection -->
    <form method="POST">
        {{ csrf_token() }}
        <button type="submit">Action</button>
    </form>
</body>
</html>
```


## 🏗️ **Architecture That Scales**

```
my-project/
├── src/
│   ├── 🎮 controllers/     # Handle HTTP requests and business logic
│   ├── 🏛️ entity/          # Database models and entities  
│   ├── 📝 form/           # Form types and validation
│   └── 🗄️ repository/     # Data access layer
├── 🎨 templates/          # Jinja2 templates with template inheritance
├── ⚙️ config/             # YAML configuration files
├── 🌐 public/            # Static assets (CSS, JS, images)
└── 📋 main.py            # Application entry point
```

**Clean MVC separation** means your code stays **maintainable** as your team and project grow.



## 🔥 **Core Features**

<table>
<tr>
<td width="50%">

### 🚄 **Performance**
- FastAPI foundation
- Async/await support
- Built-in template caching
- Dependency injection container
- Repository pattern for data access

### 🛡️ **Security**
- CSRF token generation
- XSS prevention in templates
- Secure session management
- User authentication system
- Role-based access control

</td>
<td width="50%">

### 🧰 **Developer Experience**
- Interactive CLI commands
- Component generators
- Hot reload development server
- Comprehensive error pages
- Built-in profiler and debugger

### 🗃️ **Database & ORM**
- SQLModel integration for type safety
- Pydantic validation everywhere
- Entity-Repository pattern
- Database migrations with Alembic
- Relationship mapping
- Query builder integration
- Multi-database support

</td>
</tr>
</table>

---

## 🛠️ **Interactive CLI**

Framefox includes a powerful CLI for rapid development:

```bash
# Generate components instantly
framefox create controller
framefox create entity
framefox create crud       # Full CRUD with templates

# Database management
framefox database create-migration
framefox database upgrade

# Development tools
framefox server              # Start development server
framefox debug router       # List all routes
framefox cache clear        # Clear application cache

```

---

## 🎨 **Template System**

Framefox uses **Jinja2** with powerful built-in functions:

### 🔧 **Built-in Template Functions**
- `{{ url_for('route.name', param=value) }}` - Generate URLs from route names
- `{{ asset('path/file.css') }}` - Asset management with versioning
- `{{ csrf_token() }}` - CSRF protection
- `{{ current_user }}` - Access authenticated user
- `{{ get_flash_messages() }}` - Session-based notifications

### 🏗️ **Template Inheritance**
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My App{% endblock %}</title>
    <link href="{{ asset('css/app.css') }}" rel="stylesheet">
</head>
<body>
    <nav>
        <!-- Navigation with authentication -->
        {% if current_user %}
            <span>Welcome, {{ current_user.name }}!</span>
        {% endif %}
    </nav>
    
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

---

## 🔧 **Dependency Injection**

Framefox features a powerful dependency injection system:

```yaml
# config/services.yaml
services:
  user_manager:
    class: src.service.user.user_manager.UserManager
    arguments:
      - "@entity_manager"
      - "@mailer"
      - "@security.password_encoder"
```

```python
# Automatic injection in controllers
class UserController(AbstractController):
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager
```

## 📚 **Learn More**

| 📖 **Resource**                                                                      | 🎯 **Perfect For**               |
| ----------------------------------------------------------------------------------- | ------------------------------- |
| [📋 Installation Guide](https://soma-smart.github.io/doc-framefox/docs/installation) | Getting up and running          |
| [🎮 Controllers Guide](https://soma-smart.github.io/doc-framefox/docs/controllers)   | Building your application logic |
| [🎨 Templates Guide](https://soma-smart.github.io/doc-framefox/docs/templates)       | Creating beautiful views        |
| [🔐 Security Guide](https://soma-smart.github.io/doc-framefox/docs/security)         | Securing your application       |
| [🧪 Testing Guide](https://soma-smart.github.io/doc-framefox/docs/testing)           | Writing comprehensive tests     |
| [🚀 Deployment Guide](https://soma-smart.github.io/doc-framefox/docs/deployment)     | Going to production             |



## 💬 **Community**

<div align="center">

[![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/framefox)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/framefox_py)
[![Stack Overflow](https://img.shields.io/badge/Stack_Overflow-FE7A16?style=for-the-badge&logo=stack-overflow&logoColor=white)](https://stackoverflow.com/questions/tagged/framefox)

**Join developers building amazing applications with Framefox**

</div>

- 💬 **Get help** on [Discord](https://discord.gg/framefox)
- 🐦 **Follow updates** on [Twitter](https://twitter.com/framefox_py)  
- 🔧 **Report issues** on [GitHub Issues](https://github.com/soma-smart/framefox/issues)
- 📖 **Read the docs** at [soma-smart.github.io](https://soma-smart.github.io/doc-framefox/)

---

## 🤝 **Contributing**

We ❤️ contributors! Here's how you can help:

### 🆕 **For New Contributors**
1. 🍴 Fork the repository
2. 🌿 Create a feature branch: `git checkout -b feature/amazing-feature`
3. 💾 Commit your changes: `git commit -m 'Add amazing feature'`
4. 📤 Push to the branch: `git push origin feature/amazing-feature`
5. 🔄 Open a Pull Request

### 🎯 **Good First Issues**
- 📝 Improve documentation
- 🐛 Fix small bugs
- ✨ Add examples
- 🧪 Write tests

**Example**: [Add comprehensive logging documentation with examples](https://github.com/soma-smart/framefox/issues/161)

[**View Good First Issues →**](https://github.com/soma-smart/framefox/labels/good%20first%20issue)

---

## 🏆 **Support the Project**

If Framefox helps you build amazing things:

⭐ **Star this repository**  
🐦 **Tweet about it**  
📝 **Write a blog post**  
🔗 **Share with friends**  

Your support means the world to us! 🙏

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](./LICENSE) file for details.

---

## 👥 **Core Team**

<div align="center">

### 🏢 **Backed by SOMA Smart**

[![SOMA Smart](https://img.shields.io/badge/Backed%20by-SOMA%20Smart-00D4AA?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMSA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDMgOUwxMC45MSA4LjI2TDEyIDJaIiBmaWxsPSJ3aGl0ZSIvPgo8L3N2Zz4K)](https://soma-smart.com)

*Framefox is proudly backed by **SOMA Smart**, a technology company focused on data transformation and building innovative development tools.*

| ![Rayen](https://github.com/RayenBou.png?size=100) | ![Raphaël](https://github.com/Vasulvius.png?size=100) |
| :------------------------------------------------: | :---------------------------------------------------: |
|  **[Rayen BOUMAZA](https://github.com/RayenBou)**  |  **[Raphaël LEUROND](https://github.com/Vasulvius)**  |
|               *Framework Architect*                |                   *Core Developer*                    |
|            🏗️ Architecture & Performance            |                   🔧 Features & DevX                   |

---

### 🌟 **About SOMA Smart**

**SOMA Smart** is committed to **empowering developers** with cutting-edge tools and frameworks. Framefox represents our vision of making Python web development more **productive**, **secure**, and **enjoyable**.

- 🚀 **Innovation-driven** development approach
- 🔧 **Open-source** commitment and community focus  
- 🌍 **Global** team of passionate developers
- 📈 **Long-term** support and continuous improvement

[**Learn more about SOMA Smart →**](https://soma-smart.com)

</div>
---

<div align="center">

### 🦊 **Swift, smart, and a bit foxy!**

**Framefox makes Python web development enjoyable and productive.**

⭐ **[Star us on GitHub](https://github.com/soma-smart/framefox)** ⭐

</div>