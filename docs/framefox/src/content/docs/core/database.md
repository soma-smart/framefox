---
title: Database & ORM
description: Complete guide to Framefox's integrated ORM for powerful data management
---

Framefox includes a powerful ORM (Object-Relational Mapping) based on SQLModel for database operations, making it easy to work with your data while keeping your code type-safe and maintainable.

It works with SQLite, MySQL, PostgreSQL and other SQL databases, making it easy to switch between development and production environments without code changes.

:::note[ORM Architecture]
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
- **Security**: Protects against SQL injection attacks
- **Maintainability**: Cleaner, more readable code
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

:::caution[Security Best Practices]
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

### What is an entity ?

An entity represents a **data model** in your application - a Python class that maps directly to a database table. In the MVC (Model-View-Controller) architectural pattern, entities serve as the **Model layer**, encapsulating the structure, validation rules, and relationships of your data without containing business logic.

Think of an entity as a **blueprint** for your data. When you create a `Product` entity, you're defining what a product looks like in your database  it has a name, price, description, and relationships to other entities like categories or orders. The entity class describes these properties using Python type hints and SQLModel field definitions.

#### Core Characteristics of Entities

**Data Structure Definition**: Entities define the schema of your database tables using Python classes. Each property corresponds to a database column, with type hints providing both Python and database type information.

**Validation and Constraints**: Entities include field-level validation rules such as required fields, length constraints, numeric ranges, and custom validation logic. This ensures data integrity at both the application and database levels.

**Relationship Mapping**: Entities define how different data models relate to each other - whether a product belongs to a category, an order contains multiple items, or a user has a profile. These relationships are automatically translated into foreign keys and JOIN operations.

**Framework Integration**: Framefox entities extend `AbstractEntity`, providing automatic generation of API models, form validation classes, and repository integration without additional configuration.

#### Entity vs Business Logic Separation

In Framefox's clean architecture approach, entities are **data-focused only**. They don't contain business operations like "calculate discount" or "send notification" - these belong in service classes. This separation makes your code more maintainable, testable, and follows the single responsibility principle from SOLID principles.

```python
# ✅ Good: Entity focuses on data structure
class Product(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=255)
    price: float = Field(gt=0)
    is_active: bool = Field(default=True)
    
    # Relationships only - no business logic
    category: "Category" = Relationship(back_populates="products")

# ✅ Good: Business logic in service classes
class ProductService:
    def calculate_discounted_price(self, product: Product, discount: float) -> float:
        return product.price * (1 - discount)
```

#### Automatic Model Generation

One of Framefox's most powerful features is automatic model generation from entities. Each entity automatically provides:

- **CreateModel**: For API endpoints that create new records (excludes ID)
- **FindModel**: For lookup operations using primary keys
- **PatchModel**: For partial updates with all fields optional

This eliminates boilerplate code while ensuring type safety across your entire application stack.

#### Entity Lifecycle in MVC

In the MVC pattern, entities flow through your application layers:
1. **Controller**: Receives HTTP requests and validates input against entity models
2. **Service**: Applies business logic using entities retrieved from repositories
3. **Repository**: Handles entity persistence, queries, and database operations
4. **Entity**: Provides the data structure and validation rules throughout this flow

This clear separation ensures that each layer has a single responsibility while maintaining type safety and data integrity.

:::note[Entity Design Philosophy]
Framefox entities follow the **data model** approach:
- **Structure First**: Define your data schema clearly and explicitly
- **Validation Built-in**: Use type hints and Field constraints for data integrity
- **Relationship Aware**: Model real-world data connections naturally
- **Framework Integrated**: Automatic API model generation and ORM integration
- **Business Logic Free**: Keep entities focused on data, not operations
:::

### Creating Entities

Entity creation in Framefox can be done through the command-line interface or manually. Entities represent your database tables as Python classes, following the clean architecture principle where entities contain only data structure and validation logic.

#### Using the Command Line Generator

Generate a new entity with the built-in command:

```bash
framefox create entity product
```

This command creates a new entity file in `src/entity/product.py` with basic structure and common fields.

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

class Product(AbstractEntity, table=True):
    """Product entity representing store products"""
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str | None = Field(default=None)
    price: float = Field(gt=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    category_id: int | None = Field(foreign_key="category.id", nullable=True)

    # Relations (handled by SQLModel Relationship)
    category: "Category" = Relationship(back_populates="products")
    orders: List["OrderItem"] = Relationship(back_populates="product")
```

:::note[Entity Design Philosophy]
Framefox entities follow these principles:
- **Data Only**: Entities contain only data structure and basic validation
- **No Business Logic**: Business operations are handled by repositories and services
- **SQLModel Integration**: Uses SQLModel for type safety and Pydantic validation
- **Automatic Models**: Generate create/find models automatically for API endpoints
:::

:::caution[Data Security]
Never store sensitive information in plain text:
- Always hash passwords using secure algorithms (bcrypt, Argon2)
- Use encryption for personal data
- Consider implementing data validation requirements
- Implement secure data handling mechanisms
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

:::note[Field Type Selection Guide]
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
    category_id: int = Field(foreign_key="category.id")
    
    # Soft delete support
    deleted_at: datetime | None = Field(default=None)
```

## Entity Relationships

Entity relationships are one of the most powerful aspects of Framefox ORM. They allow you to model logical connections between your data in an intuitive and type-safe manner. Framefox uses SQLModel to automatically handle foreign keys, joins, and data consistency.

### What is a Relationship?

A relationship defines how two or more entities are connected in your database. For example, a product belongs to a category, an order contains multiple items, or a profile belongs to a user. These connections are essential for structuring your data logically and avoiding duplication.

### The Three Types of Relationships

**One-to-Many (One to Many)**: One entity can have multiple related entities. This is the most common type of relationship - for example, a category can have multiple products.

**Many-to-Many (Many to Many)**: Entities can have multiple bidirectional relationships, requiring a junction table - for example, a product can belong to multiple collections and a collection can contain multiple products.

**One-to-One (One to One)**: Each entity is linked to exactly one other entity - for example, a product can have a single detailed profile.

### One-to-Many Relationships

The One-to-Many relationship is fundamental in data modeling. It uses a foreign key to establish the connection and SQLModel's Relationship for automatic navigation.

#### Category-Products Example

```python
# Category entity (the "one" side)
class Category(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str | None = Field(default=None)
    
    # Relationship to products
    products: List["Product"] = Relationship(back_populates="category")

# Product entity (the "many" side)
class Product(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    price: float = Field(gt=0)
    
    # Foreign key to Category
    category_id: int = Field(foreign_key="category.id")
    
    # Back relationship to category
    category: Category = Relationship(back_populates="products")
```

**How it works:**
- The `foreign_key="category.id"` establishes the database constraint
- `back_populates` ensures bidirectional consistency
- Framefox automatically generates the necessary JOINs
- Navigation is type-safe: `product.category.name` works automatically

:::tip[Relationship Best Practices]
When implementing relationships:
- **Use back_populates**: Ensures bidirectional relationship consistency
- **Foreign key naming**: Follow `{table}_id` convention for clarity
- **Nullable considerations**: Use `nullable=False` for required relationships
- **Index foreign keys**: Improves query performance automatically
:::

### Many-to-Many Relationships

Many-to-Many relationships are more complex as they require a junction table (intermediate table) to manage the connections. This table contains the foreign keys of the two main entities and can include additional metadata.

#### Product-Tag Relationship Example

```python
# Junction table for Product-Tag
class ProductTag(AbstractEntity, table=True):
    product_id: int = Field(foreign_key="product.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)
    
    # Additional metadata
    assigned_at: datetime = Field(default_factory=datetime.now)
    is_primary: bool = Field(default=False)

# Tag entity
class Tag(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    
    # Relationship to products via junction table
    products: List["Product"] = Relationship(
        back_populates="tags",
        link_table=ProductTag
    )

# Product entity with tags
class Product(AbstractEntity, table=True):
    # ...existing fields...
    
    # Relationship to tags via junction table
    tags: List[Tag] = Relationship(
        back_populates="products",
        link_table=ProductTag
    )
```

### One-to-One Relationships

One-to-One relationships link exactly one entity to another, often used for profile extensions or detailed information separation.

```python
# Product entity
class Product(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    
    # One-to-one relationship
    details: "ProductDetails" = Relationship(back_populates="product")

# ProductDetails entity
class ProductDetails(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    specifications: str | None = Field(default=None)
    warranty_info: str | None = Field(default=None)
    
    # Foreign key to Product (unique for one-to-one)
    product_id: int = Field(foreign_key="product.id", unique=True)
    
    # Relationship back to product
    product: Product = Relationship(back_populates="details")
```

:::note[Relationship Pattern Benefits]
SQLModel relationships provide:
- **Automatic Loading**: Related data loaded efficiently
- **Type Safety**: Full Python type hints for related objects
- **Query Optimization**: Intelligent JOIN generation
- **Consistency**: Automatic foreign key constraint management
- **Validation**: Pydantic validation for related data
:::
    



:::caution[Many-to-Many Considerations]
When implementing many-to-many relationships:
- **Junction tables should have meaningful names** (product_tags, not product_tag_mapping)
- **Consider additional metadata** in junction tables (created_at, expires_at)
- **Use composite primary keys** or separate ID columns based on your needs
- **Implement cascade deletes carefully** to maintain data integrity
- **Add indexes** on foreign key columns for performance
- **Consider the order of operations** when creating/deleting relationships
:::

:::note[Relationship Performance Tips]
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
from src.entity.product import Product
from typing import List, Optional, Dict, Any

class ProductRepository(Repository):
    """
    Product repository providing specialized product data access methods
    Extends base repository with product-specific functionality
    """
    
    def __init__(self):
        super().__init__(Product)
    
    def find_by_name(self, name: str) -> Optional[Product]:
        """Find a product by its name"""
        return self.find_one_by({"name": name})
    
    def find_active_products(self) -> List[Product]:
        """Retrieve all active products from the database"""
        return self.find_by({"is_active": True})
    
    def find_by_category(self, category_id: int) -> List[Product]:
        """Get all products in a specific category"""
        return self.find_by({"category_id": category_id})
    
    def search_products(self, query: str, limit: int = 50) -> List[Product]:
        """
        Search products by name or description
        Uses the Query Builder for flexible text matching
        """
        if not query or len(query.strip()) < 2:
            return []
        
        # Using Query Builder instead of raw SQL
        return self.query_builder()\
            .where("name", "LIKE", f"%{query}%")\
            .or_where("description", "LIKE", f"%{query}%")\
            .where("is_active", "=", True)\
            .order_by("name")\
            .limit(limit)\
            .get()
    
    def get_featured_products(self, limit: int = 10) -> List[Product]:
        """Get featured products for homepage display"""
        return self.query_builder()\
            .where("is_featured", "=", True)\
            .where("is_active", "=", True)\
            .order_by("created_at", "DESC")\
            .limit(limit)\
            .get()
    
    def update_last_updated(self, product_id: int) -> bool:
        """Update product's last updated timestamp"""
        from datetime import datetime
        return self.update(product_id, {"updated_at": datetime.now()})
    
    def get_recently_created(self, days: int = 7, limit: int = 20) -> List[Product]:
        """Get products created within the specified number of days using Query Builder"""
        qb = QueryBuilder(self.db)
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        return (qb.select(['p.*'])
                 .from_table('products p')
                 .where('p.created_at', '>=', cutoff_date)
                 .where('p.is_active', '=', True)
                 .order_by('p.created_at', 'DESC')
                 .limit(limit)
                 .get())
    
    def get_product_statistics(self) -> Dict[str, int]:
        """Get comprehensive product statistics using Query Builder aggregations"""
        qb = QueryBuilder(self.db)
        
        # Using Query Builder for complex aggregations
        result = (qb.select([
                    'COUNT(*) as total_products',
                    'COUNT(CASE WHEN is_active = true THEN 1 END) as active_products',
                    'COUNT(CASE WHEN is_featured = true THEN 1 END) as featured_products',
                    'COUNT(CASE WHEN stock_quantity > 0 THEN 1 END) as in_stock_products',
                    'AVG(price) as average_price'
                  ])
                  .from_table('products')
                  .first())
        
        return result if result else {}
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

### Advanced Query Builder Repository

The Query Builder allows building complex queries programmatically:


```python
from framefox.core.orm.repository import Repository
from framefox.core.orm.query_builder import QueryBuilder
from src.entity.product import Product
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

class ProductRepository(Repository):
    """
    Product repository demonstrating Query Builder usage
    Shows how to avoid raw SQL with fluent query construction
    """
    
    def __init__(self):
        super().__init__(Product)
    
    def find_active_products(self, limit: int = None) -> List[Product]:
        """
        Get all active products with category information
        Using Query Builder instead of raw SQL for maintainability
        """
        qb = QueryBuilder(self.db)
        query = (qb.select(['p.*', 'c.name as category_name'])
                  .from_table('products p')
                  .join('categories c', 'p.category_id = c.id')
                  .where('p.is_active', '=', True)
                  .where('p.created_at', '<=', 'CURRENT_TIMESTAMP')
                  .order_by('p.created_at', 'DESC'))
        
        if limit:
            query = query.limit(limit)
        
        return query.execute()
    
    def find_products_by_tag(self, tag: str, limit: int = 20) -> List[Product]:
        """
        Find products by tag using Query Builder
        Demonstrates JOIN operations without raw SQL
        """
        return (QueryBuilder(self.db)
                .select(['DISTINCT p.*', 't.name as tag_name'])
                .from_table('products p')
                .join('product_tags pt', 'p.id = pt.product_id')
                .join('tags t', 'pt.tag_id = t.id')
                .where('t.name', '=', tag)
                .where('p.is_active', '=', True)
                .order_by('p.created_at', 'DESC')
                .limit(limit)
                .execute())
    
    def get_popular_products(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular products based on views and ratings
        Using Query Builder for analytics instead of complex raw SQL
        """
        return (QueryBuilder(self.db)
                .select([
                    'p.*',
                    'c.name as category_name',
                    'COUNT(pr.id) as ratings_count',
                    'AVG(pr.rating) as avg_rating'
                ])
                .from_table('products p')
                .join('categories c', 'p.category_id = c.id')
                .left_join('product_ratings pr', 'p.id = pr.product_id')
                .where('p.is_active', '=', True)
                .where('p.created_at', '>=', f"DATE('now', '-{days} days')")
                .group_by('p.id')
                .order_by('p.view_count', 'DESC')
                .limit(limit)
                .execute())
    
```

:::tip[Query Builder vs Raw SQL]
The Query Builder offers several advantages over raw SQL:
- **Readability**: Cleaner and more maintainable code
- **Security**: Automatic protection against SQL injection  
- **Reusability**: Chainable and composable methods
- **Flexibility**: Dynamic query construction
- **Portability**: Compatible with different database engines
- **Debugging**: More explicit error messages
:::


## Entity Manager & Transactions

The EntityManager is the central component for managing entity lifecycles, transactions, and database operations in Framefox. It provides fine-grained control over when and how data is persisted to the database.

### Understanding the EntityManager

The EntityManager is the cornerstone of Framefox's ORM architecture, serving as the central coordinator for all database operations and entity lifecycle management. Acting as an implementation of the Unit of Work pattern, it tracks changes to entities throughout their lifecycle and ensures that database operations are executed efficiently and safely within transactional boundaries.

#### What is the EntityManager?

Think of the EntityManager as your application's database session manager and transaction coordinator. It maintains an internal state of all entities you're working with, tracks their changes, and provides intelligent batching of database operations. When you retrieve an entity from the database, modify it, and then commit your changes, the EntityManager handles all the complex SQL generation, change detection, and database synchronization behind the scenes.

The EntityManager operates on the principle of **dirty checking** - it knows exactly which properties of which entities have been modified since they were loaded from the database. This allows it to generate optimal UPDATE statements that only modify the changed fields, rather than updating entire records unnecessarily.

#### Transaction Management and Data Consistency

One of the most critical responsibilities of the EntityManager is managing database transactions. Transactions ensure that your database operations are atomic - either all changes are successfully applied, or none are applied at all. This is crucial for maintaining data consistency, especially when multiple related entities need to be updated together.

The EntityManager automatically manages transaction boundaries in most cases, but it also provides explicit transaction control when you need fine-grained control over when changes are committed or rolled back. This is particularly important in complex business operations where multiple entities must be updated consistently.

#### Identity Map and Object Caching

The EntityManager maintains an identity map - an internal cache that ensures that within a single session, you always get the same object instance when you request the same entity by its primary key. This prevents data inconsistencies and improves performance by avoiding redundant database queries for entities you've already loaded.

For example, if you load a Product with ID 123 twice within the same EntityManager session, you'll receive the exact same object instance both times. Any changes made to this object will be visible immediately throughout your application code within that session.

#### EntityManagerInterface: The Practical Implementation

While the EntityManager is the core implementation, **in practice, you should always use the EntityManagerInterface** rather than the EntityManager directly. The EntityManagerInterface provides several crucial advantages:

**Context Awareness**: The interface automatically resolves to the correct EntityManager instance based on your execution context. In a web application, this means it will use the EntityManager associated with the current HTTP request, ensuring proper isolation between concurrent requests.

**Request Lifecycle Management**: The interface handles the complex lifecycle management of EntityManager instances. Each HTTP request gets its own EntityManager instance, which is automatically created when needed and properly cleaned up when the request completes.

**Testing and Flexibility**: The interface allows for easier testing and dependency injection. You can easily mock or replace the underlying EntityManager implementation without changing your application code.

**Thread Safety**: The interface ensures that EntityManager operations are properly isolated between different execution contexts, preventing data corruption in multi-threaded environments.

#### Practical Example: Service Layer with EntityManagerInterface

Here's how you would typically use the EntityManagerInterface in a real application:

```python
from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from src.entity.product import Product
from src.entity.category import Category

class ProductService:
    """
    Service demonstrating proper EntityManagerInterface usage
    Notice how we inject the interface, not the concrete EntityManager
    """

    def __init__(self, entity_manager: EntityManagerInterface):
        self.em = entity_manager

    def transfer_products_category(self, from_category_id: int, to_category_id: int, 
                                   product_ids: List[int]) -> bool:
        """
        Complex business operation demonstrating transaction management
        """
        if not product_ids:
            raise ValueError("No products specified for transfer")
        
        if from_category_id == to_category_id:
            raise ValueError("Source and destination categories must be different")

        try:
            # The interface automatically handles transaction context
            with self.em.transaction():
                # Verify categories exist and are valid
                from_category = self.em.find(Category, from_category_id)
                to_category = self.em.find(Category, to_category_id)
                
                if not from_category or not to_category:
                    raise ValueError("Invalid category specified")

                # Process each product - the EntityManager tracks all changes
                for product_id in product_ids:
                    product = self.em.find(Product, product_id)
                    if product and product.category_id == from_category_id:
                        product.category_id = to_category_id
                        # No need to call persist - EntityManager tracks this change

                # Transaction commits automatically on successful exit
                return True

        except ValueError:
            # Re-raise validation errors without modification
            raise
        except Exception as e:
            # Wrap unexpected errors with context
            raise RuntimeError(f"Failed to transfer products: {str(e)}") from e
```

#### Change Tracking and Performance Optimization

The EntityManager employs sophisticated change tracking mechanisms to optimize database performance. When you modify entity properties, the EntityManager doesn't immediately execute database updates. Instead, it marks the entity as "dirty" and accumulates changes until you explicitly commit the transaction or the session is flushed.

This approach provides several performance benefits:
- **Batched Operations**: Multiple changes to the same entity result in a single UPDATE statement
- **Lazy Execution**: Database operations are deferred until absolutely necessary
- **Optimistic Updates**: Only changed fields are included in UPDATE statements
- **Connection Efficiency**: Database connections are used efficiently with minimal round trips

#### Memory Management and Session Lifecycle

The EntityManager carefully manages memory usage through its session lifecycle. Entities loaded within a session remain in memory only for the duration of that session. When the session ends (typically at the end of an HTTP request), all tracked entities are automatically detached and can be garbage collected.

This prevents memory leaks in long-running applications while ensuring that entities remain consistent within the scope of a single business operation or request.

#### Best Practices for EntityManager Usage

**Always Use the Interface**: Use `EntityManagerInterface` instead of `EntityManager` directly to ensure proper context management and request isolation.

**Understand Session Boundaries**: Be aware that entities become detached when their originating session ends. Attempting to access relationships or modify detached entities will result in errors.

**Explicit Transaction Control**: For complex operations involving multiple entities, use explicit transaction boundaries to ensure data consistency.

**Lazy Loading Awareness**: Understand when related entities are loaded from the database versus when they're accessed from the identity map cache.

:::danger[Transaction Management]
Always follow these transaction patterns:
- **Always use try-except blocks** around transactions
- **Call rollback() in exception handlers** to maintain data consistency
- **Keep transactions short** to minimize lock time
- **Don't nest transactions** unless using savepoints
- **Test transaction rollback scenarios** thoroughly
:::


## Database Commands

Framefox provides a comprehensive set of database commands through the CLI to manage your database lifecycle. These commands handle database creation, migrations, schema management, and maintenance operations.

:::tip[Command Syntax]
All database commands follow the pattern:
```bash
framefox database <command> [options]
```
Use `framefox database --help` to see all available commands.
:::

### Core Database Commands

#### Create Database

Initialize a new database based on your configuration:

```bash
# Create the database if it doesn't exist
framefox database create

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
framefox database drop

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
framefox database create-migration

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
framefox database upgrade

# Output example:
# ✓ Running migration 20240603_152345 -> 20240603_152400
# ✓ Database schema updated successfully
# ✓ All migrations applied
```

#### Rollback Migrations

Revert database schema to a previous state:

```bash
# Rollback to previous migration
framefox database downgrade

# Output example:
# ✓ Rolling back migration 20240603_152400 -> 20240603_152345
# ✓ Database schema reverted successfully
```

#### Check Migration Status

View the current migration state and history:

```bash
# Show migration status
framefox database status

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

Create a backup copy of your database 

```bash
# Copy database to backup location
framefox database copy

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
framefox database clear-metadata

# Output example:
# ✓ Metadata cache cleared
# ✓ Temporary files removed
# ✓ Database optimized
```

Use this command when:
- Encountering metadata conflicts
- After major schema changes
- For database maintenance and optimization


#### Environment-Specific Operations

Run database commands for specific environments:

```bash
# Production environment
DATABASE_URL=postgresql://prod_user:pass@prod-host:5432/prod_db framefox database status

# Development environment
DATABASE_URL=sqlite:///dev.db framefox database create

# Testing environment
DATABASE_URL=sqlite:///:memory: framefox database upgrade
```

#### Automation and CI/CD Integration

Database commands in automated environments:

```bash
# CI/CD pipeline example
#!/bin/bash
set -e

echo "Setting up test database..."
framefox database create
framefox database create-migration
framefox database upgrade

echo "Running tests..."
python -m pytest

echo "Cleaning up..."
framefox database drop
```

:::note[Best Practices]
Follow these guidelines for database command usage:
- **Always backup** before running destructive operations
- **Test migrations** in development before production
- **Use descriptive names** for migration files
- **Review migration files** before applying them
- **Monitor migration performance** on large datasets
- **Keep migrations small** and focused on single changes
- **Document complex migrations** with clear comments
:::

:::caution[Production Considerations]
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

:::note[Migration Benefits]
Migrations provide:
- **Version Control**: Track database schema changes over time
- **Team Collaboration**: Share schema changes across development teams
- **Environment Consistency**: Ensure identical database structure across environments
- **Rollback Capability**: Revert problematic changes safely
- **Data Preservation**: Modify schema while preserving existing data
- **Automated Deployment**: Include schema updates in deployment processes
:::

### Creating Migrations

#### Basic Migration Example

```python
# migrations/versions/20240115_001_create_products_table.py
"""Create products table with proper constraints and indexes

Revision ID: 20240115_001
Revises: 
Create Date: 2024-01-15 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

revision = '20240115_001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create products table with comprehensive structure"""
    
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sku', sa.String(100), nullable=False, unique=True),
        sa.Column('price', sa.Decimal(10, 2), nullable=False),
        sa.Column('stock_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, 
                 server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, 
                 server_default=func.now(), onupdate=func.now()),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku', name='uq_products_sku'),
        
        # Check constraints for validation
        sa.CheckConstraint(
            "price > 0", 
            name='ck_products_price_positive'
        ),
        sa.CheckConstraint(
            "stock_quantity >= 0", 
            name='ck_products_stock_non_negative'
        ),
        sa.CheckConstraint(
            "length(name) >= 1", 
            name='ck_products_name_length'
        )
    )
    
    # Create indexes for performance
    op.create_index('ix_products_name', 'products', ['name'])
    op.create_index('ix_products_sku', 'products', ['sku'])
    op.create_index('ix_products_active_created', 'products', ['is_active', 'created_at'])
    op.create_index('ix_products_category', 'products', ['category_id'])
    op.create_index('ix_products_price', 'products', ['price'])
    
    # Create partial index for active products only (PostgreSQL)
    # op.create_index('ix_products_active_only', 'products', ['id'], 
    #                postgresql_where=sa.text('is_active = true'))

def downgrade():
    """Reverse the migration - drop products table"""
    
    # Drop indexes first
    op.drop_index('ix_products_price', table_name='products')
    op.drop_index('ix_products_category', table_name='products')
    op.drop_index('ix_products_active_created', table_name='products')
    op.drop_index('ix_products_sku', table_name='products')
    op.drop_index('ix_products_name', table_name='products')
    
    # Drop the table
    op.drop_table('products')
```

### Query Builder Pattern

The Query Builder provides a fluent interface for building complex queries programmatically, eliminating the need to write raw SQL:

```python
from framefox.core.orm.query_builder import QueryBuilder
from framefox.core.orm.repository import Repository
from src.entity.product import Product
from typing import List, Dict, Any

class AdvancedProductRepository(Repository):
    """
    Repository demonstrating advanced querying techniques  
    with the Query Builder - no raw SQL needed
    """
    
    def __init__(self):
        super().__init__(Product)
    
    def advanced_product_search(self, filters: Dict[str, Any]) -> List[Product]:
        """
        Complex product search with dynamic filtering using Query Builder
        Demonstrates flexible query construction without raw SQL
        """
        qb = QueryBuilder(self.entity_class)
        
        # Text search with multiple fields using Query Builder
        if filters.get('search'):
            search_term = f"%{filters['search']}%"
            qb.where_group(
                qb.where('name', 'LIKE', search_term)
                .or_where('description', 'LIKE', search_term)
                .or_where('sku', 'LIKE', search_term)
            )
        
        # Exact matches using fluent interface
        if filters.get('category_id'):
            qb.where('category_id', '=', filters['category_id'])
        
        if filters.get('sku'):
            qb.where('sku', '=', filters['sku'])
        
        # Boolean filters with Query Builder
        if filters.get('is_active') is not None:
            qb.where('is_active', '=', filters['is_active'])
        
        if filters.get('is_featured') is not None:
            qb.where('is_featured', '=', filters['is_featured'])
        
        if filters.get('in_stock') is not None:
            if filters['in_stock']:
                qb.where('stock_quantity', '>', 0)
            else:
                qb.where('stock_quantity', '=', 0)
        
        # Price range filtering
        if filters.get('min_price'):
            qb.where('price', '>=', filters['min_price'])
        
        if filters.get('max_price'):
            qb.where('price', '<=', filters['max_price'])
        
        # Date range filters using Query Builder
        if filters.get('created_after'):
            qb.where('created_at', '>=', filters['created_after'])
        
        if filters.get('created_before'):
            qb.where('created_at', '<=', filters['created_before'])
        
        # Category-based filtering with JOIN
        if filters.get('category_name'):
            qb.join('categories', 'products.category_id', '=', 'categories.id')
            qb.where('categories.name', '=', filters['category_name'])
        
        # Tag-based filtering with complex JOINs
        if filters.get('tags'):
            tag_list = filters['tags'] if isinstance(filters['tags'], list) else [filters['tags']]
            qb.join('product_tags', 'products.id', '=', 'product_tags.product_id')
            qb.join('tags', 'product_tags.tag_id', '=', 'tags.id')
            qb.where_in('tags.name', tag_list)
            qb.distinct()
        
        # Stock level filtering
        if filters.get('min_stock'):
            qb.where('stock_quantity', '>=', filters['min_stock'])
        
        # Sorting options with Query Builder
        sort_field = filters.get('sort_by', 'created_at')
        sort_order = filters.get('sort_order', 'DESC')
        
        if sort_field == 'popularity':
            qb.order_by('view_count', sort_order)
        elif sort_field == 'price_asc':
            qb.order_by('price', 'ASC')
        elif sort_field == 'price_desc':
            qb.order_by('price', 'DESC')
        else:
            qb.order_by(sort_field, sort_order)
        
        # Pagination support
        if filters.get('limit'):
            qb.limit(filters['limit'])
        
        if filters.get('offset'):
            qb.offset(filters['offset'])
        
        return qb.get()
    
    def get_product_analytics_summary(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """
        Product analytics using Query Builder aggregation methods
        Replaces complex raw SQL with maintainable Query Builder calls
        """
        qb = QueryBuilder(self.db)
        
        # Base query with aggregations
        qb.select([
            'COUNT(*) as total_products',
            'AVG(price) as average_price',
            'SUM(stock_quantity) as total_stock',
            'COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_products',
            'COUNT(CASE WHEN is_featured = 1 THEN 1 END) as featured_products'
        ]).from_table('products')
        
        # Date filtering if provided
        if date_from:
            qb.where('created_at', '>=', date_from)
        
        if date_to:
            qb.where('created_at', '<=', date_to)
        
        result = qb.execute()
        return result[0] if result else {}
    
    def get_category_performance(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Category performance analysis using Query Builder
        Shows how to replace complex analytics SQL with Query Builder
        """
        return (QueryBuilder(self.db)
                .select([
                    'c.name as category_name',
                    'COUNT(p.id) as products_count',
                    'AVG(p.price) as avg_price',
                    'SUM(p.view_count) as total_views',
                    'SUM(p.stock_quantity) as total_stock'
                ])
                .from_table('categories c')
                .left_join('products p', 'c.id = p.category_id')
                .where('p.is_active', '=', True)
                .group_by('c.id', 'c.name')
                .order_by('total_views', 'DESC')
                .limit(limit)
                .execute())
```

:::tip[Query Optimization Strategies]
Optimize your queries for better performance:
- **Use indexes** on frequently queried columns
- **Limit result sets** with LIMIT clauses
- **Use EXISTS instead of IN** for subqueries when possible
- **Avoid SELECT *** in production code
- **Use JOINs instead of separate queries** to prevent N+1 problems
- **Profile queries** with EXPLAIN to understand execution plans
:::


