---
title: Advanced Database Configuration
description: Detailed database configuration, environment setup, and production optimization for Framefox applications
---

This guide covers advanced database configuration scenarios, production optimization, and environment-specific setup for Framefox applications.

## Advanced Configuration File

For complex deployments, use the detailed configuration in `config/orm.yaml`:

```yaml
database 
  # Environment variable takes precedence
  url: "${DATABASE_URL}"
  
  # Fallback detailed configuration
  # driver: "${DATABASE_DRIVER:-postgresql}"
  # host: "${DATABASE_HOST:-localhost}"
  # port: "${DATABASE_PORT:-5432}"
  # username: "${DATABASE_USER:-framefox}"
  # password: "${DATABASE_PASSWORD}"
  # database  "${DATABASE_NAME:-framefoxdb}"
  # charset: "utf8mb4"

  # Production-optimized connection pooling
  pool_size: 20                    # Number of persistent connections
  max_overflow: 10                 # Additional connections when pool is full
  pool_timeout: 30                 # Seconds to wait for available connection
  pool_recycle: 1800              # Seconds before connection refresh
  pool_pre_ping: true             # Validate connections before use
  autocommit: false               # Manual transaction control
  autoflush: false                # Manual session flushing
```

:::note[Connection Pooling Explained]
Framefox's connection pooling optimizes database performance:
- **pool_size**: Core connections kept alive (recommended: 10-50)
- **max_overflow**: Extra connections during peak load
- **pool_timeout**: Prevents hanging requests during high load
- **pool_recycle**: Refreshes stale connections automatically
- **pool_pre_ping**: Detects and handles dropped connections
:::

## Database Driver Installation

Install the appropriate database driver for your chosen database engine:

```bash
# SQLite (included with Python - no installation needed)
# Ideal for development and small applications

# PostgreSQL (recommended for production)
pip install psycopg2-binary
# Alternative: pip install asyncpg  # For async operations

# MySQL/MariaDB
pip install pymysql
# Alternative: pip install aiomysql  # For async operations

# Microsoft SQL Server
pip install pyodbc

# Oracle Database
pip install cx_Oracle
```

:::tip[Database Selection Guide]
Choose your database based on your needs:
- **SQLite**: Development, testing, small applications (< 100 concurrent users)
- **PostgreSQL**: Production applications, complex queries, JSON data, full-text search
- **MySQL**: Web applications, high read workloads, replication needs
- **SQL Server**: Enterprise environments, .NET integration, Windows ecosystems
:::

## Multi-Environment Setup

Configure different databases for different environments:

```bash
# .env.development
DATABASE_URL=sqlite:///dev.db

# .env.testing  
DATABASE_URL=sqlite:///:memory:

# .env.production
DATABASE_URL=postgresql://prod_user:secure_pass@db-cluster:5432/prod_db?sslmode=require
```

**Kubernetes/Docker Configuration:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    environment:
      - DATABASE_URL=postgresql://app:${DB_PASSWORD}@postgres:5432/appdb
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: appdb
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Production Optimization

### Connection Pool Tuning

For high-traffic applications, optimize connection pooling:

```yaml
database:
  # Production pool settings for high concurrency
  pool_size: 50                    # Base connections (adjust based on CPU cores)
  max_overflow: 20                 # Peak traffic connections
  pool_timeout: 60                 # Higher timeout for busy periods
  pool_recycle: 3600              # Recycle connections hourly
  pool_pre_ping: true             # Validate connections
  
  # Performance optimizations
  echo: false                     # Disable SQL logging in production
  autocommit: false               # Explicit transaction control
  autoflush: false                # Manual session management
```

### Load Balancing Configuration

Configure read/write splitting for scalability:

```yaml
database:
  # Primary database (writes)
  primary:
    url: "postgresql://app:pass@primary-db:5432/appdb"
    pool_size: 30
    max_overflow: 10
  
  # Read replicas (reads)
  replicas:
    - url: "postgresql://app:pass@replica1-db:5432/appdb"
      pool_size: 20
      max_overflow: 5
    - url: "postgresql://app:pass@replica2-db:5432/appdb"
      pool_size: 20
      max_overflow: 5
```

### Security Configuration

Implement security best practices:

```yaml
database:
  url: "${DATABASE_URL}"
  
  # SSL/TLS configuration
  ssl_config:
    ssl_mode: "require"
    ssl_cert: "/path/to/client-cert.pem"
    ssl_key: "/path/to/client-key.pem"
    ssl_ca: "/path/to/ca-cert.pem"
  
  # Connection encryption
  options:
    sslmode: "require"
    sslcert: "/etc/ssl/certs/client.crt"
    sslkey: "/etc/ssl/private/client.key"
    sslrootcert: "/etc/ssl/certs/ca.crt"
```

## Environment-Specific Configurations

### Development Environment

Optimized for debugging and rapid development:

```yaml
database:
  url: "sqlite:///dev.db"
  echo: true                      # Enable SQL logging
  pool_size: 5                    # Minimal connections
  autoflush: true                 # Immediate persistence for debugging
```

### Testing Environment

Fast, isolated testing setup:

```yaml
database:
  url: "sqlite:///:memory:"       # In-memory database
  echo: false                     # Clean test output
  pool_size: 1                    # Single connection for tests
  pool_recycle: -1                # Never recycle in tests
```

### Staging Environment

Production-like configuration for testing:

```yaml
database:
  url: "${STAGING_DATABASE_URL}"
  pool_size: 20                   # Production-like load
  max_overflow: 5
  pool_timeout: 30
  echo: false
```

## Monitoring and Health Checks

### Database Health Monitoring

Implement health checks for production monitoring:

```python
from framefox.core.orm.entity_manager_interface import EntityManagerInterface

class DatabaseHealthService:
    def __init__(self, entity_manager: EntityManagerInterface):
        self.em = entity_manager
    
    def health_check(self) -> dict:
        """Comprehensive database health check"""
        try:
            # Basic connectivity test
            with self.em.transaction():
                result = self.em.execute("SELECT 1")
                
            # Connection pool status
            pool_status = {
                "pool_size": self.em.pool.size(),
                "checked_in": self.em.pool.checkedin(),
                "checked_out": self.em.pool.checkedout(),
                "overflow": self.em.pool.overflow(),
                "invalid": self.em.pool.invalid()
            }
            
            return {
                "status": "healthy",
                "connection": "active",
                "pool": pool_status,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now()
            }
```

### Performance Monitoring

Track database performance metrics:

```python
class DatabaseMetricsService:
    def get_performance_metrics(self) -> dict:
        """Get database performance metrics"""
        return {
            "connection_pool": self._get_pool_metrics(),
            "query_performance": self._get_query_metrics(),
            "transaction_stats": self._get_transaction_stats()
        }
    
    def _get_pool_metrics(self) -> dict:
        """Connection pool utilization metrics"""
        return {
            "active_connections": self.em.pool.checkedout(),
            "idle_connections": self.em.pool.checkedin(),
            "pool_utilization": self.em.pool.checkedout() / self.em.pool.size(),
            "overflow_count": self.em.pool.overflow()
        }
```

:::tip[Production Deployment Checklist]
Before deploying to production:
- [ ] Configure SSL/TLS encryption
- [ ] Set up connection pooling appropriately
- [ ] Implement database monitoring
- [ ] Configure backup strategies
- [ ] Test failover scenarios
- [ ] Set up read replicas if needed
- [ ] Configure proper firewall rules
- [ ] Implement connection limits
:::

:::caution[Security Best Practices]
Never commit database credentials to version control:
- Use environment variables for sensitive data
- Use different credentials for each environment
- Enable SSL/TLS for production databases
- Implement proper firewall rules and network security
- Use database user accounts with minimal required permissions
:::
