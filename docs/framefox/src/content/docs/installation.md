---
title: Installation and Configuration
description: Complete guide to install and configure Framefox
---

# Installation and Configuration

## Prerequisites

Before installing Framefox, make sure you have:

- **Python 3.12+** installed on your system
- **pip** (Python package manager)
- A code editor (VS Code, Vim, etc.)

## Installation via pip

The simplest way to install Framefox:

```bash
pip install framefox
```
### Installation in a virtual environment (recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install Framefox
pip install framefox
```

### Installation with uv (faster)

If you have [uv](https://docs.astral.sh/uv/) installed, you can use it for faster installation:

```bash
# Direct installation
uv pip install framefox

# Or in a virtual environment
uv venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
uv pip install framefox
```

## Create a new project

Once Framefox is installed, create your first project:

```bash
# Create the project folder
mkdir my-first-project
cd my-first-project

# Initialize the Framefox project
framefox init
```

This command will automatically create the basic structure:

```
user-project/
├── src/
│   ├── controllers/       # User application controllers
│   ├── entity/            # Database entities (models)
│   └── repository/        # Custom repository classes
├── config/                # Application configuration
│   ├── application.yaml   # Main application configuration
│   ├── debug.yaml         # Debug configuration
│   ├── mail.yaml          # Email configuration
│   ├── orm.yaml           # ORM configuration
│   ├── parameter.yaml     # Application parameters
│   ├── security.yaml      # Security configuration
│   ├── services.yaml      # Services configuration
│   └── tasks.yaml         # Tasks configuration
├── public/                # Static assets
├── migrations/            # Database migrations
├── templates/             # Jinja2 templates
├── var/                   # Variable data (logs, cache)
├── .env                   # Environment variables
├── requirements.txt       # Python dependencies
└── main.py                # Application entry point
```

## Basic configuration

### Application configuration

```yaml
# config/application.yaml
application:
  env: "${APP_ENV}"
  template_dir: "templates"
  openapi_url: /openapi.json #empty value to disable openapi swagger ui
  redoc_url: /redoc

  controllers:
    dir: "src/controllers/"
  profiler:
    enabled: true # Set to false in production
  cors:
    allow_origins:
      - "http://localhost"
      - "http://localhost:8000"
    allow_credentials: true
    allow_methods:
      - "*"
    allow_headers:
      - "*"

  session:
    name: "session_id"
    file_path: var/session/sessions.db
    secret_key: "${SESSION_SECRET_KEY}"

  cookie:
    max_age: 3600 # 1 hour
    secure: true
    http_only: true
    same_site: "strict" # "strict", "lax", "none"
    path: "/"
```

**Parameter descriptions:**
- `env`: Runtime environment (dev, prod, test)
- `template_dir`: Jinja2 templates directory
- `openapi_url` / `redoc_url`: URLs for automatic API documentation
- `controllers.dir`: Application controllers directory
- `profiler.enabled`: Enable/disable performance profiler
- `cors`: CORS configuration for APIs
- `session`: User session management parameters
- `cookie`: Security cookie configuration

### ORM Configuration

```yaml
# config/services.yaml
database:
  # You can use either the URL format or the detailed configuration
  # If both are provided, DATABASE_URL environment variable takes precedence,
  # followed by the url field here, and finally the detailed configuration.
  
  # Option 1: Database URL 
  url: "${DATABASE_URL}" 
  
  # Option 2: Detailed configuration (useful for Docker/Kubernetes)
  # Uncomment and adjust these settings if needed, they will be used
  # only if no url is specified above or in environment variables
  # driver: "${DATABASE_DRIVER:-postgresql}"
  # host: "${DATABASE_HOST:-localhost}"
  # port: "${DATABASE_PORT:-5432}"
  # username: "${DATABASE_USER:-framefox}"
  # password: "${DATABASE_PASSWORD}"
  # database: "${DATABASE_NAME:-framefoxdb}"
  # charset: "utf8mb4"
  
  # Connection pooling settings (important for production)
  pool_size: 20
  max_overflow: 10
  pool_timeout: 30
  pool_recycle: 1800
  pool_pre_ping: true
  autocommit: false
  autoflush: false
```

**Parameter descriptions:**
- `url`: Database connection URL
- `pool_size`: Number of connections in the pool
- `max_overflow`: Additional connections allowed
- `pool_timeout`: Timeout to obtain a connection
- `pool_recycle`: Connection lifetime (seconds)
- `pool_pre_ping`: Connection verification before use
- `autocommit/autoflush`: Automatic transaction management

### Debug configuration

```yaml
# config/debug.yaml
debug:
  profiler:
    enabled: true # Enable the profiler
    max_files: 1000 # Maximum number of profile files per day
    retention_days: 7 # Number of days to retain profiles
    sampling_rate: 1.0 # Percentage of requests to profile (0.0 to 1.0)
    max_memory: 50 # Maximum profiles in memory
  logging:
    level: "DEBUG" # Log level when dev (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    file_path: "var/log/app.log"
    max_size: 10 # Maximum file size
    backup_count: 5 # Number of backup files
```

**Parameter descriptions:**
- `profiler.enabled`: Enable performance profiler
- `max_files`: Maximum number of profile files per day
- `retention_days`: Profile retention period
- `sampling_rate`: Percentage of requests to profile
- `logging.level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `file_path`: Log file path
- `max_size`: Maximum log file size (MB)

### Email configuration

```yaml
# config/mail.yaml
mail:
  url: "${MAIL_URL}"
  templates_dir: "templates/emails"
  queue:
    enabled: true
    max_size: 100
    retry_interval: 300
    max_retries: 3
```

**Parameter descriptions:**
- `url`: SMTP connection URL (format: smtp://user:pass@host:port)
- `templates_dir`: Email templates directory
- `queue.enabled`: Enable email queue
- `max_size`: Maximum queue size
- `retry_interval`: Delay between attempts (seconds)
- `max_retries`: Maximum number of sending attempts

### Security configuration

```yaml
# config/security.yaml
security:
  providers:

  firewalls:

  access_control:
    # Access control rules define which roles have access to specific paths.
    # Each rule consists of a path pattern and the roles that are allowed to access it.

    # Example:
    # - { path: ^/admin, roles: ROLE_ADMIN }  # Only users with ROLE_ADMIN can access  paths starting with /admin
    # - { path: ^/profile, roles: ROLE_USER }  # Only users with ROLE_USER can access paths starting with /profile

    - { path: ^/users, roles: ROLE_USER }
    - { path: ^/products, roles: ROLE_ADMIN }
    # - { path: ^/test2, roles: ROLE_USER }
    # - { path: ^/test3, roles: ROLE_ADMIN }
```

**Parameter descriptions:**
- `providers`: Authentication providers (database, LDAP, etc.)
- `firewalls`: Firewall rules for different sections
- `access_control`: Access rules based on roles and paths
- Each rule defines a path pattern and allowed roles

### Services configuration

```yaml
# config/services.yaml
services:
  _defaults:
    autowire: true
    autoconfigure: true
```

**Parameter descriptions:**
- `_defaults.autowire`: Automatic dependency injection
- `_defaults.autoconfigure`: Automatic service configuration
- This configuration enables automatic dependency injection for all services

### Tasks configuration

```yaml
# config/tasks.yaml
tasks:
  # Worker configuration
  type: database # Worker type (can be 'database', 'rabbitmq')
  # Transport URL for RabbitMQ (used when type is 'rabbitmq')
  task_transport_url: ${RABBITMQ_URL}

  worker:
    concurrency: 5 # Number of simultaneous tasks
    polling_interval: 5 # Polling interval (seconds)
    default_queues: # Default queues
      - default

  # Automatic cleanup configuration
  cleanup:
    interval_hours: 24 # Cleanup interval (hours)
    retention_days: 7 # Retention period for failed tasks (days)

  # Default parameters for tasks
  defaults:
    queue: default # Default queue
    priority: 0 # Default priority (0 = normal)
    max_retries: 3 # Maximum number of retries
    retry_delay: 300 # Delay between retries (seconds)
```

**Parameter descriptions:**
- `type`: Worker type (database or rabbitmq)
- `worker.concurrency`: Number of simultaneous tasks
- `polling_interval`: Task checking interval
- `cleanup`: Automatic cleanup configuration
- `defaults`: Default parameters for all tasks
- `max_retries`: Maximum number of attempts on failure

### Parameters configuration

```yaml
# config/parameter.yaml
parameters:
# create your own parameters here by creating as many key as you want.
# to refer to the parameter in your application, use the Settings class and call the get_param method
# custom_variables:
#   api_key: "${API_KEY}"
#   base_url: "${BASE_URL}"
#   max_retries: "${MAX_RETRIES}"
#   timeout: "${TIMEOUT}"
```

**Description:**
- This file allows you to define custom parameters for the application
- Parameters can use environment variables
- Accessible via the `Settings` class and the `get_param()` method
- Useful for centralizing application configuration

## Installation verification

Start the development server:

```bash
framefox server start

# Output example:
# Starting the server on port 8000
# INFO:     Will watch for changes in these directories: ['/my_project']
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [16768] using StatReload
```

Visit `http://localhost:8000` in your browser. You should see the default Framefox homepage!

## Advanced configuration

### Environment variables

```env
# .env
#==============================
# App environment
#==============================

APP_ENV=dev # can be dev or prod
SESSION_SECRET_KEY=your-very-secret-key


#==============================
# Database
#==============================

# uncomment the line you want below, to use the database you want
DATABASE_URL=sqlite:///app.db
# DATABASE_URL=postgresql://root:password@localhost:5432/dbname
# DATABASE_URL=mysql://root:password@localhost:3306/dbname

#==============================
# Mail
#==============================
# MAIL_URL=smtp://username:password@host:port?tls=true

#==============================
# Task transport
#==============================
# RABBITMQ_URL=amqp://guest:guest@localhost:5672/%2F
```

**Variable descriptions:**

- `APP_ENV`: Runtime environment (dev/prod)
- `SESSION_SECRET_KEY`: Session encryption key
- `DATABASE_URL`: Database connection URL (SQLite by default)
- `MAIL_URL`: SMTP configuration for emails (optional)
- `RABBITMQ_URL`: RabbitMQ URL for asynchronous tasks (optional)
- You can add any parameter. You'll also need to add it to config/parameters.yaml

**Note:** This file should never be committed as it contains sensitive information.

### Database configuration

To use MySQL or PostgreSQL, simply add the connection URL in the .env file
  
Example for MySQL:  
```env
# .env
# ...existing code...

#==============================
# Database
#==============================

DATABASE_URL=mysql://root:password@localhost:3306/dbname

# ...existing code...
```
  
Example for PostgreSQL:  
```env
# .env
# ...existing code...

#==============================
# Database
#==============================

DATABASE_URL=postgresql://root:password@localhost:5432/dbname

# ...existing code...
```

## Useful commands

Once your project is configured, here are the main commands:

```bash
# Start the development server
framefox server start

# Start the server without automatically opening a browser
framefox server start --no-browser

# Create an entity
framefox create entity

# Create a controller
framefox create controller

# Manage the database
framefox database create
framefox database create-migration
framefox database upgrade

# List routes
framefox debug router
```

## Next steps

- [Create your first controller](/docs/controllers)
- [Configure the database](/docs/database)
- [Routing system](/docs/routing)
