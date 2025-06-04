# Contributing to Framefox

Thank you for your interest in contributing to Framefox! This guide will help you understand how to participate in the development of our modern Python web framework.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Pull Request Process](#pull-request-process)
- [Project Structure](#project-structure)

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct. Be respectful, inclusive, and constructive in all your interactions.

## Getting Started

Before contributing, please:

1. Read this entire contributing guide
<!-- 2. Check the [existing issues](../../issues) and [pull requests](../../pulls) -->
1. Check the existing issues and pull requests
2. Familiarize yourself with the project structure and architecture

## How to Contribute

There are several ways to contribute to Framefox:

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Fix bugs
- ✨ Implement new features
- 🧪 Write tests
- 🌐 Improve translations
- 📖 Update examples and tutorials

## Reporting Bugs

Before reporting a bug:

<!-- 1. Check that the bug hasn't already been reported in [Issues](../../issues) -->
1. Check that the bug hasn't already been reported
2. Ensure you're using the latest version of Framefox
3. Test with a minimal reproduction case

**Bug Report Template:**

```markdown
## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
A clear description of what actually happened.

## Environment
- OS: [e.g. Ubuntu 22.04, Windows 11, macOS 13]
- Python version: [e.g. 3.9.0]
- Framefox version: [e.g. 1.0.0]
- Browser (if applicable): [e.g. chrome, safari]

## Additional Context
Add any other context about the problem here.
```

## Suggesting Features

For new feature suggestions:

<!-- 1. Check if it's not already proposed in [Issues](../../issues) -->
1. Check if it's not already proposed
2. Create a new issue with the "enhancement" label
3. Clearly describe:
   - The problem this feature solves
   - The proposed solution
   - Alternatives you've considered
   - Additional context

## Development Setup

### Prerequisites

- Python 3.12+
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Instructions

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/framefox.git
cd framefox

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install Framefox in development mode
pip install -e .

# Run tests to verify setup
python -m pytest
```

### Running the Development Server

```bash
# Navigate to the docs example
cd docs/framefox

# Install documentation dependencies
npm install

# Start the development server
npm run dev
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run tests with coverage
python -m pytest --cov=framefox

# Run specific test file
python -m pytest tests/test_controllers.py
```

## Code Standards

### Python Code Style

- Follow [PEP 8](https://pep8.org/) conventions
- Use [Black](https://black.readthedocs.io/) for code formatting (140 character line limit)
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Write descriptive variable and function names
- Comment complex code sections
- Write docstrings for all public functions and classes

### Git Workflow

- **Branch per feature**: Create a new branch for each feature/fix
- **Conventional commits**: Use conventional commit format
- **No direct commits to main**: All changes must go through Pull Requests
- **Clean history**: Keep git history clean and meaningful

### Branch Naming Convention

We follow the [Conventional Branch](https://conventional-branch.github.io/) specification:

```
<type>/<description>
```

**Branch Types:**
- `feature/` - For new features (e.g., `feature/add-new-orm-feature`)
- `bugfix/` - For bug fixes (e.g., `bugfix/resolve-routing-bug`)
- `hotfix/` - For urgent fixes (e.g., `hotfix/security-patch`)
- `chore/` - For non-code tasks (e.g., `chore/update-dependencies`)

**Naming Rules:**
- Use lowercase letters, numbers, and hyphens only
- Keep descriptions clear and concise
- Include ticket numbers when applicable (e.g., `feature/issue-123-new-login`)
- No consecutive or trailing hyphens

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Examples:
```bash
feat(orm): add support for JSON columns
fix(routing): resolve parameter parsing bug
docs: update installation instructions
refactor(container): improve service injection
test: add unit tests for form validation
```

### Code Quality Tools

We use automated tools to maintain code quality and consistency across the project:

```bash
# Install pre-commit hooks (run once after cloning)
pre-commit install

# Format code (140 character limit)
black --line-length 140 .

# Sort imports
isort .

# Lint code
flake8

# Run pre-commit manually on all files
pre-8
```

**Pre-commit hooks** automatically run these quality checks before each commit, ensuring consistent code style and catching issues early. The hooks will:

- Format code with Black
- Sort imports with isort  
- Lint code with flake8
- Check for common issues (trailing whitespace, large files, etc.)

If any pre-commit hook fails, the commit will be rejected. Fix the issues and try committing again.

## Pull Request Process

### Before Creating a Pull Request

1. **Fork** the repository on GitHub
   > **Why fork?** Since you don't have write access to the main repository, you need to create your own copy (fork) where you can push your changes before creating a Pull Request.

2. **Clone your fork** to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/framefox.git
   cd framefox
   ```
3. **Create a feature branch** from `main` following the [branch naming convention](#branch-naming-convention):
   ```bash
   git checkout -b feature/your-feature-description
   # or
   git checkout -b bugfix/fix-specific-issue
   ```
4. **Make your changes** following the coding standards
5. **Add tests** for new functionality
6. **Update documentation** if necessary
7. **Run the test suite** and ensure all tests pass
8. **Run code quality tools**

### Creating the Pull Request

1. **Push** your branch to your fork:
   ```bash
   git push origin feature/your-feature-description
   ```
2. **Create a Pull Request** on GitHub from your fork to the main repository
3. **Fill out the PR template** completely
4. **Link any related issues**

### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Changes Made
- List the specific changes made
- Include any new files created
- Mention any files deleted or moved

## Testing
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] I have tested this change manually

## Documentation
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Related Issues
Fixes #(issue number)
```

### Review Process

- All PRs require review from at least one maintainer
- Address feedback promptly and respectfully
- Keep discussions focused on the code and technical aspects
- Be prepared to make changes based on feedback

## Project Structure

Understanding the Framefox project structure:

```
framefox/
├── framefox/                    # Core framework library
│   ├── core/                    # Core framework components
│   │   ├── bundle/              # Bundle management and configuration
│   │   ├── config/              # Configuration handling and parsing
│   │   ├── controller/          # Base controller and routing system
│   │   ├── debug/               # Debug tools and profiler
│   │   ├── di/                  # Dependency injection container
│   │   ├── events/              # Event dispatcher system
│   │   ├── file/                # File handling and upload utilities
│   │   ├── form/                # Form creation and validation
│   │   ├── logging/             # Logging system and handlers
│   │   ├── mail/                # Email sending and templating
│   │   ├── middleware/          # HTTP middleware components
│   │   ├── orm/                 # ORM implementation (entities, repositories)
│   │   ├── request/             # HTTP request handling and parsing
│   │   ├── routing/             # Route decorators and URL handling
│   │   ├── security/            # Authentication, authorization, CSRF
│   │   ├── task/                # Background task management
│   │   └── templates/           # Template engine integration (Jinja2)
│   ├── terminal/                # CLI commands and generators
│   │   ├── commands/            # Individual CLI commands
│   │   ├── common/              # Common terminal utilities
│   │   ├── templates/           # Code generation templates
│   │   ├── typer_config/        # Typer CLI configuration
│   │   ├── ui/                  # Terminal UI components
│   │   └── utils/               # Terminal utility functions
│   └── tests/                   # Framework test suite
├── docs/                        # Documentation website
│   └── framefox/                # Astro-based documentation
└── pyproject.toml               # Package configuration and dependencies
```

### Key Framework Components

When contributing to Framefox, understanding these core components is essential:

- **Controllers**: Base classes for handling HTTP requests with MVC pattern
- **ORM**: Entity management, repository pattern, and database abstraction
- **Routing**: Decorator-based route registration and URL parameter handling
- **Security**: CSRF protection, authentication, and authorization middleware
- **Forms**: Form creation, validation, and rendering system
- **Services**: Dependency injection container following SOLID principles
- **Terminal**: CLI commands for scaffolding and project management
- **Templates**: Jinja2 integration with framework-specific helpers

### Generated Project Structure

When developers use `framefox init`, the framework generates this structure:

```
user-project/
├── src/
│   ├── controllers/       # User application controllers
│   ├── entity/            # Database entities (models)
│   ├── repository/        # Custom repository classes
│   └── services/          # User-defined services
├── config/                # Application configuration
├── public/                # Static assets
├── migrations/            # Database migrations
├── templates/             # Jinja2 templates
├── var/                   # Variable data (logs, cache)
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── main.py                # Application entry point
```

## Development Guidelines

### Adding New Features

1. **Design first**: Discuss the feature in an issue before implementing
2. **Follow SOLID principles**: Ensure single responsibility, open/closed, and dependency inversion
3. **Implement Clean Code practices**: Meaningful names, small functions, clear abstractions
4. **Start with interfaces**: Define abstract base classes for new components
5. **Write tests first**: Use TDD approach for new functionality
6. **Document thoroughly**: Update docstrings, README, and user documentation
7. **Provide examples**: Add usage examples in the docs and test cases

### Framework Design Principles

- **Convention over Configuration**: Provide sensible defaults while allowing customization
- **MVC Architecture**: Maintain clear separation between models, views, and controllers
- **Dependency Injection**: Use the service container for loose coupling
- **Decorator Pattern**: Leverage Python decorators for clean, declarative syntax
- **Repository Pattern**: Abstract data access through repository interfaces

### Performance Considerations

Since Framefox is a library that developers will use to build production applications, performance is critical:

#### Framework-Level Optimizations

- **Lazy Loading**: Import heavy dependencies only when needed
- **Caching**: Implement intelligent caching for route resolution, service definitions, and ORM metadata
- **Memory Management**: Avoid memory leaks in long-running applications
- **Async Support**: Ensure all I/O operations support async/await patterns
- **Minimal Overhead**: Keep framework overhead as low as possible

#### Code Performance Guidelines

```python
# ✅ Good: Lazy imports
def get_database_connection():
    from framefox.core.orm import DatabaseManager
    return DatabaseManager.get_connection()

# ❌ Bad: Heavy imports at module level
from some_heavy_library import ExpensiveClass

# ✅ Good: Use __slots__ for performance-critical classes
class Entity:
    __slots__ = ['id', 'created_at', 'updated_at']

# ✅ Good: Cache expensive operations
@lru_cache(maxsize=128)
def parse_route_pattern(pattern: str):
    return compiled_pattern
```

#### Database Performance

- **Query Optimization**: Ensure ORM generates efficient SQL queries
- **Connection Pooling**: Implement proper database connection management
- **Lazy Loading**: Load related entities only when accessed
- **Batch Operations**: Support bulk inserts and updates

### Security Considerations

- Validate all user inputs
- Use parameterized queries to prevent SQL injection
- Handle sensitive data appropriately
  
#### Security Checklist for Contributors

- [ ] **Input validation**: All user inputs are validated and sanitized
- [ ] **SQL injection**: Use parameterized queries or ORM methods
- [ ] **XSS prevention**: Template engine auto-escapes output by default
- [ ] **Authorization**: Proper permission checks for protected resources
- [ ] **Error handling**: Don't expose sensitive information in error messages
- [ ] **Dependencies**: Keep third-party dependencies updated and secure

#### Responsible Disclosure

If you discover a security vulnerability:

1. **Don't create a public issue** for security vulnerabilities
2. **Email the maintainers** directly with details
3. **Wait for acknowledgment** before discussing publicly
4. **Allow time for fixes** before any public disclosure

## Getting Help

- **Documentation**: Check the [official documentation](https://soma-smart.github.io/doc-framefox/)
- **Issues**: Search existing [issues](../../issues) for similar problems
- **Discussions**: Use GitHub Discussions for questions and ideas

## Recognition

Contributors will be recognized in:
- The project's README
- Release notes for significant contributions
- The project's documentation

Thank you for contributing to Framefox! 🦊

---

**Swift, smart, and a bit foxy!** - Framefox makes Python web development enjoyable and productive.