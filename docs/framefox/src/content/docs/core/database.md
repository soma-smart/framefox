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

## Entity Management

### What is an entity ?

An entity represents a **data model** in your application - a Python class that maps directly to a database table. In the MVC (Model-View-Controller) architectural pattern, entities serve as the **Model layer**, encapsulating the structure, validation rules, and relationships of your data without containing business logic.

Think of an entity as a **blueprint** for your data. When you create a `Product` entity, you're defining what a product looks like in your database  it has a name, price, description, and relationships to other entities like categories or orders. The entity class describes these properties using Python type hints and SQLModel field definitions.

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

### Basic Entity Relationships

Entity relationships define how different data models connect in your database. Framefox uses SQLModel to automatically handle foreign keys, joins, and data consistency.

#### One-to-Many Relationships

The most common relationship type - one entity can have multiple related entities:

```python
# Category entity (the "one" side)
class Category(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    
    # Relationship to products
    products: List["Product"] = Relationship(back_populates="category")

# Product entity (the "many" side)  
class Product(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    
    # Foreign key to Category
    category_id: int = Field(foreign_key="category.id")
    
    # Back relationship to category
    category: Category = Relationship(back_populates="products")
```

## Repositories

All repositories extend the base `Repository` class, which provides fundamental CRUD operations and query capabilities. Repositories follow the Data Access Object (DAO) pattern to encapsulate database operations.

### Basic Repository Usage

```python
from framefox.core.orm.repository import Repository
from src.entity.product import Product
from typing import List, Optional

class ProductRepository(Repository):
    """Product repository for data access operations"""
    
    def __init__(self):
        super().__init__(Product)
    
    def find_by_name(self, name: str) -> Optional[Product]:
        """Find a product by its name"""
        return self.find_one_by({"name": name})
    
    def find_active_products(self) -> List[Product]:
        """Retrieve all active products"""
        return self.find_by({"is_active": True})
    
    def find_by_category(self, category_id: int) -> List[Product]:
        """Get products in a specific category"""
        return self.find_by({"category_id": category_id})
```

:::tip[Repository Best Practices]
- **Single Responsibility**: Each repository handles one entity type
- **Descriptive Method Names**: Use clear, action-oriented names
- **Type Hints**: Include type hints for better IDE support
- **Error Handling**: Provide meaningful error messages
:::

## Database Commands

Framefox provides essential CLI commands for database management:

```bash
# Create the database
framefox database create

# Apply migrations
framefox database upgrade

# Check migration status
framefox database status

# Create new migration
framefox database create-migration

# Rollback migration
framefox database downgrade
```

## Entity Manager & Transactions

The EntityManager provides the central coordination for database operations and entity lifecycle management. It implements the Unit of Work pattern to track entity changes and manage transactions efficiently.

### Basic EntityManager Usage

```python
from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from src.entity.product import Product

class ProductService:
    def __init__(self, entity_manager: EntityManagerInterface):
        self.em = entity_manager

    def create_product(self, product_data: dict) -> Product:
        """Create a new product with transaction management"""
        try:
            with self.em.transaction():
                product = Product(**product_data)
                self.em.persist(product)
                return product
        except Exception as e:
            raise RuntimeError(f"Failed to create product: {str(e)}") from e
```

:::tip[EntityManager Best Practices]
- **Always use EntityManagerInterface** for dependency injection
- **Use explicit transactions** for multi-entity operations
- **Handle exceptions properly** with try-except blocks
- **Keep transactions short** to minimize lock time
:::

## Core Database Concepts

Understanding these fundamental concepts will help you work effectively with Framefox's database layer:

### **Entity Manager & Transactions**
The EntityManager coordinates database operations and manages entity lifecycles using the Unit of Work pattern.

### **Repository Pattern**
Repositories provide a clean interface for data access, encapsulating complex queries and business logic.

### **Migration System**
Database migrations provide version control for your schema, enabling safe database evolution.

### **Query Builder**
A fluent interface for building complex queries programmatically without writing raw SQL.


## Entity Management

### What is an entity ?

An entity represents a **data model** in your application - a Python class that maps directly to a database table. In the MVC (Model-View-Controller) architectural pattern, entities serve as the **Model layer**, encapsulating the structure, validation rules, and relationships of your data without containing business logic.

Think of an entity as a **blueprint** for your data. When you create a `Product` entity, you're defining what a product looks like in your database  it has a name, price, description, and relationships to other entities like categories or orders. The entity class describes these properties using Python type hints and SQLModel field definitions.

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

### Basic Entity Relationships

Entity relationships define how different data models connect in your database. Framefox uses SQLModel to automatically handle foreign keys, joins, and data consistency.

#### One-to-Many Relationships

The most common relationship type - one entity can have multiple related entities:

```python
# Category entity (the "one" side)
class Category(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    
    # Relationship to products
    products: List["Product"] = Relationship(back_populates="category")

# Product entity (the "many" side)  
class Product(AbstractEntity, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    
    # Foreign key to Category
    category_id: int = Field(foreign_key="category.id")
    
    # Back relationship to category
    category: Category = Relationship(back_populates="products")
```

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

## Basic Database Commands

Framefox provides essential database commands through the CLI to manage your database lifecycle:

### Core Database Commands

```bash
# Create the database if it doesn't exist
framefox database create

# Apply pending migrations to update schema
framefox database upgrade

# Check migration status and history
framefox database status

# Create a new migration file
framefox database create-migration

# Rollback to previous migration
framefox database downgrade
```

## Entity Manager & Transactions

The EntityManager provides the central coordination for database operations and entity lifecycle management. It implements the Unit of Work pattern to track entity changes and manage transactions efficiently.

### Basic EntityManager Usage

```python
from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from src.entity.product import Product

class ProductService:
    def __init__(self, entity_manager: EntityManagerInterface):
        self.em = entity_manager

    def create_product(self, product_data: dict) -> Product:
        """Create a new product with transaction management"""
        try:
            with self.em.transaction():
                product = Product(**product_data)
                self.em.persist(product)
                return product
        except Exception as e:
            raise RuntimeError(f"Failed to create product: {str(e)}") from e
```

:::tip[EntityManager Best Practices]
- **Always use EntityManagerInterface** for dependency injection
- **Use explicit transactions** for multi-entity operations
- **Handle exceptions properly** with try-except blocks
- **Keep transactions short** to minimize lock time
:::

## Advanced Topics

Ready to dive deeper into database management? Explore these specialized guides:

### **Need production-ready configuration?**
→ [Advanced Database Configuration](/database/advanced-configuration) - Production optimization, environment setup, connection pooling, and security configurations for high-traffic applications.

### **Working with complex data relationships?**
→ [Advanced Relationships & Entity Patterns](/database/advanced-relationships) - Self-referencing relationships, polymorphic associations, audit trails, versioning patterns, and sophisticated entity modeling.

### **Building complex queries and repositories?**
→ [Query Builder & Advanced Patterns](/database/query-builder-patterns) - Master the Query Builder, specification pattern, caching strategies, and batch operations for high-performance applications.

### **Managing transactions and performance?**
→ [Entity Manager & Transaction Management](/database/entity-manager-transactions) - Advanced EntityManager usage, transaction patterns, connection pool management, and performance optimization techniques.

### **Handling migrations and database commands?**
→ [Database Migrations & Commands](/database/migrations-commands) - Complex migration strategies, production deployment patterns, custom maintenance commands, and automation integration.

## Repositories

All repositories extend the base `Repository` class, which provides fundamental CRUD operations and query capabilities. Repositories follow the Data Access Object (DAO) pattern to encapsulate database operations.

### Basic Repository Usage

```python
from framefox.core.orm.repository import Repository
from src.entity.product import Product
from typing import List, Optional

class ProductRepository(Repository):
    """Product repository for data access operations"""
    
    def __init__(self):
        super().__init__(Product)
    
    def find_by_name(self, name: str) -> Optional[Product]:
        """Find a product by its name"""
        return self.find_one_by({"name": name})
    
    def find_active_products(self) -> List[Product]:
        """Retrieve all active products"""
        return self.find_by({"is_active": True})
    
    def find_by_category(self, category_id: int) -> List[Product]:
        """Get products in a specific category"""
        return self.find_by({"category_id": category_id})
```

:::tip[Repository Best Practices]
- **Single Responsibility**: Each repository handles one entity type
- **Descriptive Method Names**: Use clear, action-oriented names
- **Type Hints**: Include type hints for better IDE support
- **Error Handling**: Provide meaningful error messages
:::

## Database Commands

Framefox provides essential CLI commands for database management:

```bash
# Create the database
framefox database create

# Apply migrations
framefox database upgrade

# Check migration status
framefox database status

# Create new migration
framefox database create-migration

# Rollback migration
framefox database downgrade
```

## Core Database Concepts

Understanding these fundamental concepts will help you work effectively with Framefox's database layer:

### **Entity Manager & Transactions**
The EntityManager coordinates database operations and manages entity lifecycles using the Unit of Work pattern.

### **Repository Pattern**
Repositories provide a clean interface for data access, encapsulating complex queries and business logic.

### **Migration System**
Database migrations provide version control for your schema, enabling safe database evolution.

### **Query Builder**
A fluent interface for building complex queries programmatically without writing raw SQL.

Ready to explore advanced database features? Check out our specialized guides above for in-depth coverage of complex scenarios and optimization techniques.

### **Handling migrations and database commands?**
→ [Database Migrations & Commands](/database/migrations-commands) - Complex migration strategies, production deployment patterns, custom maintenance commands, and automation integration.

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

#### Generate Migration Command

Use the Framefox CLI to automatically detect entity changes and create migrations:

```bash
# Create a new migration based on entity changes
framefox database create-migration

# Output example:
# ✓ Migration created: migrations/versions/20240603_152345_migration.py
# ✓ You can now run 'framefox database upgrade' to apply the updates
```

This command:
- **Analyzes your entities** in the `src/entity/` directory
- **Compares with current database schema** to detect differences
- **Creates a timestamped migration file** in `migrations/versions/`
- **Auto-generates upgrade/downgrade operations** based on detected changes

#### Typical Migration Workflow

**Most of the time, everything works perfectly** and you simply need to:

1. **Modify your entities** (add fields, change types, etc.)
2. **Generate the migration**: `framefox database create-migration`
3. **Apply the migration**: `framefox database upgrade`

The framework handles the complexity automatically, generating proper SQL operations for your changes.

#### When Manual Adjustments Are Needed

**Sometimes you need to customize the generated migration** for:
- **Data transformations** during schema changes
- **Complex constraint modifications** that require specific ordering
- **Custom SQL operations** not detectable by auto-generation
- **Performance optimizations** like adding specific indexes

#### Basic Migration Example

The generated migration file in `migrations/versions/` follows this structure:

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

#### Migration Recovery

:::note
If you encounter problems during migration (corrupted migration files, failed migrations, or inconsistent state):

1. **Delete the problematic migration file(s)** from `migrations/versions/`
2. **Remove the migration reference** from the `alembic_version` table in your database:
   ```sql
   DELETE FROM alembic_version WHERE version_num = 'problematic_revision_id';
   ```
3. **Start fresh** by creating a new migration with `framefox database create-migration`

This approach allows you to recover from migration issues and restart the migration process cleanly. Always backup your database before attempting migration recovery in production.
:::

## Related Topics

**[🔧 How to configure database for production environments?](core/database/advanced-configuration/)**  
**[🔗 How to create complex entity relationships and patterns?](core/database/advanced-relationships/)**  
**[🔍 How to build advanced queries and repository patterns?](core/database/query-builder-patterns/)**  
**[⚡ How to manage transactions and optimize performance?](core/database/entity-manager-transactions/)**  
**[📦 How to handle database migrations and commands?](core/database/migrations-commands/)**
