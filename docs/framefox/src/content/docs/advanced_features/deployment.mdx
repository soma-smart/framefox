---
title: Deployment
description: Deploy your Framefox application in production
---

This guide shows you how to deploy your Framefox application in production, using different methods and platforms.

## Deployment preparation

Before deploying your application, you must ensure it is ready for production:

### Environment configuration

Framefox uses environment variables to distinguish between development and production environments. Configure your application according to the environment in `config/application.yaml`:

```yaml
# config/application.yaml
application:
  env: "${APP_ENV}" # Can be dev or prod
  template_dir: "templates"
  openapi_url: /openapi.json #empty value to disable openapi swagger ui
  redoc_url: /redoc

  controller:
    dir: "src/controller/"
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

### Application verification

Before deployment, ensure your application is configured correctly:

```bash
# Check that the application starts without error
python main.py

# Test main routes
curl http://localhost:8000/

# Check required configuration files
ls config/

# Check application configuration
framefox debug config

# Optimize application for production
framefox cache clear
framefox cache warmup
```

### Production configuration

Modify your `config/application.yaml` for production:

```yaml
# config/application.yaml
application:
  env: "${APP_ENV}"
  debug: false
  
  controller:
    dir: "src/controller/"
    
  profiler:
    enabled: false # Disabled in production
    
  cors:
    allow_origins:
      - "https://your-domain.com"
    allow_credentials: true
    allow_methods:
      - "GET"
      - "POST"
      - "PUT"
      - "DELETE"
    allow_headers:
      - "*"

  session:
    name: "session_id"
    file_path: "var/session/sessions.db"
    secret_key: "${SESSION_SECRET_KEY}"

  cookie:
    max_age: 3600
    secure: true
    http_only: true
    same_site: "strict"
    path: "/"
```

```.env
# .env
export APP_ENV=prod
export SESSION_SECRET_KEY="your-generated-secret-key"
```

## Deployment best practices

### 1. Production profiler configuration

The Framefox profiler must be disabled in production for performance and security reasons:

```yaml
# config/application.yaml
application:
  profiler:
    enabled: false # MANDATORY in production
```

**Important**: The profiler exposes sensitive information via `/_profiler/` and can impact performance.

### 2. Log management

Framefox uses Python's standard logging system. Configure it according to your needs:

```python
# In your application
import logging

# Simple configuration for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('var/log/app.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Service cache optimization

Use Framefox cache commands:

```bash
# Clear cache before deployment
framefox cache clear

# Warm up cache after deployment
framefox cache warmup
```

These commands optimize Framefox's [`ServiceContainer`](framefox/core/di/service_container.py).

### 4. Security environment variables

Configure sensitive variables correctly:

```bash
# Mandatory variables
export APP_ENV=prod
export SESSION_SECRET_KEY="your-very-secure-32-character-minimum-key"

# Optional variables depending on your configuration
export DATABASE_URL="postgresql://user:password@localhost/db"
```

### 5. Production CORS configuration

Restrict allowed origins:

```yaml
# config/application.yaml
application:
  cors:
    allow_origins:
      - "https://your-domain.com"
      - "https://www.your-domain.com"
    allow_credentials: true
    allow_methods:
      - "GET"
      - "POST"
      - "PUT"
      - "DELETE"
    allow_headers:
      - "Content-Type"
      - "Authorization"
```

### 6. Session cookie security

```yaml
# config/application.yaml
application:
  cookie:
    max_age: 3600
    secure: true      # HTTPS only
    http_only: true   # No JavaScript access
    same_site: "strict"
    path: "/"
```

### 7. Basic monitoring

Create a simple health endpoint:

```python
# src/controller/health_controller.py
from framefox.core.controller.controller import Controller
from framefox.core.routing.decorators import route

class HealthController(Controller):
    
    @route("/health", methods=["GET"])
    def health_check(self):
        return {
            "status": "ok",
            "service": "framefox",
            "timestamp": self.get_current_datetime().isoformat()
        }
    
    @route("/health/ready", methods=["GET"])  
    def readiness_check(self):
        # More advanced checks if necessary
        return {"status": "ready"}
```

## Deployment checklist

Before deploying your Framefox application in production, check the following points:

1. **Production environment configured** (`APP_ENV=prod`)
2. **Profiler disabled** (`profiler.enabled: false`)
3. **Sensitive variables configured as environment variables** (SESSION_SECRET_KEY, etc.)
4. **CORS configured for your production domain**
5. **Secure cookies enabled** (`secure: true`, `http_only: true`)
6. **SSL certificates installed** (for HTTPS)
7. **Cache optimized** (`framefox cache clear` then `framefox cache warmup`)
8. **Application tested locally** (`python main.py`)
9. **Production server configured** (Gunicorn + Uvicorn)
10. **Log directories created** (if necessary)
11. **File permissions checked**
12. **Database configuration** (if used)

## Deployment strategies

### Simple deployment

The most basic deployment consists of:

```bash
# 1. Prepare environment
export APP_ENV=prod
export SESSION_SECRET_KEY="your-secure-secret-key"

# 2. Optimize cache
framefox cache clear
framefox cache warmup

# 3. Start application
gunicorn -c gunicorn.conf.py main:app
```

### Docker deployment

```bash
# Build image
docker build -t my-framefox-app .

# Start container
docker run -d \
  -p 8000:8000 \
  -e APP_ENV=prod \
  -e SESSION_SECRET_KEY="your-secret-key" \
  --name framefox-app \
  my-framefox-app
```

### CI/CD deployment

Simplified GitHub Actions configuration example:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Test application startup
        run: |
          export APP_ENV=dev
          timeout 10s python main.py || true
          
      - name: Deploy to Heroku
        uses: akhileshns/heroku-deploy@v3.12.14
        with:
          heroku_api_key: ${{secrets.HEROKU_API_KEY}}
          heroku_app_name: "my-framefox-app"
          heroku_email: ${{secrets.HEROKU_EMAIL}}
```

### Automated deployment script

```bash
#!/bin/bash
# deploy.sh

set -e  # Stop on error

echo "🚀 Deploying Framefox application..."

# Preliminary checks
echo "📋 Preliminary checks..."

# Check that environment is defined
if [ -z "$APP_ENV" ]; then
  echo "❌ APP_ENV variable not defined"
  exit 1
fi

if [ -z "$SESSION_SECRET_KEY" ]; then
  echo "❌ SESSION_SECRET_KEY variable not defined"
  exit 1
fi

# Check that necessary files exist
if [ ! -f "main.py" ]; then
  echo "❌ main.py file not found"
  exit 1
fi

if [ ! -f "config/application.yaml" ]; then
  echo "❌ config/application.yaml file not found"
  exit 1
fi

echo "✅ Checks completed"

# Cache optimization
echo "🔄 Cache optimization..."
framefox cache clear
framefox cache warmup

# Quick startup test
echo "🧪 Startup test..."
timeout 5s python main.py &
STARTUP_PID=$!
sleep 2
kill $STARTUP_PID 2>/dev/null || true
wait $STARTUP_PID 2>/dev/null || true

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p var/log
mkdir -p var/session

# Start application
echo "🎯 Starting application..."
if [ -f "gunicorn.conf.py" ]; then
  gunicorn -c gunicorn.conf.py main:app
else
  uvicorn main:app --host 0.0.0.0 --port 8000
fi
```

Make the script executable:

```bash
chmod +x deploy.sh
```

## Post-deployment monitoring

### Simple health check

Create a health endpoint in your application:

```python
# In your main controller
@route("/health", methods=["GET"])
def health_check(self):
    return {"status": "ok", "timestamp": datetime.now().isoformat()}
```

### Monitoring script

```bash
#!/bin/bash
# monitor.sh

APP_URL="https://your-domain.com"
HEALTH_ENDPOINT="$APP_URL/health"

# Check that application responds
if curl -f -s "$HEALTH_ENDPOINT" > /dev/null; then
  echo "✅ Application accessible"
else
  echo "❌ Application inaccessible"
  exit 1
fi

# Check JSON response
RESPONSE=$(curl -s "$HEALTH_ENDPOINT")
if echo "$RESPONSE" | grep -q '"status":"ok"'; then
  echo "✅ Application healthy"
else
  echo "❌ Problem detected: $RESPONSE"
  exit 1
fi
```

## Rollback in case of problems

If something goes wrong after deployment:

```bash
#!/bin/bash
# rollback.sh

echo "🔄 Rollback in progress..."

# Stop current application
pkill -f "gunicorn.*main:app" || true

# Return to previous version (according to your strategy)
git checkout HEAD~1  # or your previous version tag

# Clear cache
framefox cache clear

# Restart
export APP_ENV=prod
gunicorn -c gunicorn.conf.py main:app &

echo "✅ Rollback completed"
```

## After deployment

Once your application is deployed, don't forget to:

1. **Monitor performance**: Use tools like New Relic or Datadog
2. **Check logs**: Look for errors or anomalies
3. **Test the application**: Ensure all features work
4. **Set up alerts**: To be informed of problems
5. **Document the process**: To facilitate future deployments

With these tips, your Framefox application will be properly deployed and ready to be used in production.