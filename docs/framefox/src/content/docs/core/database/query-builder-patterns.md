---
title: Query Builder & Advanced Patterns
description: Master the Query Builder, repository patterns, and complex database operations in Framefox
---

This guide covers advanced querying techniques, repository patterns, and sophisticated database operations using Framefox's Query Builder and ORM capabilities.

## Query Builder Pattern

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

:::tip[Query Builder vs Raw SQL]
The Query Builder offers several advantages over raw SQL:
- **Readability**: Cleaner and more maintainable code
- **Security**: Automatic protection against SQL injection  
- **Reusability**: Chainable and composable methods
- **Flexibility**: Dynamic query construction
- **Portability**: Compatible with different database engines
- **Debugging**: More explicit error messages
:::

## Advanced Repository Patterns

### Specification Pattern Implementation

Implement the Specification pattern for complex business rules:

```python
from abc import ABC, abstractmethod
from typing import Protocol
from framefox.core.orm.query_builder import QueryBuilder

class Specification(Protocol):
    """Specification interface for business rules"""
    
    def is_satisfied_by(self, entity: Any) -> bool:
        """Check if entity satisfies the specification"""
        ...
    
    def to_query_builder(self, qb: QueryBuilder) -> QueryBuilder:
        """Apply specification to query builder"""
        ...

class ActiveProductSpecification:
    """Specification for active products"""
    
    def is_satisfied_by(self, product: Product) -> bool:
        return product.is_active and product.stock_quantity > 0
    
    def to_query_builder(self, qb: QueryBuilder) -> QueryBuilder:
        return qb.where('is_active', '=', True).where('stock_quantity', '>', 0)

class FeaturedProductSpecification:
    """Specification for featured products"""
    
    def is_satisfied_by(self, product: Product) -> bool:
        return product.is_featured
    
    def to_query_builder(self, qb: QueryBuilder) -> QueryBuilder:
        return qb.where('is_featured', '=', True)

class PriceRangeSpecification:
    """Specification for price range filtering"""
    
    def __init__(self, min_price: float = None, max_price: float = None):
        self.min_price = min_price
        self.max_price = max_price
    
    def is_satisfied_by(self, product: Product) -> bool:
        if self.min_price and product.price < self.min_price:
            return False
        if self.max_price and product.price > self.max_price:
            return False
        return True
    
    def to_query_builder(self, qb: QueryBuilder) -> QueryBuilder:
        if self.min_price:
            qb = qb.where('price', '>=', self.min_price)
        if self.max_price:
            qb = qb.where('price', '<=', self.max_price)
        return qb

class CompositeSpecification:
    """Combine multiple specifications"""
    
    def __init__(self, *specifications: Specification):
        self.specifications = specifications
    
    def to_query_builder(self, qb: QueryBuilder) -> QueryBuilder:
        for spec in self.specifications:
            qb = spec.to_query_builder(qb)
        return qb

# Repository using specifications
class ProductRepository(Repository):
    def find_by_specification(self, specification: Specification, 
                            limit: int = None, offset: int = None) -> List[Product]:
        """Find products matching business specification"""
        qb = QueryBuilder(self.entity_class)
        qb = specification.to_query_builder(qb)
        
        if limit:
            qb = qb.limit(limit)
        if offset:
            qb = qb.offset(offset)
        
        return qb.get()
    
    def get_featured_active_products_in_range(self, min_price: float, max_price: float) -> List[Product]:
        """Complex business query using multiple specifications"""
        composite_spec = CompositeSpecification(
            ActiveProductSpecification(),
            FeaturedProductSpecification(),
            PriceRangeSpecification(min_price, max_price)
        )
        
        return self.find_by_specification(composite_spec)
```

### Caching Layer Integration

Implement intelligent caching for expensive queries:

```python
from functools import wraps
from typing import Callable, Any, Optional
import hashlib
import json

class CachedRepository(Repository):
    """Repository with intelligent caching capabilities"""
    
    def __init__(self, entity_class, cache_service=None):
        super().__init__(entity_class)
        self.cache = cache_service or self._get_default_cache()
        self.cache_ttl = 300  # 5 minutes default
    
    def cache_key(self, method_name: str, *args, **kwargs) -> str:
        """Generate cache key from method and parameters"""
        key_data = {
            'class': self.__class__.__name__,
            'method': method_name,
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def cached_query(self, ttl: int = None):
        """Decorator for caching query results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self.cache_key(func.__name__, *args, **kwargs)
                
                # Try to get from cache
                cached_result = self.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute query and cache result
                result = func(*args, **kwargs)
                self.cache.set(cache_key, result, ttl or self.cache_ttl)
                return result
            
            return wrapper
        return decorator
    
    @cached_query(ttl=600)  # Cache for 10 minutes
    def get_popular_products(self, limit: int = 10) -> List[Product]:
        """Get popular products with caching"""
        return (QueryBuilder(self.entity_class)
                .where('is_active', '=', True)
                .order_by('view_count', 'DESC')
                .limit(limit)
                .get())
    
    @cached_query(ttl=300)  # Cache for 5 minutes
    def get_category_stats(self, category_id: int) -> Dict[str, Any]:
        """Get category statistics with caching"""
        return (QueryBuilder(self.db)
                .select([
                    'COUNT(*) as product_count',
                    'AVG(price) as avg_price',
                    'SUM(stock_quantity) as total_stock'
                ])
                .from_table('products')
                .where('category_id', '=', category_id)
                .where('is_active', '=', True)
                .first())
    
    def invalidate_cache(self, pattern: str = None):
        """Invalidate cache entries"""
        if pattern:
            # Invalidate specific pattern
            self.cache.delete_pattern(f"*{pattern}*")
        else:
            # Invalidate all repository cache
            self.cache.delete_pattern(f"*{self.__class__.__name__}*")
    
    def create(self, data: dict) -> Any:
        """Override create to invalidate relevant cache"""
        result = super().create(data)
        self.invalidate_cache("get_popular_products")
        self.invalidate_cache("get_category_stats")
        return result
```

### Batch Operations and Performance

Implement efficient batch operations for high-performance scenarios:

```python
class BatchProductRepository(Repository):
    """Repository optimized for batch operations"""
    
    def bulk_create(self, products_data: List[Dict[str, Any]], 
                   batch_size: int = 1000) -> List[Product]:
        """Efficiently create multiple products in batches"""
        created_products = []
        
        # Process in batches to avoid memory issues
        for i in range(0, len(products_data), batch_size):
            batch = products_data[i:i + batch_size]
            
            # Use bulk insert for performance
            products = [Product(**data) for data in batch]
            
            with self.db.begin():
                self.db.add_all(products)
                self.db.flush()  # Get IDs without committing
                
                # Collect created products with IDs
                created_products.extend(products)
        
        return created_products
    
    def bulk_update(self, updates: List[Dict[str, Any]], 
                   batch_size: int = 1000) -> int:
        """Efficiently update multiple products"""
        updated_count = 0
        
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            
            # Group updates by fields being changed
            update_groups = {}
            for update in batch:
                fields = tuple(sorted(k for k in update.keys() if k != 'id'))
                if fields not in update_groups:
                    update_groups[fields] = []
                update_groups[fields].append(update)
            
            # Execute bulk updates for each group
            with self.db.begin():
                for fields, group_updates in update_groups.items():
                    ids = [u['id'] for u in group_updates]
                    update_data = {k: v for k, v in group_updates[0].items() if k != 'id'}
                    
                    # Use Query Builder for bulk update
                    qb = QueryBuilder(self.db)
                    result = (qb.table('products')
                             .where_in('id', ids)
                             .update(update_data))
                    
                    updated_count += result.rowcount
        
        return updated_count
    
    def bulk_delete(self, product_ids: List[int], 
                   soft_delete: bool = True) -> int:
        """Efficiently delete multiple products"""
        if not product_ids:
            return 0
        
        qb = QueryBuilder(self.db)
        
        if soft_delete:
            # Soft delete by setting deleted_at timestamp
            from datetime import datetime
            result = (qb.table('products')
                     .where_in('id', product_ids)
                     .update({'deleted_at': datetime.now()}))
        else:
            # Hard delete from database
            result = (qb.table('products')
                     .where_in('id', product_ids)
                     .delete())
        
        return result.rowcount
    
    def bulk_upsert(self, products_data: List[Dict[str, Any]], 
                   conflict_column: str = 'sku') -> Dict[str, int]:
        """Efficiently upsert products (update if exists, create if not)"""
        stats = {'created': 0, 'updated': 0}
        
        # Separate existing and new products
        existing_values = [data[conflict_column] for data in products_data]
        existing_products = (QueryBuilder(self.entity_class)
                           .where_in(conflict_column, existing_values)
                           .get())
        
        existing_map = {getattr(p, conflict_column): p for p in existing_products}
        
        updates = []
        creates = []
        
        for data in products_data:
            conflict_value = data[conflict_column]
            if conflict_value in existing_map:
                # Update existing
                existing_product = existing_map[conflict_value]
                update_data = data.copy()
                update_data['id'] = existing_product.id
                updates.append(update_data)
            else:
                # Create new
                creates.append(data)
        
        # Execute bulk operations
        if creates:
            self.bulk_create(creates)
            stats['created'] = len(creates)
        
        if updates:
            stats['updated'] = self.bulk_update(updates)
        
        return stats
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

:::note[Caching Best Practices]
Implement intelligent caching strategies:
- **Cache expensive aggregations** and analytics queries
- **Use appropriate TTL values** based on data volatility
- **Implement cache invalidation** for data consistency
- **Monitor cache hit rates** and adjust strategies accordingly
- **Consider cache warming** for critical queries
:::

:::caution[Batch Operation Considerations]
When implementing batch operations:
- **Process in reasonable batch sizes** to avoid memory issues
- **Use transactions** to ensure data consistency
- **Implement proper error handling** for partial failures
- **Monitor performance** and adjust batch sizes accordingly
- **Consider database connection limits** for concurrent operations
:::
