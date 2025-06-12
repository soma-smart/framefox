---
title: Web Profiler
description: Debug and monitor the performance of your Framefox application with the integrated profiler
---

The Framefox web profiler is a debugging and performance monitoring tool that provides detailed insights into your application's behavior during development.

## Overview

The profiler system automatically captures detailed information about every HTTP request processed by your Framefox application:

- **Request/Response Analysis**: Headers, parameters, status codes, and timing
- **Database Monitoring**: SQL queries with execution times and parameters
- **Memory Tracking**: Memory usage and peak consumption per request
- **Exception Handling**: Python exceptions and HTTP errors (4xx/5xx)
- **Log Collection**: Application logs with context and filtering
- **Routing Information**: Controller methods, templates, and routing details
- **Performance Metrics**: Execution time breakdown and bottleneck identification

## Configuration

### Enabling the Profiler

The profiler is automatically enabled in development mode. You can control it via configuration:

```yaml title="config/debug.yaml"
debug:
  profiler:
    enabled: true             # Enable/disable the profiler
    max_files: 1000           # Max profile files per day
    retention_days: 7         # Days to retain profile data
    max_memory: 100           # Max profiles in memory cache
    sampling_rate: 1.0        # Sampling rate (0.0-1.0)
```

### Environment Configuration

```python title="settings.py"
@property
def profiler_enabled(self) -> bool:
    """Returns whether the profiler is enabled (debug mode only)"""
    if not self.is_debug:
        return False
    return self.config.get("debug", {}).get("profiler", {}).get("enabled", True)
```

### Automatic Middleware Registration

The profiler middleware is automatically registered when enabled. No manual configuration is required.

## Component Architecture

### Core Components

The profiler is organized around several key components:

- **ProfilerMiddleware**: Intercepts HTTP requests/responses and injects the debug toolbar
- **Profiler**: Manages data collectors and stores profiles to disk  
- **Data Collectors**: Collect specific data types (SQL, memory, logs, etc.)

### Data Flow

1. **Request Interception**: `ProfilerMiddleware` captures incoming requests
2. **Data Collection**: Collectors gather information during request processing
3. **Storage**: Data is serialized and stored to disk
4. **Web Interface**: Profiles are accessible via a dedicated web interface
5. **Toolbar Injection**: For HTML responses, a debug toolbar is injected
6. **Storage**: Profile data is saved as JSON files organized by date
7. **Web Interface**: Profiles are accessible via `/_profiler` routes

## Data Collectors

### RequestDataCollector

Captures HTTP request and response information with security filtering.

**Features:**
- Request headers, parameters, and body data
- Response headers and status codes
- Client IP and user agent information
- Automatic filtering of sensitive fields (passwords, tokens, keys)
- Support for JSON, form data, and raw body formats

**Security:**
```python
# Sensitive fields are automatically masked
sensitive_fields = {
    "password", "passwd", "pwd", "secret", "token", "key",
    "api_key", "auth_token", "access_token", "refresh_token",
    "csrf_token", "credit_card", "card_number", "cvv",
    "ssn", "social_security", "private_key", "client_secret"
}
```

### SQLDataCollector

Monitors database queries with detailed performance metrics.

**Features:**
- Captures all SQL queries (SELECT, INSERT, UPDATE, DELETE, etc.)
- Execution time tracking with millisecond precision
- Query parameters and result metadata
- Database configuration information
- Query count and duration statistics
- Integration with SQLAlchemy and SQLModel loggers

**Example Output:**
```json
{
  "queries": [
    {
      "query": "SELECT user.id, user.email FROM user WHERE user.id = ?",
      "duration": 2.45,
      "timestamp": 1640995200.123,
      "formatted_time": "18:54:02.123",
      "parameters": "[1]"
    }
  ],
  "query_count": 1,
  "total_duration": 2.45,
  "average_duration": 2.45
}
```

### ExceptionDataCollector

Handles both Python exceptions and HTTP error responses.

**Python Exceptions:**
- Full stack traces with file and line information
- Exception class, message, and error codes
- Context preservation for debugging

**HTTP Errors:**
- 4xx and 5xx status code handling
- Request context (URL, method, headers)
- Client information and user agent
- Helpful debugging suggestions

### LogDataCollector

Collects application logs with filtering and context.

**Features:**
- Captures logs from all application loggers
- Filters out SQL logs (handled by SQLDataCollector)
- Preserves log levels, timestamps, and context
- Error count statistics
- Request-scoped log collection

### MemoryDataCollector

Tracks memory usage during request processing.

**Metrics:**
- Current memory usage (RSS)
- Peak memory consumption (VMS)
- Memory data in MB for easy reading

```python
# Memory tracking using psutil
process = psutil.Process(os.getpid())
memory_info = process.memory_info()
data = {
    "memory_usage": memory_info.rss / (1024 * 1024),  # MB
    "peak_memory": memory_info.vms / (1024 * 1024)    # MB
}
```

### RouteDataCollector

Provides routing and controller information.

**Data Captured:**
- Route name and path patterns
- Controller class and method names
- Allowed HTTP methods
- Template information (if applicable)
- Endpoint details

### TimeDataCollector

Measures request processing performance.

**Metrics:**
- Total request duration
- Start and end timestamps
- Performance timing breakdown
- Millisecond precision measurements

## Web Interface

### Profile List (`/_profiler`)

The main interface showing all captured profiles:

**Features:**
- Searchable table of all requests
- Filtering by URL, method, status code
- Sortable columns (duration, timestamp, status)
- Pagination for large datasets
- Visual indicators for performance and errors

**UI Elements:**
- **Token**: Unique identifier for each profile
- **URL**: Request URL with truncation for long URLs
- **Method**: HTTP method with color coding
- **Status Code**: Response status with success/error styling
- **Duration**: Request processing time with performance indicators
- **Timestamp**: When the request was processed

### Profile Details (`/_profiler/{token}`)

Detailed view of individual profiles with tabbed interface:

#### Request Panel
- HTTP method, URL, and status code
- Request headers with sensitive data filtering
- Query parameters and form data
- Client information (IP, user agent, referer)
- POST/PUT/PATCH body data with security masking

#### Database Panel
- List of all SQL queries executed
- Execution times and query parameters
- Database configuration details
- Query statistics and performance metrics
- Formatted query display with syntax highlighting

#### Exception Panel
- Python exceptions with full stack traces
- HTTP errors with debugging suggestions
- Error context and metadata
- Solution recommendations based on error type

#### Logs Panel
- Application logs filtered by request
- Log levels, timestamps, and messages
- Error count and level distribution
- Context-aware log grouping

#### Memory Panel
- Memory usage statistics
- Peak memory consumption
- Memory allocation patterns

#### Route Panel
- Controller and method information
- Route patterns and allowed methods
- Template usage information
- Endpoint metadata

#### Performance Panel
- Request duration breakdown
- Timing analysis
- Performance bottleneck identification

### Profiler Toolbar

For HTML responses, a debug toolbar is automatically injected:

**Features:**
- Fixed bottom position with application metrics
- Quick access to profile details
- Color-coded performance indicators
- Memory usage display
- One-click access to detailed profiler view

```html
<!-- Automatically injected toolbar -->
<div id="framefox-profiler" data-token="abc123...">
  <div class="profiler-item">Duration: 45ms</div>
  <div class="profiler-item">Memory: 12.5MB</div>
  <div class="profiler-item">Queries: 3</div>
</div>
```

## Security Features

### Sensitive Data Protection

The profiler automatically protects sensitive information:

**Automatic Filtering:**
- Passwords and authentication tokens
- API keys and secret keys
- Credit card and personal information
- Session IDs and authentication headers

**Implementation:**
```python
# Raw body masking example
password=***FILTERED***&email=user@example.com&roles=['ROLE_USER']

# JSON data filtering
{
  "email": "user@example.com",
  "password": "***FILTERED***",
  "api_key": "***FILTERED***"
}
```

### Header Filtering

Sensitive HTTP headers are automatically masked:
- `Authorization`
- `Cookie`
- `X-API-Key`
- `X-Auth-Token`
- `X-CSRF-Token`

### Production Safety

The profiler is automatically disabled in production:
- Only enabled when `app_env = "dev"`
- No performance impact in production builds
- Automatic cleanup of old profile data

## Performance Considerations

### Storage Management

**File Organization:**
```
var/profiler/
├── 2025-06-03/
│   ├── profile-token-1.json
│   ├── profile-token-2.json
│   └── ...
└── 2025-06-04/
    └── ...
```

**Automatic Cleanup:**
- Daily profile limits (configurable)
- Retention period management
- Oldest file removal when limits exceeded
- Memory cache size limits

### Sampling

Configure sampling to reduce overhead:
```yaml
debug:
  profiler:
    sampling_rate: 0.5  # Profile 50% of requests
```

### Exclusions

Certain paths are automatically excluded:
- `/static/*` - Static assets
- `/_profiler/*` - Profiler interface itself
- `/favicon.ico` - Browser favicon requests

## Troubleshooting

### Common Issues

**Profiler Not Appearing:**
1. Verify debug mode is enabled (`app_env = "dev"`)
2. Check profiler configuration in `config/debug.yaml`
3. Ensure HTML responses contain `</body>` tag for toolbar injection

**Missing SQL Queries:**
1. Verify database logging is enabled
2. Check SQLAlchemy/SQLModel logger configuration
3. Ensure `request_active` flag is properly managed

**Memory Issues:**
1. Reduce `max_files` and `max_memory` settings
2. Implement more aggressive cleanup
3. Use sampling to reduce profile volume

**Performance Impact:**
1. Enable sampling for high-traffic applications
2. Exclude additional paths if needed
3. Monitor disk space usage for profile storage

### Debug Logging

Enable profiler debug logging:
```python
import logging
logging.getLogger("PROFILER").setLevel(logging.DEBUG)
```

### Manual Testing

Test profiler functionality:
```bash
# Make requests to trigger profiling
curl -X GET http://localhost:8000/users
curl -X POST http://localhost:8000/users -d '{"name":"test"}'

# Check profile storage
ls -la var/profiler/$(date +%Y-%m-%d)/

# Access profiler interface
curl http://localhost:8000/_profiler
```

## API Reference

### ProfilerController Routes

- `GET /_profiler` - Profile list interface
- `GET /_profiler/{token}` - Profile details view
- `GET /_profiler/{token}/{panel}` - Specific panel data
- `GET /_profiler/{token}/json` - Raw profile data as JSON

### Configuration Options

| Setting          | Type  | Default | Description             |
| ---------------- | ----- | ------- | ----------------------- |
| `enabled`        | bool  | `true`  | Enable/disable profiler |
| `max_files`      | int   | `1000`  | Max profiles per day    |
| `retention_days` | int   | `7`     | Days to keep profiles   |
| `max_memory`     | int   | `100`   | Max profiles in memory  |
| `sampling_rate`  | float | `1.0`   | Request sampling rate   |

---

The Framefox Web Profiler provides good debugging capabilities for development environments, helping developers identify performance bottlenecks, debug issues, and understand application behavior with detailed metrics and an intuitive web interface.
