---
title: Database & ORM
description: Complete guide to Framefox's integrated ORM for powerful data management
---

# Database & ORM

Framefox includes a powerful Object-Relational Mapping (ORM) system that simplifies database interactions while providing enterprise-grade features for data management. Built with modern Python standards and designed for performance, scalability, and developer productivity.

The ORM supports multiple database engines including SQLite, MySQL, PostgreSQL, and other SQL-compatible databases, making it easy to switch between development and production environments without code changes.

:::info[ORM Architecture]
Framefox ORM is built on top of SQLAlchemy, providing:
- **Type Safety**: Full Python type hints and validation
- **Performance**: Optimized queries with connection pooling
- **Migrations**: Automatic schema versioning with Alembic
- **Relationships**: Intuitive foreign key and join handling
- **Async Support**: Non-blocking database operations
- **Security**: Built-in protection against SQL injection
:::

:::tip[Why Use an ORM?]
ORMs provide several advantages over raw SQL:
- **Database Agnostic**: Write code once, run on any supported database
- **Type Safety**: Catch errors at development time, not runtime
- **Security**: Automatic parameterization prevents SQL injection
- **Maintainability**: Cleaner, more readable code
- **Productivity**: Rapid development with intelligent code completion
- **Testing**: Easy mocking and fixtures for unit tests
:::

## Database Configuration

Framefox provides flexible database configuration options that support both simple URL-based connections and detailed configuration settings. The framework automatically handles connection pooling, transaction management, and performance optimization.

### Environment-Based Configuration

The primary method for database configuration uses environment variables in your `.env` file:

```properties
#==============================
# Database Configuration
#==============================

# Primary database connection (choose one)
DATABASE_URL=sqlite:///app.db
# DATABASE_URL=postgresql://username:password@localhost:5432/dbname
# DATABASE_URL=mysql://username:password@localhost:3306/dbname

# For production environments, use full connection strings:
# DATABASE_URL=postgresql://user:pass@db-host:5432/production_db?sslmode=require
```

:::warning[Security Best Practices]
Never commit database credentials to version control:
- Use environment variables for sensitive data
- Use different credentials for each environment
- Enable SSL/TLS for production databases
- Implement proper firewall rules and network security
- Use database user accounts with minimal required permissions
:::

### Advanced Configuration File

For complex deployments, use the detailed configuration in `config/orm.yaml`:

```yaml
database:
  # Environment variable takes precedence
  url: "${DATABASE_URL}"
  
  # Fallback detailed configuration
  # driver: "${DATABASE_DRIVER:-postgresql}"
  # host: "${DATABASE_HOST:-localhost}"
  # port: "${DATABASE_PORT:-5432}"
  # username: "${DATABASE_USER:-framefox}"
  # password: "${DATABASE_PASSWORD}"
  # database: "${DATABASE_NAME:-framefoxdb}"
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

:::info[Connection Pooling Explained]
Framefox's connection pooling optimizes database performance:
- **pool_size**: Core connections kept alive (recommended: 10-50)
- **max_overflow**: Extra connections during peak load
- **pool_timeout**: Prevents hanging requests during high load
- **pool_recycle**: Refreshes stale connections automatically
- **pool_pre_ping**: Detects and handles dropped connections
:::

### Database Driver Installation

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

### Multi-Environment Setup

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

## Entity Management

### Creating Entities

Entity creation in Framefox can be done through the command-line interface or manually. Entities represent your database tables as Python classes, following the clean architecture principle where entities contain only data structure and validation logic.

#### Using the Command Line Generator

Generate a new entity with the built-in command:

```bash
framefox create entity User
```

This command creates a new entity file in `src/entity/user.py` with basic structure and common fields.

:::tip[Entity Generation Benefits]
The entity generator provides:
- **Consistent Structure**: Standard file organization and naming conventions
- **Boilerplate Code**: Pre-configured imports and basic methods
- **Best Practices**: Following framework conventions out of the box
- **Time Saving**: Rapid entity creation for faster development
:::

#### Entity Structure Example

Entities in Framefox follow a clean approach focused on data structure. Here's the actual structure used in the framework:

```python
from framefox.core.orm.abstract_entity import AbstractEntity
from sqlmodel import Field, Relationship
from datetime import datetime
from typing import List
import uuid

class User(AbstractEntity, table=True):
    """User entity representing application users"""
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    password: str = Field(nullable=False)
    roles: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    organization_id: uuid.UUID | None = Field(foreign_key="organization.id", nullable=True)

    # Relations (handled by SQLModel Relationship)
    organization: "Organization" = Relationship(back_populates="users")
    user_groups: List["UserGroup"] = Relationship(back_populates="user")
    scenarios: List["Scenario"] = Relationship(back_populates="creator")
```

:::info[Entity Design Philosophy]
Framefox entities follow these principles:
- **Data Only**: Entities contain only data structure and basic validation
- **No Business Logic**: Business operations are handled by repositories and services
- **SQLModel Integration**: Uses SQLModel for type safety and Pydantic validation
- **Automatic Models**: Generate create/find models automatically for API endpoints
:::

:::warning[Password Security]
Never store plain text passwords in the database:
- Always hash passwords using secure algorithms (bcrypt, Argon2)
- Use salt for additional security
- Consider implementing password complexity requirements
- Implement secure password reset mechanisms
:::

### Column Types and Configuration

Framefox supports SQLModel field types with comprehensive validation and configuration options:

```python
from sqlmodel import Field, Column, JSON
from datetime import datetime
import uuid

class Product(AbstractEntity, table=True):
    """Product entity demonstrating various field types"""
    
    id: int | None = Field(default=None, primary_key=True)
    
    # Text fields with validation
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None)
    slug: str = Field(unique=True, max_length=255)
    
    # Numeric fields with constraints
    price: float = Field(gt=0)  # Greater than 0
    stock: int = Field(ge=0, default=0)  # Greater or equal to 0
    weight: float | None = Field(default=None, gt=0)
    
    # JSON data for structured information
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))
    specifications: list = Field(default_factory=list, sa_column=Column(JSON))
    
    # Boolean flags
    is_featured: bool = Field(default=False)
    is_digital: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default=None)
    
    # UUID for external references
    external_id: uuid.UUID = Field(default_factory=uuid.uuid4)
```

:::info[Field Type Selection Guide]
Choose appropriate field types based on your data:
- **str**: Text data with length constraints using `min_length`/`max_length`
- **int/float**: Numeric data with validation using `gt`, `ge`, `lt`, `le`
- **bool**: True/false flags with clear defaults
- **datetime**: Timestamps with automatic generation using `default_factory`
- **JSON**: Structured data that needs querying capabilities
- **UUID**: Unique identifiers for external system integration
:::

### Advanced Field Configuration

```python
class AdvancedEntity(AbstractEntity, table=True):
    # Field with multiple constraints and validation
    email: str = Field(
        regex=r'^[^@]+@[^@]+\.[^@]+$',  # Email validation
        unique=True,
        max_length=255
    )
    
    # Optional field with custom default
    status: str = Field(
        default="active",
        regex=r'^(active|inactive|pending)$'  # Enum-like validation
    )
    
    # Foreign key with cascade behavior
    user_id: int = Field(foreign_key="user.id")
    
    # Soft delete support
    deleted_at: datetime | None = Field(default=None)
```

## Entity Relationships

Understanding and implementing relationships between entities is crucial for building robust applications. Framefox uses SQLModel's Relationship functionality to manage connections between entities efficiently.

### One-to-Many Relationships

One-to-Many relationships are the most common type, where one entity can have multiple related entities. This is implemented using foreign keys and SQLModel relationships.

#### User-Posts Example

```python
# User entity (one side)
class User(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)
    
    # Relationship to posts
    posts: List["Post"] = Relationship(back_populates="author")

# Post entity (many side)
class Post(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    content: str | None = Field(default=None)
    
    # Foreign key to User
    user_id: int = Field(foreign_key="user.id")
    
    # Relationship back to user
    author: User = Relationship(back_populates="posts")
```

:::tip[Relationship Best Practices]
When implementing relationships:
- **Use back_populates**: Ensures bidirectional relationship consistency
- **Foreign key naming**: Follow `{table}_id` convention for clarity
- **Nullable considerations**: Use `nullable=False` for required relationships
- **Index foreign keys**: Improves query performance automatically
:::

### Many-to-Many Relationships

Many-to-Many relationships require a junction table (intermediate entity) to manage the connections between two entities.

#### User-Role Relationship Example

```python
# Junction table for User-Role relationship
class UserRole(AbstractEntity, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)
    
    # Additional relationship metadata
    assigned_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = Field(default=True)

# Role entity
class Role(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    description: str | None = Field(default=None)
    
    # Relationship to users through junction table
    users: List[User] = Relationship(
        back_populates="roles",
        link_table=UserRole
    )

# Enhanced User entity with roles
class User(AbstractEntity, table=True):
    # ... existing fields ...
    
    # Relationship to roles through junction table
    roles: List[Role] = Relationship(
        back_populates="users",
        link_table=UserRole
    )
```

### One-to-One Relationships

One-to-One relationships link exactly one entity to another, often used for profile extensions or detailed information separation.

```python
# User entity
class User(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    
    # One-to-one relationship
    profile: "UserProfile" = Relationship(back_populates="user")

# Profile entity
class UserProfile(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    bio: str | None = Field(default=None)
    avatar_url: str | None = Field(default=None)
    
    # Foreign key to User (unique for one-to-one)
    user_id: int = Field(foreign_key="user.id", unique=True)
    
    # Relationship back to user
    user: User = Relationship(back_populates="profile")
```

:::info[Relationship Pattern Benefits]
SQLModel relationships provide:
- **Automatic Loading**: Related data loaded efficiently
- **Type Safety**: Full Python type hints for related objects
- **Query Optimization**: Intelligent JOIN generation
- **Consistency**: Automatic foreign key constraint management
- **Validation**: Pydantic validation for related data
:::
    
    def get_roles(self):
        """Get all active roles for this user"""
        from src.repository.user_role_repository import UserRoleRepository
        from src.repository.role_repository import RoleRepository
        
        user_role_repo = UserRoleRepository()
        role_repo = RoleRepository()
        
        user_roles = user_role_repo.find_by({
            "user_id": self.id, 
            "is_active": True
        })
        
        roles = []
        for user_role in user_roles:
            if not user_role.is_expired():
                role = role_repo.find(user_role.role_id)
                if role:
                    roles.append(role)
        
        return roles
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role"""
        roles = self.get_roles()
        return any(role.name == role_name for role in roles)
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission through their roles"""
        roles = self.get_roles()
        
        for role in roles:
            if hasattr(role, permission) and getattr(role, permission):
                return True
        
        return False
    
    def assign_role(self, role_id: int, assigned_by: int = None, expires_at = None):
        """Assign a role to this user"""
        from src.repository.user_role_repository import UserRoleRepository
        
        user_role_repo = UserRoleRepository()
        
        # Check if assignment already exists
        existing = user_role_repo.find_one_by({
            "user_id": self.id,
            "role_id": role_id,
            "is_active": True
        })
        
        if existing:
            return existing
        
        # Create new role assignment
        user_role_data = {
            "user_id": self.id,
            "role_id": role_id,
            "assigned_by": assigned_by,
            "expires_at": expires_at,
            "is_active": True
        }
        
        return user_role_repo.create(user_role_data)
    
    def revoke_role(self, role_id: int):
        """Revoke a role from this user"""
        from src.repository.user_role_repository import UserRoleRepository
        
        user_role_repo = UserRoleRepository()
        
        user_role = user_role_repo.find_one_by({
            "user_id": self.id,
            "role_id": role_id,
            "is_active": True
        })
        
        if user_role:
            user_role.is_active = False
            user_role_repo.update(user_role.id, {"is_active": False})
            return True
        
        return False
```

:::warning[Many-to-Many Considerations]
When implementing many-to-many relationships:
- **Junction tables should have meaningful names** (user_roles, not user_role_mapping)
- **Consider additional metadata** in junction tables (created_at, expires_at)
- **Use composite primary keys** or separate ID columns based on your needs
- **Implement cascade deletes carefully** to maintain data integrity
- **Add indexes** on foreign key columns for performance
- **Consider the order of operations** when creating/deleting relationships
:::

### One-to-One Relationships

One-to-One relationships are less common but useful for separating concerns or extending entities:

```python
class UserProfile(Entity):
    """
    Extended user profile information in separate table
    Demonstrates one-to-one relationship with User
    """
    __tablename__ = "user_profiles"
    
    id = Column("id", type="INTEGER", primary_key=True, auto_increment=True)
    user_id = Column("user_id", type="INTEGER", foreign_key="users.id", unique=True, nullable=False)
    
    # Extended profile fields
    phone = Column("phone", type="VARCHAR(20)")
    address = Column("address", type="TEXT")
    date_of_birth = Column("date_of_birth", type="DATE")
    website = Column("website", type="VARCHAR(255)")
    linkedin_url = Column("linkedin_url", type="VARCHAR(255)")
    github_url = Column("github_url", type="VARCHAR(255)")
    
    # Preferences
    timezone = Column("timezone", type="VARCHAR(50)", default="UTC")
    language = Column("language", type="VARCHAR(5)", default="en")
    email_notifications = Column("email_notifications", type="BOOLEAN", default=True)
    
    def __str__(self) -> str:
        return f"UserProfile(user_id={self.user_id})"
    
    def get_user(self):
        """Get the associated user"""
        from src.repository.user_repository import UserRepository
        user_repo = UserRepository()
        return user_repo.find(self.user_id)
```

:::info[Relationship Performance Tips]
- **Use eager loading** when you know you'll need related data
- **Implement repository methods** for common relationship queries
- **Consider denormalization** for frequently accessed data
- **Use database indexes** on foreign key columns
- **Batch operations** when working with multiple relationships
- **Cache expensive relationship queries** when appropriate
:::
## Repository Pattern

The Repository pattern in Framefox provides a clean abstraction layer between your application logic and data persistence. Repositories encapsulate the logic needed to access data sources, centralizing common data access functionality for better maintainability and testability.

### Base Repository

All repositories extend the base `Repository` class, which provides fundamental CRUD operations and query capabilities:

```python
from framefox.core.orm.repository import Repository
from src.entity.user import User
from typing import List, Optional, Dict, Any

class UserRepository(Repository):
    """
    User repository providing specialized user data access methods
    Extends base repository with user-specific functionality
    """
    
    def __init__(self):
        super().__init__(User)
    
    def find_by_username(self, username: str) -> Optional[User]:
        """Find a user by their unique username"""
        return self.find_one_by({"username": username})
    
    def find_by_email(self, email: str) -> Optional[User]:
        """Find a user by their unique email address"""
        return self.find_one_by({"email": email})
    
    def find_active_users(self) -> List[User]:
        """Retrieve all active users from the database"""
        return self.find_by({"is_active": True})
    
    def find_admins(self) -> List[User]:
        """Get all users with administrative privileges"""
        return self.find_by({"is_admin": True, "is_active": True})
    
    def search_users(self, query: str, limit: int = 50) -> List[User]:
        """
        Search users by username, email, first name, or last name
        Uses SQL LIKE for flexible text matching
        """
        if not query or len(query.strip()) < 2:
            return []
        
        search_term = f"%{query.strip()}%"
        sql = """
        SELECT * FROM users 
        WHERE (
            username LIKE ? OR 
            email LIKE ? OR 
            first_name LIKE ? OR 
            last_name LIKE ?
        )
        AND is_active = 1
        ORDER BY 
            CASE 
                WHEN username LIKE ? THEN 1
                WHEN email LIKE ? THEN 2
                ELSE 3
            END,
            username ASC
        LIMIT ?
        """
        
        params = [search_term] * 6 + [limit]
        return self.query(sql, params)
    
    def get_users_with_posts_count(self) -> List[Dict[str, Any]]:
        """
        Get users with their post count for analytics
        Returns list of dictionaries with user data and post counts
        """
        sql = """
        SELECT 
            u.*,
            COUNT(p.id) as posts_count,
            COUNT(CASE WHEN p.status = 'published' THEN 1 END) as published_posts_count,
            MAX(p.created_at) as last_post_date
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
        WHERE u.is_active = 1
        GROUP BY u.id
        ORDER BY posts_count DESC, u.username ASC
        """
        return self.query(sql)
    
    def create_user(self, data: Dict[str, Any]) -> User:
        """
        Create a new user with validation
        Ensures email and username uniqueness
        """
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Field '{field}' is required")
        
        # Check email uniqueness
        if self.find_by_email(data['email']):
            raise ValueError("A user with this email already exists")
        
        # Check username uniqueness
        if self.find_by_username(data['username']):
            raise ValueError("This username is already taken")
        
        # Validate email format
        if '@' not in data['email'] or '.' not in data['email']:
            raise ValueError("Invalid email format")
        
        # Validate username format
        username = data['username'].strip()
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        # Hash password before storing (implement password hashing)
        # data['password'] = self._hash_password(data['password'])
        
        return self.create(data)
    
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        from datetime import datetime
        return self.update(user_id, {"last_login": datetime.now()})
    
    def get_recently_registered(self, days: int = 7, limit: int = 20) -> List[User]:
        """Get users registered within the specified number of days"""
        sql = """
        SELECT * FROM users 
        WHERE created_at >= DATE('now', '-{} days')
        AND is_active = 1
        ORDER BY created_at DESC
        LIMIT ?
        """.format(days)
        
        return self.query(sql, [limit])
    
    def get_user_statistics(self) -> Dict[str, int]:
        """Get comprehensive user statistics"""
        sql = """
        SELECT 
            COUNT(*) as total_users,
            COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users,
            COUNT(CASE WHEN is_admin = 1 THEN 1 END) as admin_users,
            COUNT(CASE WHEN created_at >= DATE('now', '-30 days') THEN 1 END) as new_users_30d,
            COUNT(CASE WHEN last_login >= DATE('now', '-7 days') THEN 1 END) as active_7d
        FROM users
        """
        
        result = self.query(sql)
        return result[0] if result else {}
```

:::tip[Repository Best Practices]
Follow these patterns for effective repository design:
- **Single Responsibility**: Each repository handles one entity type
- **Descriptive Method Names**: Clear, action-oriented method names
- **Input Validation**: Validate parameters before database operations
- **Error Handling**: Provide meaningful error messages
- **Documentation**: Document complex queries and business logic
- **Type Hints**: Use type hints for better IDE support and documentation
:::

### Advanced Repository with Complex Queries

```python
from framefox.core.orm.repository import Repository
from src.entity.post import Post
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

class PostRepository(Repository):
    """
    Advanced post repository demonstrating complex queries
    and sophisticated data access patterns
    """
    
    def __init__(self):
        super().__init__(Post)
    
    def find_published_posts(self, limit: int = None) -> List[Post]:
        """Get all published posts with author information"""
        sql = """
        SELECT 
            p.*,
            u.username as author_username,
            u.first_name as author_first_name,
            u.last_name as author_last_name
        FROM posts p
        INNER JOIN users u ON p.user_id = u.id
        WHERE p.status = 'published' 
        AND p.published_at IS NOT NULL
        AND p.published_at <= CURRENT_TIMESTAMP
        ORDER BY p.published_at DESC
        """
        
        if limit:
            sql += f" LIMIT {limit}"
        
        return self.query(sql)
    
    def find_posts_by_tag(self, tag: str, limit: int = 20) -> List[Post]:
        """Find posts by tag with tag relationship"""
        sql = """
        SELECT DISTINCT p.*, t.name as tag_name
        FROM posts p
        INNER JOIN post_tags pt ON p.id = pt.post_id
        INNER JOIN tags t ON pt.tag_id = t.id
        WHERE t.name = ? 
        AND p.status = 'published'
        ORDER BY p.published_at DESC
        LIMIT ?
        """
        return self.query(sql, [tag, limit])
    
    def get_popular_posts(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular posts based on views and comments
        within specified time period
        """
        sql = """
        SELECT 
            p.*,
            u.username as author_username,
            p.view_count,
            COUNT(c.id) as comments_count,
            (p.view_count * 0.7 + COUNT(c.id) * 0.3) as popularity_score
        FROM posts p
        INNER JOIN users u ON p.user_id = u.id
        LEFT JOIN comments c ON p.id = c.post_id
        WHERE p.status = 'published'
        AND p.published_at >= DATE('now', '-{} days')
        GROUP BY p.id
        ORDER BY popularity_score DESC
        LIMIT ?
        """.format(days)
        
        return self.query(sql, [limit])
    
    def paginate_posts(self, page: int = 1, per_page: int = 10, 
                      filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Advanced pagination with filtering and sorting
        Returns paginated results with metadata
        """
        filters = filters or {}
        offset = (page - 1) * per_page
        
        # Build WHERE clause dynamically
        where_conditions = ["p.status = 'published'"]
        params = []
        
        if filters.get('author_id'):
            where_conditions.append("p.user_id = ?")
            params.append(filters['author_id'])
        
        if filters.get('category'):
            where_conditions.append("p.category = ?")
            params.append(filters['category'])
        
        if filters.get('search'):
            where_conditions.append(
                "(p.title LIKE ? OR p.content LIKE ? OR p.excerpt LIKE ?)"
            )
            search_term = f"%{filters['search']}%"
            params.extend([search_term, search_term, search_term])
        
        if filters.get('date_from'):
            where_conditions.append("p.published_at >= ?")
            params.append(filters['date_from'])
        
        if filters.get('date_to'):
            where_conditions.append("p.published_at <= ?")
            params.append(filters['date_to'])
        
        where_clause = " AND ".join(where_conditions)
        
        # Main query
        sql = f"""
        SELECT 
            p.*,
            u.username as author_username,
            u.first_name as author_first_name,
            u.last_name as author_last_name
        FROM posts p
        INNER JOIN users u ON p.user_id = u.id
        WHERE {where_clause}
        ORDER BY p.published_at DESC
        LIMIT ? OFFSET ?
        """
        
        posts = self.query(sql, params + [per_page, offset])
        
        # Count query for pagination metadata
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM posts p
        WHERE {where_clause}
        """
        
        total_result = self.query(count_sql, params)
        total = total_result[0]['total'] if total_result else 0
        
        return {
            'data': posts,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': total,
                'last_page': (total + per_page - 1) // per_page,
                'from': offset + 1 if posts else 0,
                'to': offset + len(posts),
                'has_next': page * per_page < total,
                'has_prev': page > 1
            },
            'filters': filters
        }
    
    def get_post_analytics(self, post_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for a specific post"""
        sql = """
        SELECT 
            p.*,
            u.username as author_username,
            COUNT(DISTINCT c.id) as comments_count,
            COUNT(DISTINCT l.id) as likes_count,
            COUNT(DISTINCT s.id) as shares_count,
            AVG(r.rating) as average_rating,
            COUNT(DISTINCT r.id) as ratings_count
        FROM posts p
        INNER JOIN users u ON p.user_id = u.id
        LEFT JOIN comments c ON p.id = c.post_id
        LEFT JOIN post_likes l ON p.id = l.post_id
        LEFT JOIN post_shares s ON p.id = s.post_id
        LEFT JOIN post_ratings r ON p.id = r.post_id
        WHERE p.id = ?
        GROUP BY p.id
        """
        
        result = self.query(sql, [post_id])
        return result[0] if result else {}
    
    def find_related_posts(self, post_id: int, limit: int = 5) -> List[Post]:
        """
        Find related posts based on tags and category
        Excludes the current post from results
        """
        sql = """
        SELECT DISTINCT p2.*, COUNT(t.id) as common_tags
        FROM posts p1
        INNER JOIN post_tags pt1 ON p1.id = pt1.post_id
        INNER JOIN tags t ON pt1.tag_id = t.id
        INNER JOIN post_tags pt2 ON t.id = pt2.tag_id
        INNER JOIN posts p2 ON pt2.post_id = p2.id
        WHERE p1.id = ?
        AND p2.id != ?
        AND p2.status = 'published'
        GROUP BY p2.id
        ORDER BY common_tags DESC, p2.published_at DESC
        LIMIT ?
        """
        
        return self.query(sql, [post_id, post_id, limit])
    
    def get_content_calendar(self, year: int, month: int) -> List[Dict[str, Any]]:
        """Get content calendar for editorial planning"""
        sql = """
        SELECT 
            DATE(p.published_at) as publish_date,
            COUNT(*) as posts_count,
            GROUP_CONCAT(p.title, ' | ') as titles,
            GROUP_CONCAT(u.username, ' | ') as authors
        FROM posts p
        INNER JOIN users u ON p.user_id = u.id
        WHERE strftime('%Y', p.published_at) = ?
        AND strftime('%m', p.published_at) = ?
        AND p.status = 'published'
        GROUP BY DATE(p.published_at)
        ORDER BY publish_date ASC
        """
        
        return self.query(sql, [str(year), f"{month:02d}"])
```

:::warning[Query Performance]
When writing complex queries:
- **Use indexes** on frequently queried columns
- **Limit result sets** to prevent memory issues
- **Avoid N+1 queries** by joining related data
- **Profile slow queries** and optimize them
- **Consider pagination** for large datasets
- **Cache expensive queries** when appropriate
:::

### Repository with Caching

```python
from framefox.core.orm.repository import Repository
from framefox.core.cache.cache_manager import CacheManager
from src.entity.user import User
from typing import Optional, List
import json

class CachedUserRepository(Repository):
    """
    User repository with intelligent caching for improved performance
    """
    
    def __init__(self, cache_manager: CacheManager):
        super().__init__(User)
        self.cache = cache_manager
        self.cache_ttl = 3600  # 1 hour default TTL
    
    def find_with_cache(self, user_id: int) -> Optional[User]:
        """Find user with caching support"""
        cache_key = f"user:{user_id}"
        
        # Try cache first
        cached_user = self.cache.get(cache_key)
        if cached_user:
            return self._deserialize_user(cached_user)
        
        # Load from database
        user = self.find(user_id)
        if user:
            # Cache for future requests
            self.cache.set(cache_key, self._serialize_user(user), self.cache_ttl)
        
        return user
    
    def find_by_username_cached(self, username: str) -> Optional[User]:
        """Find by username with caching"""
        cache_key = f"user:username:{username}"
        
        cached_user = self.cache.get(cache_key)
        if cached_user:
            return self._deserialize_user(cached_user)
        
        user = self.find_by_username(username)
        if user:
            self.cache.set(cache_key, self._serialize_user(user), self.cache_ttl)
            # Also cache by ID
            id_cache_key = f"user:{user.id}"
            self.cache.set(id_cache_key, self._serialize_user(user), self.cache_ttl)
        
        return user
    
    def update(self, user_id: int, data: dict) -> bool:
        """Update user and invalidate related cache entries"""
        result = super().update(user_id, data)
        
        if result:
            self.invalidate_user_cache(user_id)
        
        return result
    
    def delete(self, user_id: int) -> bool:
        """Delete user and clean up cache"""
        # Get user first to access username for cache cleanup
        user = self.find(user_id)
        result = super().delete(user_id)
        
        if result and user:
            self.invalidate_user_cache(user_id)
            username_key = f"user:username:{user.username}"
            self.cache.delete(username_key)
        
        return result
    
    def invalidate_user_cache(self, user_id: int):
        """Invalidate all cache entries for a specific user"""
        cache_key = f"user:{user_id}"
        self.cache.delete(cache_key)
        
        # Also invalidate any user-related list caches
        self.cache.delete_pattern("users:*")
    
    def _serialize_user(self, user: User) -> str:
        """Convert user object to JSON for caching"""
        return json.dumps(user.to_dict())
    
    def _deserialize_user(self, cached_data: str) -> User:
        """Convert cached JSON back to user object"""
        data = json.loads(cached_data)
        user = User()
        for key, value in data.items():
            setattr(user, key, value)
        return user
```

## Entity Manager & Transactions

The EntityManager is the central component for managing entity lifecycles, transactions, and database operations in Framefox. It provides fine-grained control over when and how data is persisted to the database.

### Understanding the EntityManager

The EntityManager acts as a Unit of Work, tracking entity changes and managing database transactions:

```python
from framefox.core.orm.entity_manager import EntityManager
from src.entity.user import User
from src.entity.post import Post
from typing import List, Optional

class UserService:
    """
    Service layer demonstrating EntityManager usage patterns
    Handles complex business logic with proper transaction management
    """
    
    def __init__(self, entity_manager: EntityManager):
        self.em = entity_manager
    
    def create_user_with_profile(self, user_data: dict, profile_data: dict) -> User:
        """
        Create a user and their profile in a single transaction
        Demonstrates proper transaction management and error handling
        """
        try:
            # Begin explicit transaction
            self.em.begin_transaction()
            
            # Create and persist user
            user = User()
            user.username = user_data['username']
            user.email = user_data['email']
            user.password = self._hash_password(user_data['password'])
            user.first_name = user_data.get('first_name', '')
            user.last_name = user_data.get('last_name', '')
            user.is_active = True
            
            # Persist user to database
            self.em.persist(user)
            
            # Flush to get the generated ID without committing
            self.em.flush()
            
            # Create profile with user ID
            from src.entity.user_profile import UserProfile
            profile = UserProfile()
            profile.user_id = user.id
            profile.bio = profile_data.get('bio', '')
            profile.phone = profile_data.get('phone')
            profile.website = profile_data.get('website')
            profile.timezone = profile_data.get('timezone', 'UTC')
            
            self.em.persist(profile)
            
            # Commit both operations
            self.em.commit()
            
            return user
            
        except Exception as e:
            # Rollback on any error
            self.em.rollback()
            raise Exception(f"Failed to create user with profile: {str(e)}")
    
    def transfer_posts_ownership(self, from_user_id: int, to_user_id: int, 
                               post_ids: List[int]) -> bool:
        """
        Transfer multiple posts from one user to another
        Demonstrates bulk operations within transactions
        """
        try:
            self.em.begin_transaction()
            
            # Verify both users exist
            from_user = self.em.find(User, from_user_id)
            to_user = self.em.find(User, to_user_id)
            
            if not from_user or not to_user:
                raise ValueError("Source or destination user not found")
            
            if not to_user.is_active:
                raise ValueError("Cannot transfer posts to inactive user")
            
            # Transfer each post
            transferred_count = 0
            for post_id in post_ids:
                post = self.em.find(Post, post_id)
                
                if post and post.user_id == from_user_id:
                    post.user_id = to_user_id
                    # Update timestamp to track the change
                    from datetime import datetime
                    post.updated_at = datetime.now()
                    
                    self.em.persist(post)
                    transferred_count += 1
            
            # Log the transfer operation
            from src.entity.transfer_log import TransferLog
            log = TransferLog()
            log.from_user_id = from_user_id
            log.to_user_id = to_user_id
            log.posts_transferred = transferred_count
            log.transfer_date = datetime.now()
            
            self.em.persist(log)
            self.em.commit()
            
            return transferred_count > 0
            
        except Exception as e:
            self.em.rollback()
            raise Exception(f"Posts transfer failed: {str(e)}")
    
    def bulk_update_users(self, updates: List[dict]) -> dict:
        """
        Update multiple users efficiently with validation
        Returns summary of successful and failed updates
        """
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            self.em.begin_transaction()
            
            for update in updates:
                try:
                    user_id = update.get('id')
                    update_data = update.get('data', {})
                    
                    if not user_id:
                        results['errors'].append("Missing user ID in update")
                        results['failed'] += 1
                        continue
                    
                    user = self.em.find(User, user_id)
                    if not user:
                        results['errors'].append(f"User {user_id} not found")
                        results['failed'] += 1
                        continue
                    
                    # Apply updates with validation
                    for key, value in update_data.items():
                        if hasattr(user, key):
                            # Validate specific fields
                            if key == 'email' and value:
                                if '@' not in value:
                                    results['errors'].append(f"Invalid email for user {user_id}")
                                    results['failed'] += 1
                                    continue
                            
                            setattr(user, key, value)
                    
                    self.em.persist(user)
                    results['successful'] += 1
                    
                except Exception as e:
                    results['errors'].append(f"Error updating user {update.get('id', 'unknown')}: {str(e)}")
                    results['failed'] += 1
            
            # Only commit if we have successful updates
            if results['successful'] > 0:
                self.em.commit()
            else:
                self.em.rollback()
            
            return results
            
        except Exception as e:
            self.em.rollback()
            results['errors'].append(f"Bulk update failed: {str(e)}")
            return results
    
    def deactivate_user_cascade(self, user_id: int) -> bool:
        """
        Deactivate user and handle cascade operations
        Demonstrates complex business logic with multiple entity updates
        """
        try:
            self.em.begin_transaction()
            
            user = self.em.find(User, user_id)
            if not user:
                raise ValueError("User not found")
            
            if not user.is_active:
                return True  # Already deactivated
            
            # Deactivate user
            user.is_active = False
            from datetime import datetime
            user.updated_at = datetime.now()
            self.em.persist(user)
            
            # Handle user's posts
            from src.repository.post_repository import PostRepository
            post_repo = PostRepository()
            user_posts = post_repo.find_by({"user_id": user_id, "status": "published"})
            
            for post in user_posts:
                # Archive published posts instead of deleting
                post.status = "archived"
                post.updated_at = datetime.now()
                self.em.persist(post)
            
            # Revoke active sessions
            from src.entity.user_session import UserSession
            sessions = self.em.query(
                "SELECT * FROM user_sessions WHERE user_id = ? AND is_active = 1",
                [user_id]
            )
            
            for session in sessions:
                session_obj = UserSession()
                for key, value in session.items():
                    setattr(session_obj, key, value)
                session_obj.is_active = False
                self.em.persist(session_obj)
            
            # Log deactivation
            from src.entity.user_log import UserLog
            log = UserLog()
            log.user_id = user_id
            log.action = "deactivated"
            log.timestamp = datetime.now()
            log.details = "User deactivated with cascade operations"
            
            self.em.persist(log)
            self.em.commit()
            
            return True
            
        except Exception as e:
            self.em.rollback()
            raise Exception(f"User deactivation failed: {str(e)}")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using secure algorithm"""
        # Implement proper password hashing (bcrypt, Argon2, etc.)
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
```

:::danger[Transaction Management]
Always follow these transaction patterns:
- **Always use try-except blocks** around transactions
- **Call rollback() in exception handlers** to maintain data consistency
- **Keep transactions short** to minimize lock time
- **Don't nest transactions** unless using savepoints
- **Test transaction rollback scenarios** thoroughly
:::

### Advanced EntityManager Operations

```python
class AdvancedEntityOperations:
    """
    Advanced EntityManager patterns for complex scenarios
    """
    
    def __init__(self, entity_manager: EntityManager):
        self.em = entity_manager
    
    def batch_create_with_relationships(self, batch_data: List[dict]) -> dict:
        """
        Create multiple entities with relationships in batches
        Optimized for large data imports
        """
        results = {
            'created': 0,
            'errors': [],
            'created_ids': []
        }
        
        batch_size = 100  # Process in chunks
        
        try:
            self.em.begin_transaction()
            
            for i in range(0, len(batch_data), batch_size):
                batch = batch_data[i:i + batch_size]
                
                for item_data in batch:
                    try:
                        # Create primary entity
                        user = User()
                        user.username = item_data['username']
                        user.email = item_data['email']
                        user.password = self._hash_password(item_data['password'])
                        
                        self.em.persist(user)
                        self.em.flush()  # Get ID for relationships
                        
                        # Create related entities
                        if 'profile' in item_data:
                            profile = UserProfile()
                            profile.user_id = user.id
                            profile.bio = item_data['profile'].get('bio', '')
                            self.em.persist(profile)
                        
                        if 'roles' in item_data:
                            for role_id in item_data['roles']:
                                user_role = UserRole()
                                user_role.user_id = user.id
                                user_role.role_id = role_id
                                self.em.persist(user_role)
                        
                        results['created'] += 1
                        results['created_ids'].append(user.id)
                        
                    except Exception as e:
                        results['errors'].append(f"Item {i}: {str(e)}")
                
                # Commit each batch
                self.em.commit()
                self.em.begin_transaction()
            
            self.em.commit()
            return results
            
        except Exception as e:
            self.em.rollback()
            results['errors'].append(f"Batch operation failed: {str(e)}")
            return results
    
    def find_with_lazy_loading(self, entity_class, entity_id: int, 
                             load_relations: List[str] = None):
        """
        Find entity with selective relationship loading
        Optimizes queries by loading only required relationships
        """
        entity = self.em.find(entity_class, entity_id)
        
        if not entity or not load_relations:
            return entity
        
        # Load specified relationships
        for relation in load_relations:
            if relation == 'posts' and hasattr(entity, 'get_posts'):
                entity._loaded_posts = entity.get_posts()
            elif relation == 'roles' and hasattr(entity, 'get_roles'):
                entity._loaded_roles = entity.get_roles()
            elif relation == 'profile' and hasattr(entity, 'get_profile'):
                entity._loaded_profile = entity.get_profile()
        
        return entity
    
    def execute_with_retry(self, operation_func, max_retries: int = 3) -> any:
        """
        Execute database operation with automatic retry on failure
        Useful for handling temporary connection issues
        """
        import time
        
        for attempt in range(max_retries):
            try:
                return operation_func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # Wait before retry (exponential backoff)
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                
                # Reset connection if needed
                self.em.clear()
    
    def get_entity_changes(self, entity) -> dict:
        """
        Get pending changes for an entity
        Useful for audit logs and debugging
        """
        if not hasattr(entity, '_original_values'):
            return {}
        
        changes = {}
        for attr, original_value in entity._original_values.items():
            current_value = getattr(entity, attr, None)
            if current_value != original_value:
                changes[attr] = {
                    'from': original_value,
                    'to': current_value
                }
        
        return changes
    
    def soft_delete_with_cascade(self, entity_class, entity_id: int, 
                               cascade_relations: List[str] = None) -> bool:
        """
        Perform soft delete with cascade to related entities
        Maintains referential integrity while preserving data
        """
        try:
            self.em.begin_transaction()
            
            entity = self.em.find(entity_class, entity_id)
            if not entity:
                return False
            
            # Mark primary entity as deleted
            from datetime import datetime
            entity.deleted_at = datetime.now()
            self.em.persist(entity)
            
            # Handle cascade relations
            if cascade_relations:
                for relation in cascade_relations:
                    if relation == 'posts':
                        posts = entity.get_posts()
                        for post in posts:
                            post.deleted_at = datetime.now()
                            self.em.persist(post)
                    
                    elif relation == 'comments':
                        comments = entity.get_comments()
                        for comment in comments:
                            comment.deleted_at = datetime.now()
                            self.em.persist(comment)
            
            self.em.commit()
            return True
            
        except Exception as e:
            self.em.rollback()
            raise Exception(f"Soft delete failed: {str(e)}")
```

:::info[EntityManager Performance Tips]
Optimize EntityManager usage:
- **Use flush() sparingly** - only when you need generated IDs
- **Batch operations** in transactions for better performance
- **Clear entity manager** periodically in long-running processes
- **Use lazy loading** for optional relationships
- **Monitor memory usage** with large entity sets
- **Configure connection pooling** appropriately
:::

### Transaction Isolation Levels

```python
class TransactionService:
    """
    Service demonstrating different transaction isolation levels
    """
    
    def __init__(self, entity_manager: EntityManager):
        self.em = entity_manager
    
    def read_committed_operation(self):
        """
        Default isolation level - prevents dirty reads
        """
        self.em.set_isolation_level('READ_COMMITTED')
        try:
            self.em.begin_transaction()
            # Your operations here
            self.em.commit()
        except Exception:
            self.em.rollback()
    
    def serializable_operation(self):
        """
        Highest isolation level - prevents all phenomena
        Use for critical financial operations
        """
        self.em.set_isolation_level('SERIALIZABLE')
        try:
            self.em.begin_transaction()
            # Critical operations requiring full isolation
            self.em.commit()
        except Exception:
            self.em.rollback()
    
    def read_uncommitted_analytics(self):
        """
        Lowest isolation level - allows dirty reads
        Suitable for analytics where speed > accuracy
        """
        self.em.set_isolation_level('READ_UNCOMMITTED')
        # Analytics queries that can tolerate inconsistency
        return self.em.query("SELECT COUNT(*) FROM users")
```

## Database Commands

Framefox provides a comprehensive set of database commands through the CLI to manage your database lifecycle. These commands handle database creation, migrations, schema management, and maintenance operations.

:::tip[Command Syntax]
All database commands follow the pattern:
```bash
framefox database:<command> [options]
```
Use `framefox database --help` to see all available commands.
:::

### Core Database Commands

#### Create Database

Initialize a new database based on your configuration:

```bash
# Create the database if it doesn't exist
framefox database:create

# Output example:
# ✓ Database 'app.db' created successfully
# ✓ Ready for migrations and table creation
```

This command:
- Creates the database file (SQLite) or database schema (PostgreSQL/MySQL)
- Verifies database connectivity
- Prepares the database for table creation via migrations

#### Drop Database

Remove the entire database and all its data:

```bash
# Drop the database (use with caution!)
framefox database:drop

# Output example:
# ⚠ Warning: This will permanently delete all data
# ✓ Database 'app.db' dropped successfully
```

:::danger[Data Loss Warning]
The `drop` command permanently deletes all database data. Always backup your data before using this command in production environments.
:::

### Migration Commands

#### Create Migration

Generate a new migration file to track schema changes:

```bash
# Create a new migration with descriptive name
framefox database:create-migration

# Output example:
# ✓ Migration created: migrations/versions/20240603_152345_migration.py
# ✓ Edit the file to define your schema changes
```

The migration file structure:
```python
"""Migration description

Revision ID: 20240603_152345
Revises: 
Create Date: 2024-06-03 15:23:45.123456
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '20240603_152345'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Apply schema changes"""
    pass

def downgrade():
    """Revert schema changes"""
    pass
```

#### Apply Migrations

Run pending migrations to update your database schema:

```bash
# Apply all pending migrations
framefox database:upgrade

# Output example:
# ✓ Running migration 20240603_152345 -> 20240603_152400
# ✓ Database schema updated successfully
# ✓ All migrations applied
```

#### Rollback Migrations

Revert database schema to a previous state:

```bash
# Rollback to previous migration
framefox database:downgrade

# Output example:
# ✓ Rolling back migration 20240603_152400 -> 20240603_152345
# ✓ Database schema reverted successfully
```

#### Check Migration Status

View the current migration state and history:

```bash
# Show migration status
framefox database:status

# Output example:
# Current revision: 20240603_152400
# 
# Migration History:
# ✓ 20240603_152345 - Create users table
# ✓ 20240603_152400 - Add user profiles (current)
# 
# Pending migrations: None
```

### Database Maintenance Commands

#### Copy Database

Create a backup copy of your database:

```bash
# Copy database to backup location
framefox database:copy

# Output example:
# ✓ Database copied successfully
# ✓ Backup saved to: backups/app_backup_20240603_152345.db
```

This command:
- Creates a complete database backup
- Includes all tables, data, and indexes
- Generates timestamped backup files
- Verifies backup integrity

#### Clear Metadata

Clean up database metadata and temporary files:

```bash
# Clear database metadata cache
framefox database:clear-metadata

# Output example:
# ✓ Metadata cache cleared
# ✓ Temporary files removed
# ✓ Database optimized
```

Use this command when:
- Encountering metadata conflicts
- After major schema changes
- For database maintenance and optimization

### Advanced Command Usage

#### Environment-Specific Operations

Run database commands for specific environments:

```bash
# Production environment
DATABASE_URL=postgresql://prod_user:pass@prod-host:5432/prod_db framefox database:status

# Development environment
DATABASE_URL=sqlite:///dev.db framefox database:create

# Testing environment
DATABASE_URL=sqlite:///:memory: framefox database:upgrade
```

#### Command Chaining for Development Workflow

Common development patterns:

```bash
# Fresh database setup
framefox database:drop && framefox database:create && framefox database:upgrade

# Reset database with fresh data
framefox database:drop && framefox database:create && framefox database:upgrade && python seed_data.py

# Safe deployment workflow
framefox database:copy && framefox database:upgrade
```

#### Automation and CI/CD Integration

Database commands in automated environments:

```bash
# CI/CD pipeline example
#!/bin/bash
set -e

echo "Setting up test database..."
framefox database:create
framefox database:upgrade

echo "Running tests..."
python -m pytest

echo "Cleaning up..."
framefox database:drop
```

:::info[Best Practices]
Follow these guidelines for database command usage:
- **Always backup** before running destructive operations
- **Test migrations** in development before production
- **Use descriptive names** for migration files
- **Review migration files** before applying them
- **Monitor migration performance** on large datasets
- **Keep migrations small** and focused on single changes
- **Document complex migrations** with clear comments
:::

:::warning[Production Considerations]
In production environments:
- **Schedule migrations** during maintenance windows
- **Monitor migration progress** for large datasets
- **Have rollback plans** for failed migrations
- **Test performance impact** before deployment
- **Backup before** any schema changes
- **Use connection pooling** for better performance
:::

## Database Migrations

Database migrations provide version control for your database schema, allowing you to evolve your database structure over time while maintaining data integrity and enabling team collaboration.

### Understanding Migrations

Framefox uses Alembic for database migrations, providing powerful schema management capabilities:

:::info[Migration Benefits]
Migrations provide:
- **Version Control**: Track database schema changes over time
- **Team Collaboration**: Share schema changes across development teams
- **Environment Consistency**: Ensure identical database structure across environments
- **Rollback Capability**: Revert problematic changes safely
- **Data Preservation**: Modify schema while preserving existing data
- **Automated Deployment**: Include schema updates in deployment processes
:::

### Creating Migrations

#### Generate Migration from Changes

Create a migration automatically by detecting changes in your entities:

```bash
# Generate migration with descriptive name
framefox database create-migration "add_user_profile_table"

# Generate migration with auto-detected changes
framefox database create-migration "update_post_indexes" --auto-detect

# Create empty migration for custom SQL
framefox database create-migration "add_custom_functions" --empty
```

#### Manual Migration Creation

For complex schema changes, create migrations manually:

```python
# migrations/versions/20240115_001_create_users_table.py
"""Create users table with comprehensive fields

Revision ID: 20240115_001
Revises: 
Create Date: 2024-01-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# Revision identifiers
revision = '20240115_001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Apply the migration - create users table"""
    
    # Create users table with comprehensive schema
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, 
                 server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, 
                 server_default=func.now(), onupdate=func.now()),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username', name='uq_users_username'),
        sa.UniqueConstraint('email', name='uq_users_email'),
        
        # Check constraints for validation
        sa.CheckConstraint(
            "email LIKE '%@%.%'", 
            name='ck_users_email_format'
        ),
        sa.CheckConstraint(
            "length(username) >= 3", 
            name='ck_users_username_length'
        )
    )
    
    # Create indexes for performance
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_active_created', 'users', ['is_active', 'created_at'])
    op.create_index('ix_users_last_login', 'users', ['last_login'])
    
    # Create partial index for active users only (PostgreSQL)
    # op.create_index('ix_users_active_only', 'users', ['id'], 
    #                postgresql_where=sa.text('is_active = true'))

def downgrade():
    """Reverse the migration - drop users table"""
    
    # Drop indexes first
    op.drop_index('ix_users_last_login', table_name='users')
    op.drop_index('ix_users_active_created', table_name='users')
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    
    # Drop the table
    op.drop_table('users')
```

#### Advanced Migration with Data Transformation

```python
# migrations/versions/20240115_002_migrate_user_data.py
"""Migrate user data to new profile structure

Revision ID: 20240115_002
Revises: 20240115_001
Create Date: 2024-01-15 14:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func, table, column

revision = '20240115_002'
down_revision = '20240115_001'
branch_labels = None
depends_on = None

def upgrade():
    """Migrate existing user data to new profile structure"""
    
    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(20)),
        sa.Column('address', sa.Text()),
        sa.Column('date_of_birth', sa.Date()),
        sa.Column('website', sa.String(255)),
        sa.Column('linkedin_url', sa.String(255)),
        sa.Column('github_url', sa.String(255)),
        sa.Column('timezone', sa.String(50), default='UTC'),
        sa.Column('language', sa.String(5), default='en'),
        sa.Column('email_notifications', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=func.now()),
        
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', name='uq_user_profiles_user_id')
    )
    
    # Create indexes
    op.create_index('ix_user_profiles_user_id', 'user_profiles', ['user_id'])
    
    # Migrate existing data if any
    connection = op.get_bind()
    
    # Get existing users
    users_table = table('users',
        column('id', sa.Integer),
        column('first_name', sa.String),
        column('last_name', sa.String)
    )
    
    profiles_table = table('user_profiles',
        column('user_id', sa.Integer),
        column('timezone', sa.String),
        column('language', sa.String),
        column('email_notifications', sa.Boolean)
    )
    
    # Insert default profiles for existing users
    users = connection.execute(sa.select(users_table.c.id)).fetchall()
    
    if users:
        profile_data = [
            {
                'user_id': user.id,
                'timezone': 'UTC',
                'language': 'en',
                'email_notifications': True
            }
            for user in users
        ]
        
        op.bulk_insert(profiles_table, profile_data)

def downgrade():
    """Reverse the migration"""
    op.drop_table('user_profiles')
```

### Migration Commands

#### Essential Migration Commands

```bash
# Check current migration status
framefox database status

# Apply all pending migrations
framefox database migrate

# Migrate to specific revision
framefox database migrate --revision 20240115_001

# Downgrade to previous revision  
framefox database downgrade --revision 20240114_005

# Show migration history
framefox database history

# Show current revision
framefox database current

# Validate migration scripts
framefox database check

# Generate SQL for migration (don't execute)
framefox database migrate --sql > migration.sql
```

#### Advanced Migration Operations

```bash
# Create database from scratch with all migrations
framefox database create

# Drop all tables and recreate
framefox database reset

# Reset to specific revision
framefox database reset --revision 20240115_001

# Stamp database as specific revision (without running migrations)
framefox database stamp 20240115_002

# Merge multiple migration heads
framefox database merge --message "merge branches"

# Show pending migrations
framefox database show --pending

# Validate all migrations can be applied and reversed
framefox database test-cycle
```

:::warning[Migration Safety]
Follow these migration best practices:
- **Test migrations thoroughly** in development environments
- **Backup production data** before applying migrations
- **Keep migrations small and focused** on single changes
- **Use transactions** for data migrations when possible
- **Avoid destructive operations** without confirmation
- **Document complex migrations** with clear comments
- **Test rollback scenarios** before production deployment
:::

### Migration Best Practices

#### Safe Schema Changes

```python
# migrations/versions/20240115_003_safe_column_addition.py
"""Safely add new column with default value

This migration demonstrates safe practices for adding columns
without causing downtime or data loss.
"""

def upgrade():
    """Add status column with safe default"""
    
    # Add column with default value (safe operation)
    op.add_column('posts', 
        sa.Column('status', sa.String(20), 
                 nullable=False, 
                 server_default='draft')
    )
    
    # Update existing records if needed
    connection = op.get_bind()
    connection.execute(
        "UPDATE posts SET status = 'published' WHERE published_at IS NOT NULL"
    )
    
    # Add index after data is populated
    op.create_index('ix_posts_status', 'posts', ['status'])

def downgrade():
    """Safely remove the status column"""
    op.drop_index('ix_posts_status', table_name='posts')
    op.drop_column('posts', 'status')
```

#### Data Migration Patterns

```python
# migrations/versions/20240115_004_data_migration.py
"""Data migration with error handling and progress tracking"""

def upgrade():
    """Migrate user data with proper error handling"""
    
    connection = op.get_bind()
    
    # Get count for progress tracking
    result = connection.execute("SELECT COUNT(*) FROM users")
    total_users = result.scalar()
    
    print(f"Migrating {total_users} users...")
    
    # Process in batches to avoid memory issues
    batch_size = 1000
    processed = 0
    
    while processed < total_users:
        # Get batch of users
        users = connection.execute(f"""
            SELECT id, email, first_name, last_name 
            FROM users 
            ORDER BY id 
            LIMIT {batch_size} OFFSET {processed}
        """).fetchall()
        
        if not users:
            break
        
        # Process each user
        for user in users:
            try:
                # Complex data transformation logic here
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                
                if full_name:
                    connection.execute(
                        "UPDATE users SET display_name = ? WHERE id = ?",
                        (full_name, user.id)
                    )
                else:
                    # Use email username as fallback
                    username = user.email.split('@')[0]
                    connection.execute(
                        "UPDATE users SET display_name = ? WHERE id = ?",
                        (username, user.id)
                    )
                
            except Exception as e:
                print(f"Error processing user {user.id}: {e}")
                # Log error but continue processing
        
        processed += len(users)
        print(f"Processed {processed}/{total_users} users...")
    
    print("Data migration completed successfully!")

def downgrade():
    """Remove display_name column"""
    op.drop_column('users', 'display_name')
```

#### Zero-Downtime Migrations

```python
# migrations/versions/20240115_005_zero_downtime.py
"""Zero-downtime migration using staged approach"""

def upgrade():
    """Phase 1: Add new column, maintain compatibility"""
    
    # Add new column as nullable first
    op.add_column('users', 
        sa.Column('new_email_format', sa.String(320), nullable=True)
    )
    
    # Note: In production, you would:
    # 1. Deploy this migration
    # 2. Update application code to populate both columns
    # 3. Run data migration to populate new column
    # 4. Update application to use new column
    # 5. Deploy final migration to remove old column

def downgrade():
    """Remove new column"""
    op.drop_column('users', 'new_email_format')
```

:::tip[Migration Strategies]
Choose appropriate migration strategies:
- **Single-step migrations**: For development and staging
- **Multi-phase migrations**: For zero-downtime production deployments
- **Feature flags**: Control when new schema features are used
- **Blue-green deployments**: Coordinate schema changes with application deployments
- **Shadow tables**: Test migrations on copies before applying to live data
:::

## Advanced Querying & Performance

Framefox provides multiple approaches to database querying, from simple repository methods to complex raw SQL, along with powerful optimization techniques for high-performance applications.

### Query Builder Pattern

The Query Builder provides a fluent interface for constructing complex queries programmatically:

```python
from framefox.core.orm.query_builder import QueryBuilder
from framefox.core.orm.repository import Repository
from src.entity.user import User
from typing import List, Dict, Any

class AdvancedUserRepository(Repository):
    """
    Repository demonstrating advanced querying techniques
    with the Query Builder and performance optimizations
    """
    
    def __init__(self):
        super().__init__(User)
    
    def advanced_user_search(self, filters: Dict[str, Any]) -> List[User]:
        """
        Complex user search with dynamic filtering using Query Builder
        Demonstrates flexible query construction based on provided filters
        """
        qb = QueryBuilder(self.entity_class)
        
        # Text search with multiple fields
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            qb.where_group(
                qb.where('username', 'LIKE', search_term)
                .or_where('email', 'LIKE', search_term)
                .or_where('first_name', 'LIKE', search_term)
                .or_where('last_name', 'LIKE', search_term)
            )
        
        # Exact matches
        if filters.get('email'):
            qb.where('email', '=', filters['email'])
        
        if filters.get('username'):
            qb.where('username', '=', filters['username'])
        
        # Boolean filters
        if filters.get('is_active') is not None:
            qb.where('is_active', '=', filters['is_active'])
        
        if filters.get('is_admin') is not None:
            qb.where('is_admin', '=', filters['is_admin'])
        
        if filters.get('is_verified') is not None:
            qb.where('is_verified', '=', filters['is_verified'])
        
        # Date range filters
        if filters.get('created_after'):
            qb.where('created_at', '>=', filters['created_after'])
        
        if filters.get('created_before'):
            qb.where('created_at', '<=', filters['created_before'])
        
        if filters.get('last_login_after'):
            qb.where('last_login', '>=', filters['last_login_after'])
        
        # Age-based filtering (calculated field)
        if filters.get('min_age'):
            from datetime import datetime, timedelta
            max_birth_date = datetime.now() - timedelta(days=filters['min_age'] * 365)
            qb.join('user_profiles', 'users.id', '=', 'user_profiles.user_id')
            qb.where('user_profiles.date_of_birth', '<=', max_birth_date)
        
        # Location-based filtering
        if filters.get('city'):
            qb.join('user_profiles', 'users.id', '=', 'user_profiles.user_id')
            qb.where('user_profiles.address', 'LIKE', f"%{filters['city']}%")
        
        # Role-based filtering
        if filters.get('roles'):
            role_list = filters['roles'] if isinstance(filters['roles'], list) else [filters['roles']]
            qb.join('user_roles', 'users.id', '=', 'user_roles.user_id')
            qb.join('roles', 'user_roles.role_id', '=', 'roles.id')
            qb.where_in('roles.name', role_list)
            qb.where('user_roles.is_active', '=', True)
            qb.distinct()
        
        # Post count filtering
        if filters.get('min_posts'):
            qb.having_raw('posts_count >= ?', [filters['min_posts']])
            qb.join('posts', 'users.id', '=', 'posts.user_id', 'LEFT')
            qb.group_by('users.id')
            qb.select_raw('users.*, COUNT(posts.id) as posts_count')
        
        # Sorting options
        sort_field = filters.get('sort_by', 'created_at')
        sort_order = filters.get('sort_order', 'DESC')
        
        if sort_field == 'full_name':
            qb.order_by_raw('COALESCE(first_name, "") || " " || COALESCE(last_name, "")', sort_order)
        elif sort_field == 'posts_count':
            qb.order_by('posts_count', sort_order)
        else:
            qb.order_by(sort_field, sort_order)
        
        # Pagination
        if filters.get('limit'):
            qb.limit(filters['limit'])
        
        if filters.get('offset'):
            qb.offset(filters['offset'])
        
        return qb.get()
    
    def get_user_analytics_query(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """
        Complex analytics query using raw SQL for performance
        Demonstrates advanced SQL techniques and window functions
        """
        conditions = []
        params = []
        
        if date_from:
            conditions.append("u.created_at >= ?")
            params.append(date_from)
        
        if date_to:
            conditions.append("u.created_at <= ?")
            params.append(date_to)
        
        where_clause = " AND " + " AND ".join(conditions) if conditions else ""
        
        sql = f"""
        WITH user_stats AS (
            SELECT 
                u.*,
                COUNT(DISTINCT p.id) as posts_count,
                COUNT(DISTINCT c.id) as comments_count,
                COUNT(DISTINCT l.id) as likes_received,
                AVG(pr.rating) as avg_rating,
                ROW_NUMBER() OVER (ORDER BY COUNT(DISTINCT p.id) DESC) as post_rank,
                RANK() OVER (PARTITION BY DATE(u.created_at) ORDER BY u.id) as daily_registration_rank
            FROM users u
            LEFT JOIN posts p ON u.id = p.user_id AND p.status = 'published'
            LEFT JOIN comments c ON p.id = c.post_id
            LEFT JOIN post_likes l ON p.id = l.post_id
            LEFT JOIN post_ratings pr ON p.id = pr.post_id
            WHERE u.is_active = 1 {where_clause}
            GROUP BY u.id
        ),
        activity_metrics AS (
            SELECT 
                us.*,
                CASE 
                    WHEN us.posts_count >= 10 THEN 'High'
                    WHEN us.posts_count >= 3 THEN 'Medium'
                    ELSE 'Low'
                END as activity_level,
                CASE 
                    WHEN us.last_login >= DATE('now', '-7 days') THEN 'Active'
                    WHEN us.last_login >= DATE('now', '-30 days') THEN 'Inactive'
                    ELSE 'Dormant'
                END as engagement_status
            FROM user_stats us
        )
        SELECT 
            am.*,
            NTILE(4) OVER (ORDER BY am.posts_count) as posts_quartile,
            LAG(am.posts_count) OVER (ORDER BY am.created_at) as prev_user_posts,
            LEAD(am.posts_count) OVER (ORDER BY am.created_at) as next_user_posts
        FROM activity_metrics am
        ORDER BY am.posts_count DESC, am.created_at DESC
        """
        
        return self.query(sql, params)
    
    def get_cohort_analysis(self, cohort_period: str = 'month') -> List[Dict[str, Any]]:
        """
        Cohort analysis showing user retention over time
        Advanced analytics using window functions and date manipulation
        """
        if cohort_period == 'week':
            date_format = '%Y-%W'
            interval_sql = "DATE(created_at, 'weekday 0', '-6 days')"
        else:  # month
            date_format = '%Y-%m'
            interval_sql = "DATE(created_at, 'start of month')"
        
        sql = f"""
        WITH user_cohorts AS (
            SELECT 
                u.id,
                {interval_sql} as cohort_period,
                strftime('{date_format}', u.created_at) as cohort_label,
                u.created_at,
                u.last_login
            FROM users u
            WHERE u.is_active = 1
        ),
        cohort_sizes AS (
            SELECT 
                cohort_period,
                cohort_label,
                COUNT(*) as cohort_size
            FROM user_cohorts
            GROUP BY cohort_period, cohort_label
        ),
        user_activity AS (
            SELECT 
                uc.cohort_period,
                uc.cohort_label,
                uc.id as user_id,
                CASE 
                    WHEN uc.last_login >= DATE('now', '-7 days') THEN 'week_1'
                    WHEN uc.last_login >= DATE('now', '-30 days') THEN 'month_1'
                    WHEN uc.last_login >= DATE('now', '-90 days') THEN 'month_3'
                    ELSE 'inactive'
                END as retention_period
            FROM user_cohorts uc
        ),
        retention_data AS (
            SELECT 
                ua.cohort_period,
                ua.cohort_label,
                ua.retention_period,
                COUNT(*) as retained_users
            FROM user_activity ua
            WHERE ua.retention_period != 'inactive'
            GROUP BY ua.cohort_period, ua.cohort_label, ua.retention_period
        )
        SELECT 
            cs.cohort_label,
            cs.cohort_size,
            rd.retention_period,
            rd.retained_users,
            ROUND(rd.retained_users * 100.0 / cs.cohort_size, 2) as retention_rate
        FROM cohort_sizes cs
        LEFT JOIN retention_data rd ON cs.cohort_period = rd.cohort_period
        ORDER BY cs.cohort_label, rd.retention_period
        """
        
        return self.query(sql)
```

:::tip[Query Optimization Strategies]
Optimize your queries for better performance:
- **Use indexes** on frequently queried columns
- **Limit result sets** with LIMIT clauses
- **Use EXISTS instead of IN** for subqueries when possible
- **Avoid SELECT *** in production code
- **Use JOINs instead of separate queries** to prevent N+1 problems
- **Profile queries** with EXPLAIN to understand execution plans
- **Consider denormalization** for frequently accessed data
:::

### Raw SQL for Complex Operations

For maximum performance and flexibility, use raw SQL for complex operations:

```python
class AnalyticsRepository:
    """
    Specialized repository for complex analytics queries
    Demonstrates advanced SQL techniques and performance optimization
    """
    
    def __init__(self, entity_manager):
        self.em = entity_manager
    
    def get_comprehensive_user_metrics(self) -> Dict[str, Any]:
        """
        Comprehensive user metrics using advanced SQL features
        Includes CTEs, window functions, and complex aggregations
        """
        sql = """
        WITH monthly_registrations AS (
            SELECT 
                strftime('%Y-%m', created_at) as month,
                COUNT(*) as new_users,
                LAG(COUNT(*)) OVER (ORDER BY strftime('%Y-%m', created_at)) as prev_month_users
            FROM users
            WHERE created_at >= DATE('now', '-12 months')
            GROUP BY strftime('%Y-%m', created_at)
        ),
        user_engagement AS (
            SELECT 
                COUNT(CASE WHEN last_login >= DATE('now', '-1 days') THEN 1 END) as daily_active,
                COUNT(CASE WHEN last_login >= DATE('now', '-7 days') THEN 1 END) as weekly_active,
                COUNT(CASE WHEN last_login >= DATE('now', '-30 days') THEN 1 END) as monthly_active,
                COUNT(*) as total_users,
                AVG(CASE WHEN last_login IS NOT NULL THEN 
                    JULIANDAY('now') - JULIANDAY(last_login) 
                END) as avg_days_since_login
            FROM users
            WHERE is_active = 1
        ),
        content_metrics AS (
            SELECT 
                COUNT(DISTINCT p.id) as total_posts,
                COUNT(DISTINCT p.user_id) as active_authors,
                AVG(LENGTH(p.content)) as avg_post_length,
                COUNT(CASE WHEN p.created_at >= DATE('now', '-7 days') THEN 1 END) as posts_this_week
            FROM posts p
            WHERE p.status = 'published'
        )
        SELECT 
            mr.month,
            mr.new_users,
            mr.prev_month_users,
            ROUND(
                (mr.new_users - COALESCE(mr.prev_month_users, 0)) * 100.0 / 
                NULLIF(mr.prev_month_users, 0), 2
            ) as growth_rate,
            ue.daily_active,
            ue.weekly_active,
            ue.monthly_active,
            ue.total_users,
            ROUND(ue.avg_days_since_login, 1) as avg_days_since_login,
            cm.total_posts,
            cm.active_authors,
            ROUND(cm.avg_post_length, 0) as avg_post_length,
            cm.posts_this_week
        FROM monthly_registrations mr
        CROSS JOIN user_engagement ue
        CROSS JOIN content_metrics cm
        ORDER BY mr.month DESC
        """
        
        return self.em.execute(sql).fetchall()
    
    def get_user_segmentation(self) -> List[Dict[str, Any]]:
        """
        User segmentation analysis for marketing and engagement
        Uses percentiles and statistical functions
        """
        sql = """
        WITH user_activity_scores AS (
            SELECT 
                u.id,
                u.username,
                u.email,
                u.created_at,
                u.last_login,
                COUNT(DISTINCT p.id) as posts_count,
                COUNT(DISTINCT c.id) as comments_count,
                COUNT(DISTINCT l.id) as likes_given,
                COALESCE(SUM(pv.view_count), 0) as total_views_received,
                JULIANDAY('now') - JULIANDAY(u.last_login) as days_since_login,
                JULIANDAY('now') - JULIANDAY(u.created_at) as account_age_days,
                -- Calculate engagement score
                (
                    COUNT(DISTINCT p.id) * 3 +                    -- Posts weight: 3
                    COUNT(DISTINCT c.id) * 1 +                    -- Comments weight: 1
                    COUNT(DISTINCT l.id) * 0.5 +                  -- Likes weight: 0.5
                    COALESCE(SUM(pv.view_count), 0) * 0.01        -- Views weight: 0.01
                ) as engagement_score
            FROM users u
            LEFT JOIN posts p ON u.id = p.user_id AND p.status = 'published'
            LEFT JOIN comments c ON u.id = c.user_id
            LEFT JOIN post_likes l ON u.id = l.user_id
            LEFT JOIN post_views pv ON p.id = pv.post_id
            WHERE u.is_active = 1
            GROUP BY u.id
        ),
        score_percentiles AS (
            SELECT 
                *,
                NTILE(5) OVER (ORDER BY engagement_score) as engagement_quintile,
                PERCENT_RANK() OVER (ORDER BY engagement_score) as engagement_percentile,
                CASE 
                    WHEN days_since_login <= 7 THEN 'Active'
                    WHEN days_since_login <= 30 THEN 'Occasional'
                    WHEN days_since_login <= 90 THEN 'Inactive'
                    ELSE 'Dormant'
                END as activity_status,
                CASE 
                    WHEN account_age_days <= 30 THEN 'New'
                    WHEN account_age_days <= 180 THEN 'Growing'
                    WHEN account_age_days <= 365 THEN 'Established'
                    ELSE 'Veteran'
                END as user_lifecycle
            FROM user_activity_scores
        )
        SELECT 
            sp.*,
            CASE 
                WHEN sp.engagement_quintile = 5 AND sp.activity_status = 'Active' THEN 'Champion'
                WHEN sp.engagement_quintile >= 4 AND sp.activity_status IN ('Active', 'Occasional') THEN 'Loyal'
                WHEN sp.engagement_quintile >= 3 AND sp.activity_status = 'Active' THEN 'Potential Loyal'
                WHEN sp.engagement_quintile <= 2 AND sp.activity_status = 'Active' THEN 'New Customer'
                WHEN sp.engagement_quintile >= 3 AND sp.activity_status = 'Inactive' THEN 'At Risk'
                WHEN sp.engagement_quintile <= 2 AND sp.activity_status = 'Inactive' THEN 'Cannot Lose'
                ELSE 'Others'
            END as user_segment
        FROM score_percentiles sp
        ORDER BY sp.engagement_score DESC
        """
        
        return self.em.execute(sql).fetchall()
    
    def get_content_performance_report(self, date_from: str = None, date_to: str = None) -> List[Dict[str, Any]]:
        """
        Content performance analysis with trend detection
        """
        date_filter = ""
        params = []
        
        if date_from:
            date_filter += " AND p.published_at >= ?"
            params.append(date_from)
        
        if date_to:
            date_filter += " AND p.published_at <= ?"
            params.append(date_to)
        
        sql = f"""
        WITH post_metrics AS (
            SELECT 
                p.id,
                p.title,
                p.slug,
                p.user_id,
                u.username as author,
                p.published_at,
                p.view_count,
                COUNT(DISTINCT c.id) as comments_count,
                COUNT(DISTINCT pl.id) as likes_count,
                COUNT(DISTINCT ps.id) as shares_count,
                AVG(pr.rating) as avg_rating,
                COUNT(DISTINCT pr.id) as ratings_count,
                -- Calculate engagement rate
                (COUNT(DISTINCT c.id) + COUNT(DISTINCT pl.id) + COUNT(DISTINCT ps.id)) * 100.0 / 
                NULLIF(p.view_count, 0) as engagement_rate,
                -- Calculate reading time (200 words per minute)
                ROUND(LENGTH(p.content) / 5.0 / 200.0, 1) as estimated_reading_time
            FROM posts p
            INNER JOIN users u ON p.user_id = u.id
            LEFT JOIN comments c ON p.id = c.post_id
            LEFT JOIN post_likes pl ON p.id = pl.post_id
            LEFT JOIN post_shares ps ON p.id = ps.post_id
            LEFT JOIN post_ratings pr ON p.id = pr.post_id
            WHERE p.status = 'published' {date_filter}
            GROUP BY p.id
        ),
        performance_ranks AS (
            SELECT 
                pm.*,
                ROW_NUMBER() OVER (ORDER BY pm.view_count DESC) as view_rank,
                ROW_NUMBER() OVER (ORDER BY pm.engagement_rate DESC) as engagement_rank,
                ROW_NUMBER() OVER (ORDER BY pm.likes_count DESC) as likes_rank,
                RANK() OVER (PARTITION BY DATE(pm.published_at) ORDER BY pm.view_count DESC) as daily_view_rank
            FROM post_metrics pm
        )
        SELECT 
            pr.*,
            CASE 
                WHEN pr.view_rank <= 10 THEN 'Top Performer'
                WHEN pr.engagement_rank <= 20 THEN 'High Engagement'
                WHEN pr.view_count < 100 THEN 'Needs Promotion'
                ELSE 'Average'
            END as performance_category
        FROM performance_ranks pr
        ORDER BY pr.view_count DESC, pr.engagement_rate DESC
        """
        
        return self.em.execute(sql, params).fetchall()
```

:::warning[Raw SQL Considerations]
When using raw SQL:
- **Parameterize queries** to prevent SQL injection
- **Test queries thoroughly** across different database engines
- **Document complex queries** with clear comments
- **Consider maintainability** vs performance benefits
- **Use appropriate data types** in result processing
- **Handle database-specific syntax** carefully
:::

### Query Performance Monitoring

```python
import time
import logging
from functools import wraps

class QueryPerformanceMonitor:
    """
    Monitor and log query performance for optimization
    """
    
    def __init__(self, entity_manager, logger=None):
        self.em = entity_manager
        self.logger = logger or logging.getLogger(__name__)
        self.slow_query_threshold = 1.0  # seconds
    
    def monitor_query(self, query_name: str):
        """Decorator to monitor query performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Log performance metrics
                    if execution_time > self.slow_query_threshold:
                        self.logger.warning(
                            f"Slow query detected: {query_name} took {execution_time:.3f}s"
                        )
                    else:
                        self.logger.info(
                            f"Query {query_name} executed in {execution_time:.3f}s"
                        )
                    
                    return result
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.logger.error(
                        f"Query {query_name} failed after {execution_time:.3f}s: {str(e)}"
                    )
                    raise
                    
            return wrapper
        return decorator
    
    def analyze_query_plan(self, sql: str, params: List = None) -> Dict[str, Any]:
        """Analyze query execution plan for optimization"""
        explain_sql = f"EXPLAIN QUERY PLAN {sql}"
        
        try:
            plan = self.em.execute(explain_sql, params or []).fetchall()
            
            analysis = {
                'query': sql,
                'execution_plan': plan,
                'recommendations': []
            }
            
            # Analyze plan for common issues
            plan_text = str(plan).lower()
            
            if 'scan' in plan_text and 'using index' not in plan_text:
                analysis['recommendations'].append("Consider adding indexes for table scans")
            
            if 'temp b-tree' in plan_text:
                analysis['recommendations'].append("Query may benefit from composite indexes")
            
            if 'nested loop' in plan_text:
                analysis['recommendations'].append("Large nested loops may need optimization")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze query plan: {str(e)}")
            return {'error': str(e)}
```

## Performance Optimization & Caching

Performance optimization is crucial for scalable applications. Framefox provides multiple layers of optimization including intelligent caching, connection pooling, and query optimization strategies.

### Multi-Level Caching Strategy

Implement a comprehensive caching strategy for maximum performance:

```python
from framefox.core.cache.cache_manager import CacheManager
from framefox.core.orm.repository import Repository
from src.entity.user import User
from typing import Optional, List, Dict, Any
import json
import hashlib
from datetime import datetime, timedelta

class CachedUserRepository(Repository):
    """
    Repository with intelligent multi-level caching
    Demonstrates various caching patterns and strategies
    """
    
    def __init__(self, cache_manager: CacheManager):
        super().__init__(User)
        self.cache = cache_manager
        self.l1_cache = {}  # In-memory cache for request-level caching
        self.cache_ttl = {
            'user': 3600,      # 1 hour for user data
            'list': 1800,      # 30 minutes for lists
            'search': 900,     # 15 minutes for search results
            'stats': 300       # 5 minutes for statistics
        }
    
    def find_with_cache(self, user_id: int) -> Optional[User]:
        """
        Multi-level cache lookup with intelligent invalidation
        L1: In-memory cache (request level)
        L2: Redis/Memcached (application level)
        L3: Database (persistent storage)
        """
        # Level 1: Check in-memory cache first
        l1_key = f"user_l1:{user_id}"
        if l1_key in self.l1_cache:
            return self.l1_cache[l1_key]
        
        # Level 2: Check distributed cache
        cache_key = f"user:{user_id}"
        cached_user = self.cache.get(cache_key)
        
        if cached_user:
            user = self._deserialize_user(cached_user)
            # Store in L1 cache for subsequent requests
            self.l1_cache[l1_key] = user
            return user
        
        # Level 3: Load from database
        user = self.find(user_id)
        if user:
            # Cache in both levels
            serialized = self._serialize_user(user)
            self.cache.set(cache_key, serialized, self.cache_ttl['user'])
            self.l1_cache[l1_key] = user
        
        return user
    
    def search_users_cached(self, query: str, filters: Dict = None, 
                           limit: int = 50) -> List[User]:
        """
        Cached search with smart cache key generation
        Uses hash of search parameters for consistent cache keys
        """
        # Generate cache key from search parameters
        search_params = {
            'query': query.lower().strip(),
            'filters': filters or {},
            'limit': limit
        }
        
        cache_key = self._generate_search_cache_key(search_params)
        
        # Try cache first
        cached_results = self.cache.get(cache_key)
        if cached_results:
            return [self._deserialize_user(user_data) for user_data in json.loads(cached_results)]
        
        # Execute search
        results = self.search_users(query, limit)
        
        # Cache results
        serialized_results = json.dumps([self._serialize_user(user) for user in results])
        self.cache.set(cache_key, serialized_results, self.cache_ttl['search'])
        
        return results
    
    def get_user_statistics_cached(self) -> Dict[str, Any]:
        """Cached statistics with background refresh"""
        cache_key = "user_stats:global"
        
        # Try to get fresh stats
        stats = self.cache.get(cache_key)
        if stats:
            return json.loads(stats)
        
        # Generate stats
        stats = self.get_user_statistics()
        
        # Cache with shorter TTL for frequently changing data
        self.cache.set(cache_key, json.dumps(stats), self.cache_ttl['stats'])
        
        # Schedule background refresh for popular data
        self._schedule_background_refresh(cache_key, 'user_statistics')
        
        return stats
    
    def invalidate_user_cache(self, user_id: int, cascade: bool = True):
        """
        Intelligent cache invalidation with cascade support
        Removes related cache entries to maintain consistency
        """
        # Clear specific user cache
        user_key = f"user:{user_id}"
        self.cache.delete(user_key)
        
        # Clear L1 cache
        l1_key = f"user_l1:{user_id}"
        if l1_key in self.l1_cache:
            del self.l1_cache[l1_key]
        
        if cascade:
            # Invalidate related caches
            patterns_to_clear = [
                f"user_posts:{user_id}:*",     # User's posts
                f"user_roles:{user_id}",       # User's roles
                "user_stats:*",                # Global statistics
                "search:*"                     # Search results
            ]
            
            for pattern in patterns_to_clear:
                self.cache.delete_pattern(pattern)
    
    def warm_cache(self, user_ids: List[int] = None, popular_searches: List[str] = None):
        """
        Proactively warm cache with frequently accessed data
        Improves response times for common operations
        """
        # Warm user cache
        if user_ids:
            for user_id in user_ids:
                if not self.cache.exists(f"user:{user_id}"):
                    user = self.find(user_id)
                    if user:
                        cache_key = f"user:{user_id}"
                        self.cache.set(cache_key, self._serialize_user(user), self.cache_ttl['user'])
        
        # Warm search cache
        if popular_searches:
            for search_term in popular_searches:
                search_params = {'query': search_term.lower().strip(), 'filters': {}, 'limit': 20}
                cache_key = self._generate_search_cache_key(search_params)
                
                if not self.cache.exists(cache_key):
                    results = self.search_users(search_term, 20)
                    serialized = json.dumps([self._serialize_user(user) for user in results])
                    self.cache.set(cache_key, serialized, self.cache_ttl['search'])
        
        # Warm statistics cache
        stats_key = "user_stats:global"
        if not self.cache.exists(stats_key):
            stats = self.get_user_statistics()
            self.cache.set(stats_key, json.dumps(stats), self.cache_ttl['stats'])
    
    def _generate_search_cache_key(self, search_params: Dict) -> str:
        """Generate consistent cache key for search parameters"""
        param_string = json.dumps(search_params, sort_keys=True)
        hash_digest = hashlib.md5(param_string.encode()).hexdigest()
        return f"search:{hash_digest}"
    
    def _serialize_user(self, user: User) -> str:
        """Convert user object to JSON for caching"""
        return json.dumps(user.to_dict())
    
    def _deserialize_user(self, cached_data: str) -> User:
        """Convert cached JSON back to user object"""
        data = json.loads(cached_data)
        user = User()
        for key, value in data.items():
            if key.endswith('_at') and value:
                # Convert datetime strings back to datetime objects
                setattr(user, key, datetime.fromisoformat(value))
            else:
                setattr(user, key, value)
        return user
    
    def _schedule_background_refresh(self, cache_key: str, data_type: str):
        """Schedule background cache refresh for popular data"""
        # This would integrate with your task queue (Celery, RQ, etc.)
        # For now, just log the intention
        import logging
        logging.info(f"Scheduling background refresh for {cache_key} ({data_type})")
```

:::tip[Caching Best Practices]
Implement effective caching strategies:
- **Layer your caches** (in-memory, distributed, database)
- **Use appropriate TTLs** based on data volatility
- **Implement cache warming** for frequently accessed data
- **Handle cache invalidation** properly to maintain consistency
- **Monitor cache hit rates** and adjust strategies accordingly
- **Consider cache-aside patterns** for complex data
:::

### Database Connection Optimization

```python
from framefox.core.orm.connection_manager import ConnectionManager
from typing import Dict, Any
import time
import threading

class OptimizedConnectionManager:
    """
    Advanced connection management with pooling and monitoring
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection_stats = {
            'active_connections': 0,
            'total_connections_created': 0,
            'total_queries_executed': 0,
            'average_query_time': 0.0,
            'slow_queries': 0,
            'connection_errors': 0
        }
        self.query_times = []
        self.lock = threading.Lock()
    
    def get_optimized_connection(self):
        """Get connection with automatic optimization"""
        start_time = time.time()
        
        try:
            # Get connection from pool
            connection = self._get_pooled_connection()
            
            # Monitor connection acquisition time
            acquisition_time = time.time() - start_time
            if acquisition_time > 0.1:  # 100ms threshold
                self._log_slow_connection_acquisition(acquisition_time)
            
            # Wrap connection with monitoring
            return self._wrap_connection_with_monitoring(connection)
            
        except Exception as e:
            with self.lock:
                self.connection_stats['connection_errors'] += 1
            raise
    
    def _wrap_connection_with_monitoring(self, connection):
        """Wrap connection to monitor query performance"""
        class MonitoredConnection:
            def __init__(self, conn, manager):
                self.conn = conn
                self.manager = manager
            
            def execute(self, query, params=None):
                start_time = time.time()
                
                try:
                    result = self.conn.execute(query, params)
                    execution_time = time.time() - start_time
                    
                    # Update statistics
                    with self.manager.lock:
                        self.manager.connection_stats['total_queries_executed'] += 1
                        self.manager.query_times.append(execution_time)
                        
                        # Keep only recent query times for moving average
                        if len(self.manager.query_times) > 1000:
                            self.manager.query_times = self.manager.query_times[-1000:]
                        
                        self.manager.connection_stats['average_query_time'] = (
                            sum(self.manager.query_times) / len(self.manager.query_times)
                        )
                        
                        # Track slow queries (> 1 second)
                        if execution_time > 1.0:
                            self.manager.connection_stats['slow_queries'] += 1
                            self.manager._log_slow_query(query, execution_time)
                    
                    return result
                    
                except Exception as e:
                    self.manager._log_query_error(query, str(e))
                    raise
            
            def __getattr__(self, name):
                return getattr(self.conn, name)
        
        return MonitoredConnection(connection, self)
    
    def _get_pooled_connection(self):
        """Get connection from optimized pool"""
        # Implementation would use your connection pooling library
        # This is a simplified example
        pass
    
    def _log_slow_connection_acquisition(self, acquisition_time: float):
        """Log slow connection acquisition for monitoring"""
        import logging
        logging.warning(f"Slow connection acquisition: {acquisition_time:.3f}s")
    
    def _log_slow_query(self, query: str, execution_time: float):
        """Log slow queries for optimization"""
        import logging
        logging.warning(f"Slow query detected ({execution_time:.3f}s): {query[:100]}...")
    
    def _log_query_error(self, query: str, error: str):
        """Log query errors for debugging"""
        import logging
        logging.error(f"Query error - {error}: {query[:100]}...")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get current connection statistics"""
        with self.lock:
            return self.connection_stats.copy()
    
    def optimize_pool_settings(self):
        """Dynamically optimize pool settings based on usage patterns"""
        stats = self.get_connection_stats()
        
        # Adjust pool size based on usage
        if stats['average_query_time'] > 0.5:  # 500ms average
            self._increase_pool_size()
        elif stats['connection_errors'] > 10:
            self._check_connection_health()
        
        # Log recommendations
        if stats['slow_queries'] > stats['total_queries_executed'] * 0.1:  # 10% slow queries
            import logging
            logging.warning("High number of slow queries detected. Consider optimizing queries or adding indexes.")
```

### Query Result Caching

```python
from functools import wraps
import hashlib
import json

class QueryResultCache:
    """
    Intelligent query result caching with automatic invalidation
    """
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.cache_dependencies = {}  # Track which tables affect which cache keys
    
    def cached_query(self, ttl: int = 3600, tables: List[str] = None):
        """
        Decorator for caching query results with dependency tracking
        
        Args:
            ttl: Time to live in seconds
            tables: List of tables this query depends on
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and parameters
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try cache first
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    return json.loads(cached_result)
                
                # Execute query
                result = func(*args, **kwargs)
                
                # Cache result
                self.cache.set(cache_key, json.dumps(result, default=str), ttl)
                
                # Track dependencies
                if tables:
                    self._register_cache_dependencies(cache_key, tables)
                
                return result
                
            return wrapper
        return decorator
    
    def invalidate_by_table(self, table_name: str):
        """Invalidate all cached queries that depend on a specific table"""
        if table_name in self.cache_dependencies:
            for cache_key in self.cache_dependencies[table_name]:
                self.cache.delete(cache_key)
            
            # Clean up the dependency tracking
            del self.cache_dependencies[table_name]
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate consistent cache key from function parameters"""
        # Create a consistent string representation
        key_data = {
            'function': func_name,
            'args': args,
            'kwargs': kwargs
        }
        
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        return f"query_cache:{func_name}:{key_hash[:16]}"
    
    def _register_cache_dependencies(self, cache_key: str, tables: List[str]):
        """Register which tables affect this cached query"""
        for table in tables:
            if table not in self.cache_dependencies:
                self.cache_dependencies[table] = set()
            self.cache_dependencies[table].add(cache_key)

# Usage example
class OptimizedAnalyticsRepository:
    def __init__(self, entity_manager, cache_manager):
        self.em = entity_manager
        self.query_cache = QueryResultCache(cache_manager)
    
    @QueryResultCache.cached_query(ttl=1800, tables=['users', 'posts'])  # 30 minutes
    def get_user_engagement_metrics(self) -> Dict[str, Any]:
        """Get user engagement metrics with caching"""
        sql = """
        SELECT 
            COUNT(DISTINCT u.id) as total_users,
            COUNT(DISTINCT p.id) as total_posts,
            AVG(engagement_score) as avg_engagement,
            COUNT(DISTINCT CASE WHEN u.last_login >= DATE('now', '-7 days') THEN u.id END) as active_users_7d
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
        LEFT JOIN (
            SELECT 
                user_id,
                (COUNT(posts.id) * 2 + COUNT(comments.id)) as engagement_score
            FROM users
            LEFT JOIN posts ON users.id = posts.user_id
            LEFT JOIN comments ON users.id = comments.user_id
            GROUP BY user_id
        ) engagement ON u.id = engagement.user_id
        WHERE u.is_active = 1
        """
        
        result = self.em.execute(sql).fetchone()
        return dict(result) if result else {}
    
    def invalidate_user_metrics_cache(self):
        """Manually invalidate user metrics cache"""
        self.query_cache.invalidate_by_table('users')
        self.query_cache.invalidate_by_table('posts')
```

:::warning[Performance Monitoring]
Monitor your application performance:
- **Track cache hit rates** and adjust TTLs accordingly
- **Monitor slow queries** and optimize them proactively
- **Watch connection pool utilization** to prevent bottlenecks
- **Log performance metrics** for trend analysis
- **Set up alerts** for performance degradation
- **Regular performance audits** to identify optimization opportunities
:::

### Database Index Optimization

```python
class IndexOptimizer:
    """
    Tools for analyzing and optimizing database indexes
    """
    
    def __init__(self, entity_manager):
        self.em = entity_manager
    
    def analyze_query_performance(self, sql: str, params: List = None) -> Dict[str, Any]:
        """Analyze query performance and suggest optimizations"""
        # Get query execution plan
        explain_sql = f"EXPLAIN QUERY PLAN {sql}"
        plan = self.em.execute(explain_sql, params or []).fetchall()
        
        analysis = {
            'query': sql,
            'execution_plan': plan,
            'performance_issues': [],
            'optimization_suggestions': []
        }
        
        plan_text = ' '.join([str(row) for row in plan]).lower()
        
        # Detect common performance issues
        if 'scan table' in plan_text and 'using index' not in plan_text:
            analysis['performance_issues'].append('Full table scan detected')
            analysis['optimization_suggestions'].append('Consider adding an index on filtered columns')
        
        if 'temp b-tree' in plan_text:
            analysis['performance_issues'].append('Temporary B-tree created for sorting/grouping')
            analysis['optimization_suggestions'].append('Consider adding a composite index')
        
        if 'nested loop' in plan_text and 'using index' not in plan_text:
            analysis['performance_issues'].append('Inefficient nested loop join')
            analysis['optimization_suggestions'].append('Add indexes on join columns')
        
        return analysis
    
    def suggest_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Suggest indexes based on query patterns"""
        # This would analyze actual query logs in a real implementation
        # For now, provide general recommendations
        
        suggestions = []
        
        # Get table structure
        columns_sql = f"PRAGMA table_info({table_name})"
        columns = self.em.execute(columns_sql).fetchall()
        
        for column in columns:
            column_name = column[1]  # Column name is second field
            column_type = column[2]  # Column type is third field
            
            # Suggest indexes for common query patterns
            if column_name.endswith('_id'):
                suggestions.append({
                    'type': 'foreign_key_index',
                    'columns': [column_name],
                    'reason': f'Foreign key column {column_name} likely used in joins'
                })
            
            if column_name in ['email', 'username', 'slug']:
                suggestions.append({
                    'type': 'unique_lookup_index',
                    'columns': [column_name],
                    'reason': f'Column {column_name} likely used for unique lookups'
                })
            
            if column_name.endswith('_at') and 'date' in column_type.lower():
                suggestions.append({
                    'type': 'date_range_index',
                    'columns': [column_name],
                    'reason': f'Date column {column_name} likely used in range queries'
                })
        
        # Suggest composite indexes for common patterns
        if table_name == 'posts':
            suggestions.append({
                'type': 'composite_index',
                'columns': ['status', 'published_at'],
                'reason': 'Common pattern: filter by status and sort by published date'
            })
        
        if table_name == 'users':
            suggestions.append({
                'type': 'composite_index',
                'columns': ['is_active', 'created_at'],
                'reason': 'Common pattern: filter active users and sort by registration date'
            })
        
        return suggestions
```

## Bonnes pratiques

### 1. Organisation du code

```python
# ✅ Repository spécialisé par entité
class UserRepository(Repository):
    pass

class PostRepository(Repository):
    pass

# ✅ Services pour la logique métier
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
```

### 2. Transactions

```python
# ✅ Utilisez des transactions pour les opérations complexes
def transfer_ownership(self, from_user_id: int, to_user_id: int, post_id: int):
    try:
        self.em.begin_transaction()
        
        post = self.post_repo.find(post_id)
        post.user_id = to_user_id
        self.em.persist(post)
        
        # Log de l'opération
        log = OwnershipLog()
        log.from_user_id = from_user_id
        log.to_user_id = to_user_id
        log.post_id = post_id
        self.em.persist(log)
        
        self.em.commit()
    except Exception:
        self.em.rollback()
        raise
```

### 3. Validation

```python
# ✅ Validation dans les entités
class User(Entity):
    def validate(self):
        """Valide les données de l'utilisateur"""
        errors = []
        
        if not self.username or len(self.username) < 3:
            errors.append("Le nom d'utilisateur doit faire au moins 3 caractères")
        
        if not self.email or '@' not in self.email:
            errors.append("Email invalide")
        
        if errors:
            raise ValidationError(errors)
        
        return True
```

L'ORM de Framefox vous permet de gérer vos données efficacement avec une syntaxe claire et des fonctionnalités avancées pour les applications modernes.
