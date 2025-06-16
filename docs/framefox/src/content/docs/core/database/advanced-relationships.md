---
title: Advanced Relationships & Entity Patterns
description: Complex entity relationships, advanced patterns, and best practices for data modeling in Framefox
---

This guide covers advanced entity relationship patterns, complex data modeling scenarios, and optimization techniques for sophisticated database architectures.

## Advanced Relationship Patterns

### Self-Referencing Relationships

Model hierarchical data structures with self-referencing relationships:

```python
class Category(AbstractEntity, table=True):
    """Category with hierarchical structure"""
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str | None = Field(default=None)
    
    # Self-referencing relationship for parent category
    parent_id: int | None = Field(foreign_key="category.id", nullable=True)
    
    # Relationships
    parent: "Category" = Relationship(
        back_populates="children",
        remote_side=[id]  # Required for self-referencing
    )
    children: List["Category"] = Relationship(back_populates="parent")
    products: List["Product"] = Relationship(back_populates="category")
```

### Polymorphic Relationships

Handle different entity types with polymorphic associations:

```python
# Base entity for polymorphic relationships
class Comment(AbstractEntity, table=True):
    """Polymorphic comment system"""
    
    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(nullable=False)
    author_id: int = Field(foreign_key="user.id")
    
    # Polymorphic fields
    commentable_id: int = Field(nullable=False)
    commentable_type: str = Field(nullable=False)  # 'product', 'article', etc.
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Relationship to author
    author: "User" = Relationship(back_populates="comments")

# Usage in other entities
class Product(AbstractEntity, table=True):
    # ...existing fields...
    
    @property
    def comments(self) -> List[Comment]:
        """Get comments for this product"""
        return self.query_comments("product")
    
    def query_comments(self, type_name: str) -> List[Comment]:
        """Query polymorphic comments"""
        from framefox.core.orm.entity_manager_interface import EntityManagerInterface
        em = EntityManagerInterface()
        return em.query(Comment).filter_by(
            commentable_id=self.id,
            commentable_type=type_name
        ).all()
```

### Many-to-Many with Rich Junction Tables

Create junction tables with additional metadata:

```python
# Rich junction table for product collections
class ProductCollection(AbstractEntity, table=True):
    """Product collection membership with metadata"""
    
    product_id: int = Field(foreign_key="product.id", primary_key=True)
    collection_id: int = Field(foreign_key="collection.id", primary_key=True)
    
    # Additional relationship metadata
    position: int = Field(default=0)  # Order in collection
    featured: bool = Field(default=False)  # Featured item
    added_at: datetime = Field(default_factory=datetime.now)
    added_by_id: int = Field(foreign_key="user.id")
    
    # Relationships to junction entities
    product: "Product" = Relationship()
    collection: "Collection" = Relationship()
    added_by: "User" = Relationship()

class Collection(AbstractEntity, table=True):
    """Product collection entity"""
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    description: str | None = Field(default=None)
    
    # Many-to-many with rich junction table
    product_memberships: List[ProductCollection] = Relationship(
        back_populates="collection"
    )
    
    @property
    def products(self) -> List["Product"]:
        """Get products ordered by position"""
        return [membership.product for membership in 
                sorted(self.product_memberships, key=lambda x: x.position)]
    
    @property
    def featured_products(self) -> List["Product"]:
        """Get only featured products in collection"""
        return [membership.product for membership in 
                self.product_memberships if membership.featured]
```

## Advanced Field Configurations

### Custom Field Types and Validation

Implement sophisticated field validation and custom types:

```python
from sqlmodel import Field, Column
from sqlalchemy import Text, JSON, DateTime
from typing import Dict, List, Any
import uuid
from datetime import datetime

class AdvancedProduct(AbstractEntity, table=True):
    """Product with advanced field configurations"""
    
    id: int | None = Field(default=None, primary_key=True)
    
    # Custom UUID field for external integrations
    external_uuid: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        unique=True,
        description="External system integration UUID"
    )
    
    # Text field with custom validation
    name: str = Field(
        min_length=2,
        max_length=255,
        regex=r'^[a-zA-Z0-9\s\-_]+$',  # Alphanumeric with spaces, hyphens, underscores
        description="Product name with character restrictions"
    )
    
    # Rich JSON field for flexible data
    specifications: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Flexible product specifications in JSON format"
    )
    
    # Complex validation for price tiers
    price_tiers: List[Dict[str, float]] = Field(
        default_factory=list,
        sa_column=Column(JSON),
        description="Volume-based pricing tiers"
    )
    
    # Custom business logic validation
    @validates('price_tiers')
    def validate_price_tiers(self, key, value):
        """Validate price tier structure"""
        if not value:
            return value
        
        for tier in value:
            if not isinstance(tier, dict):
                raise ValueError("Price tier must be a dictionary")
            
            required_keys = ['min_quantity', 'price']
            if not all(key in tier for key in required_keys):
                raise ValueError(f"Price tier must contain: {required_keys}")
            
            if tier['min_quantity'] <= 0 or tier['price'] <= 0:
                raise ValueError("Quantities and prices must be positive")
        
        return value
    
    # Computed fields based on other attributes
    @hybrid_property
    def display_name(self) -> str:
        """Generate display name with SKU"""
        return f"{self.name} ({self.sku})" if self.sku else self.name
    
    @hybrid_property
    def base_price(self) -> float:
        """Get base price from tier structure"""
        if self.price_tiers:
            return min(tier['price'] for tier in self.price_tiers)
        return self.price
```

### Soft Delete Implementation

Implement soft delete functionality with automatic filtering:

```python
from sqlalchemy import event
from sqlalchemy.orm import Query

class SoftDeleteMixin:
    """Mixin for soft delete functionality"""
    
    deleted_at: datetime | None = Field(default=None, nullable=True)
    
    def soft_delete(self):
        """Mark entity as deleted without removing from database"""
        self.deleted_at = datetime.now()
    
    def restore(self):
        """Restore soft-deleted entity"""
        self.deleted_at = None
    
    @property
    def is_deleted(self) -> bool:
        """Check if entity is soft-deleted"""
        return self.deleted_at is not None

class Product(AbstractEntity, SoftDeleteMixin, table=True):
    """Product with soft delete capability"""
    
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    # ...other fields...

# Automatic filtering of soft-deleted entities
@event.listens_for(Query, "before_cursor_execute")
def filter_soft_deleted(query_context):
    """Automatically filter soft-deleted entities"""
    query = query_context.statement
    if hasattr(query, 'column_descriptions'):
        for desc in query.column_descriptions:
            entity = desc.get('entity')
            if entity and hasattr(entity, 'deleted_at'):
                query = query.filter(entity.deleted_at.is_(None))
```

## Complex Entity Patterns

### Audit Trail Implementation

Track all changes to entities with comprehensive auditing:

```python
class AuditLog(AbstractEntity, table=True):
    """Comprehensive audit trail for entity changes"""
    
    id: int | None = Field(default=None, primary_key=True)
    
    # What was changed
    entity_type: str = Field(nullable=False)  # Table name
    entity_id: int = Field(nullable=False)    # Record ID
    action: str = Field(nullable=False)       # CREATE, UPDATE, DELETE
    
    # Change details
    old_values: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    new_values: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    changed_fields: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Audit metadata
    changed_at: datetime = Field(default_factory=datetime.now)
    changed_by_id: int | None = Field(foreign_key="user.id", nullable=True)
    ip_address: str | None = Field(default=None)
    user_agent: str | None = Field(default=None)
    
    # Relationships
    changed_by: "User" = Relationship()

# Mixin for auditable entities
class AuditableMixin:
    """Mixin to add audit capabilities to entities"""
    
    def create_audit_log(self, action: str, old_values: dict = None, 
                        new_values: dict = None, user_id: int = None):
        """Create audit log entry"""
        from framefox.core.orm.entity_manager_interface import EntityManagerInterface
        
        em = EntityManagerInterface()
        
        # Determine changed fields
        changed_fields = []
        if old_values and new_values:
            changed_fields = [key for key in new_values.keys() 
                            if old_values.get(key) != new_values.get(key)]
        
        audit_entry = AuditLog(
            entity_type=self.__class__.__tablename__,
            entity_id=self.id,
            action=action,
            old_values=old_values or {},
            new_values=new_values or {},
            changed_fields=changed_fields,
            changed_by_id=user_id
        )
        
        em.persist(audit_entry)
        em.commit()

class Product(AbstractEntity, AuditableMixin, table=True):
    """Product with full audit trail"""
    # ...existing fields...
    pass
```

### Versioning Pattern

Implement entity versioning for historical tracking:

```python
class VersionedMixin:
    """Mixin for entity versioning"""
    
    version: int = Field(default=1, nullable=False)
    is_current: bool = Field(default=True, nullable=False)
    
    # Version metadata
    version_created_at: datetime = Field(default_factory=datetime.now)
    version_created_by_id: int | None = Field(foreign_key="user.id", nullable=True)
    version_notes: str | None = Field(default=None)

class ProductVersion(AbstractEntity, table=True):
    """Historical versions of products"""
    
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", nullable=False)
    version: int = Field(nullable=False)
    
    # Snapshot of product data at this version
    name: str = Field(nullable=False)
    description: str | None = Field(default=None)
    price: float = Field(gt=0)
    specifications: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Version metadata
    created_at: datetime = Field(default_factory=datetime.now)
    created_by_id: int | None = Field(foreign_key="user.id", nullable=True)
    notes: str | None = Field(default=None)
    
    # Relationships
    product: "Product" = Relationship(back_populates="versions")
    created_by: "User" = Relationship()

class Product(AbstractEntity, VersionedMixin, table=True):
    """Product with version history"""
    
    # ...existing fields...
    
    # Relationship to versions
    versions: List[ProductVersion] = Relationship(back_populates="product")
    
    def create_version(self, user_id: int = None, notes: str = None) -> ProductVersion:
        """Create a new version snapshot"""
        from framefox.core.orm.entity_manager_interface import EntityManagerInterface
        
        # Increment version number
        self.version += 1
        
        # Create version snapshot
        version = ProductVersion(
            product_id=self.id,
            version=self.version,
            name=self.name,
            description=self.description,
            price=self.price,
            specifications=self.specifications,
            created_by_id=user_id,
            notes=notes
        )
        
        em = EntityManagerInterface()
        em.persist(version)
        em.persist(self)  # Update version number
        em.commit()
        
        return version
    
    def get_version(self, version_number: int) -> ProductVersion | None:
        """Retrieve specific version"""
        return next((v for v in self.versions if v.version == version_number), None)
    
    def revert_to_version(self, version_number: int, user_id: int = None) -> bool:
        """Revert product to a previous version"""
        version = self.get_version(version_number)
        if not version:
            return False
        
        # Update current product with version data
        self.name = version.name
        self.description = version.description
        self.price = version.price
        self.specifications = version.specifications
        
        # Create new version for this revert
        self.create_version(user_id, f"Reverted to version {version_number}")
        
        return True
```

:::tip[Advanced Pattern Benefits]
These advanced patterns provide:
- **Audit Trail**: Complete change tracking for compliance and debugging
- **Versioning**: Historical data preservation and rollback capabilities
- **Soft Delete**: Data preservation while hiding deleted records
- **Polymorphic Relationships**: Flexible associations across entity types
- **Rich Junction Tables**: Additional metadata for many-to-many relationships
:::

:::caution[Performance Considerations]
When implementing advanced patterns:
- **Index audit tables** properly for query performance
- **Archive old versions** to prevent table bloat
- **Consider storage impact** of JSON fields and versioning
- **Implement cleanup jobs** for old audit logs
- **Monitor query performance** with complex relationships
:::

:::note[Testing Advanced Patterns]
Comprehensive testing strategies:
- **Unit test custom validation** logic thoroughly
- **Test audit trail completeness** across all operations
- **Verify version integrity** and rollback functionality
- **Performance test** with realistic data volumes
- **Test cascade operations** with complex relationships
:::
