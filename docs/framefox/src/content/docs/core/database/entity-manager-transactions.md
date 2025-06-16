---
title: Entity Manager & Transaction Management
description: Master EntityManager, transactions, and advanced database operations in Framefox applications
---

This guide covers advanced EntityManager usage, transaction management patterns, and sophisticated database operation techniques for complex Framefox applications.

## EntityManager Deep Dive

### Understanding the EntityManager

The EntityManager is the cornerstone of Framefox's ORM architecture, serving as the central coordinator for all database operations and entity lifecycle management. Acting as an implementation of the Unit of Work pattern, it tracks changes to entities throughout their lifecycle and ensures that database operations are executed efficiently and safely within transactional boundaries.

#### What is the EntityManager?

Think of the EntityManager as your application's database session manager and transaction coordinator. It maintains an internal state of all entities you're working with, tracks their changes, and provides intelligent batching of database operations. When you retrieve an entity from the database, modify it, and then commit your changes, the EntityManager handles all the complex SQL generation, change detection, and database synchronization behind the scenes.

The EntityManager operates on the principle of **dirty checking** - it knows exactly which properties of which entities have been modified since they were loaded from the database. This allows it to generate optimal UPDATE statements that only modify the changed fields, rather than updating entire records unnecessarily.

#### EntityManagerInterface: The Practical Implementation

While the EntityManager is the core implementation, **in practice, you should always use the EntityManagerInterface** rather than the EntityManager directly. The EntityManagerInterface provides several crucial advantages:

**Context Awareness**: The interface automatically resolves to the correct EntityManager instance based on your execution context. In a web application, this means it will use the EntityManager associated with the current HTTP request, ensuring proper isolation between concurrent requests.

**Request Lifecycle Management**: The interface handles the complex lifecycle management of EntityManager instances. Each HTTP request gets its own EntityManager instance, which is automatically created when needed and properly cleaned up when the request completes.

**Testing and Flexibility**: The interface allows for easier testing and dependency injection. You can easily mock or replace the underlying EntityManager implementation without changing your application code.

**Thread Safety**: The interface ensures that EntityManager operations are properly isolated between different execution contexts, preventing data corruption in multi-threaded environments.

### Advanced EntityManager Patterns

#### Service Layer with EntityManagerInterface

```python
from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from src.entity.product import Product
from src.entity.category import Category
from typing import List, Optional, Dict, Any

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

    def bulk_update_prices(self, price_updates: Dict[int, float]) -> Dict[str, int]:
        """
        Bulk price update with comprehensive error handling and statistics
        """
        stats = {'updated': 0, 'failed': 0, 'errors': []}
        
        try:
            with self.em.transaction():
                for product_id, new_price in price_updates.items():
                    try:
                        product = self.em.find(Product, product_id)
                        if not product:
                            stats['failed'] += 1
                            stats['errors'].append(f"Product {product_id} not found")
                            continue
                        
                        if new_price <= 0:
                            stats['failed'] += 1
                            stats['errors'].append(f"Invalid price for product {product_id}")
                            continue
                        
                        old_price = product.price
                        product.price = new_price
                        
                        # Log price change for audit
                        self._log_price_change(product, old_price, new_price)
                        
                        stats['updated'] += 1
                        
                    except Exception as e:
                        stats['failed'] += 1
                        stats['errors'].append(f"Error updating product {product_id}: {str(e)}")
                
                # Only commit if we have some successful updates
                if stats['updated'] == 0:
                    raise RuntimeError("No products were successfully updated")
                
                return stats
                
        except Exception as e:
            # Transaction automatically rolls back on exception
            raise RuntimeError(f"Bulk price update failed: {str(e)}") from e

    def create_product_with_relationships(self, product_data: Dict[str, Any], 
                                        tag_names: List[str] = None) -> Product:
        """
        Create product with related entities in a single transaction
        """
        try:
            with self.em.transaction():
                # Create the main product
                product = Product(**product_data)
                self.em.persist(product)
                
                # Flush to get the product ID
                self.em.flush()
                
                # Handle tags if provided
                if tag_names:
                    for tag_name in tag_names:
                        tag = self._find_or_create_tag(tag_name)
                        # Create product-tag relationship
                        product_tag = ProductTag(
                            product_id=product.id,
                            tag_id=tag.id
                        )
                        self.em.persist(product_tag)
                
                # Create initial audit entry
                self._create_audit_entry(product, 'CREATE')
                
                return product
                
        except Exception as e:
            raise RuntimeError(f"Failed to create product: {str(e)}") from e

    def _find_or_create_tag(self, tag_name: str):
        """Helper method to find existing tag or create new one"""
        # First, try to find existing tag
        existing_tag = self.em.query(Tag).filter_by(name=tag_name).first()
        if existing_tag:
            return existing_tag
        
        # Create new tag if not found
        new_tag = Tag(name=tag_name)
        self.em.persist(new_tag)
        return new_tag
```

## Advanced Transaction Patterns

### Nested Transactions with Savepoints

```python
from contextlib import contextmanager
from typing import Generator

class AdvancedTransactionService:
    """Service demonstrating advanced transaction patterns"""
    
    def __init__(self, entity_manager: EntityManagerInterface):
        self.em = entity_manager
    
    @contextmanager
    def savepoint(self, name: str = None) -> Generator[str, None, None]:
        """
        Create a savepoint within an existing transaction
        Allows partial rollback without affecting the main transaction
        """
        savepoint_name = name or f"sp_{int(time.time())}"
        
        try:
            # Create savepoint
            self.em.execute(f"SAVEPOINT {savepoint_name}")
            yield savepoint_name
            
        except Exception:
            # Rollback to savepoint on error
            self.em.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
            raise
        finally:
            # Release savepoint if it still exists
            try:
                self.em.execute(f"RELEASE SAVEPOINT {savepoint_name}")
            except:
                pass  # Savepoint might already be released
    
    def complex_business_operation(self, orders_data: List[Dict]) -> Dict[str, Any]:
        """
        Complex operation using savepoints for granular error handling
        """
        results = {'processed': 0, 'failed': 0, 'errors': []}
        
        try:
            with self.em.transaction():
                for i, order_data in enumerate(orders_data):
                    savepoint_name = f"order_{i}"
                    
                    try:
                        with self.savepoint(savepoint_name):
                            # Process individual order
                            order = self._process_order(order_data)
                            
                            # Update inventory
                            self._update_inventory(order)
                            
                            # Send notifications
                            self._send_notifications(order)
                            
                            results['processed'] += 1
                            
                    except Exception as e:
                        # This order failed, but continue with others
                        results['failed'] += 1
                        results['errors'].append(f"Order {i}: {str(e)}")
                        continue
                
                # Decide whether to commit based on success rate
                if results['processed'] == 0:
                    raise RuntimeError("No orders were successfully processed")
                
                return results
                
        except Exception as e:
            raise RuntimeError(f"Business operation failed: {str(e)}") from e
```

### Long-Running Transaction Management

```python
import time
from datetime import datetime, timedelta

class LongRunningOperationService:
    """Service for managing long-running database operations"""
    
    def __init__(self, entity_manager: EntityManagerInterface):
        self.em = entity_manager
        self.batch_size = 1000
        self.max_transaction_time = 300  # 5 minutes
    
    def bulk_data_migration(self, source_table: str, destination_table: str, 
                           transform_func: callable = None) -> Dict[str, int]:
        """
        Migrate large amounts of data with proper transaction management
        """
        stats = {'total_processed': 0, 'total_migrated': 0, 'batches': 0}
        start_time = datetime.now()
        
        try:
            # Get total count for progress tracking
            total_count = self.em.execute(
                f"SELECT COUNT(*) FROM {source_table}"
            ).scalar()
            
            offset = 0
            
            while offset < total_count:
                batch_start = datetime.now()
                
                try:
                    with self.em.transaction():
                        # Process batch
                        batch_data = self.em.execute(
                            f"SELECT * FROM {source_table} LIMIT {self.batch_size} OFFSET {offset}"
                        ).fetchall()
                        
                        for row in batch_data:
                            # Apply transformation if provided
                            if transform_func:
                                row = transform_func(row)
                            
                            # Insert into destination
                            self._insert_migrated_row(destination_table, row)
                            stats['total_migrated'] += 1
                        
                        stats['total_processed'] += len(batch_data)
                        stats['batches'] += 1
                        
                        # Check transaction time limit
                        if (datetime.now() - batch_start).seconds > self.max_transaction_time:
                            self.em.commit()  # Force commit for long transactions
                        
                except Exception as e:
                    # Log batch error but continue
                    print(f"Batch failed at offset {offset}: {str(e)}")
                    continue
                
                offset += self.batch_size
                
                # Progress reporting
                if stats['batches'] % 10 == 0:
                    elapsed = datetime.now() - start_time
                    progress = (offset / total_count) * 100
                    print(f"Migration progress: {progress:.1f}% ({stats['total_migrated']} rows migrated in {elapsed})")
            
            return stats
            
        except Exception as e:
            raise RuntimeError(f"Data migration failed: {str(e)}") from e
```

### Connection Pool Management

```python
class ConnectionPoolService:
    """Service for advanced connection pool management"""
    
    def __init__(self, entity_manager: EntityManagerInterface):
        self.em = entity_manager
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get detailed connection pool status"""
        pool = self.em.get_bind().pool
        
        return {
            'pool_size': pool.size(),
            'checked_in': pool.checkedin(),
            'checked_out': pool.checkedout(),
            'overflow': pool.overflow(),
            'invalidated': pool.invalidated(),
            'utilization': pool.checkedout() / pool.size() if pool.size() > 0 else 0
        }
    
    def monitor_pool_health(self) -> Dict[str, Any]:
        """Monitor pool health and detect issues"""
        status = self.get_pool_status()
        health = {'status': 'healthy', 'warnings': [], 'recommendations': []}
        
        # Check for high utilization
        if status['utilization'] > 0.8:
            health['status'] = 'warning'
            health['warnings'].append('High connection pool utilization')
            health['recommendations'].append('Consider increasing pool_size')
        
        # Check for overflow usage
        if status['overflow'] > 0:
            health['warnings'].append('Connection overflow is active')
            health['recommendations'].append('Monitor peak usage and adjust pool settings')
        
        # Check for invalidated connections
        if status['invalidated'] > 0:
            health['warnings'].append('Some connections have been invalidated')
            health['recommendations'].append('Check database connectivity and network stability')
        
        return {**status, **health}
    
    @contextmanager
    def connection_timeout(self, timeout_seconds: int = 30):
        """Context manager for operations with connection timeout"""
        original_timeout = self.em.get_bind().pool._timeout
        
        try:
            # Temporarily set new timeout
            self.em.get_bind().pool._timeout = timeout_seconds
            yield
        finally:
            # Restore original timeout
            self.em.get_bind().pool._timeout = original_timeout
```

## Performance Optimization Patterns

### Query Optimization Service

```python
class QueryOptimizationService:
    """Service for query performance optimization"""
    
    def __init__(self, entity_manager: EntityManagerInterface):
        self.em = entity_manager
        self.query_cache = {}
        self.performance_log = []
    
    def execute_with_profiling(self, query: str, params: Dict = None) -> Dict[str, Any]:
        """Execute query with performance profiling"""
        start_time = time.time()
        
        try:
            # Execute query
            if params:
                result = self.em.execute(query, params)
            else:
                result = self.em.execute(query)
            
            execution_time = time.time() - start_time
            
            # Log performance metrics
            performance_data = {
                'query': query[:100] + '...' if len(query) > 100 else query,
                'execution_time': execution_time,
                'timestamp': datetime.now(),
                'row_count': result.rowcount if hasattr(result, 'rowcount') else None
            }
            
            self.performance_log.append(performance_data)
            
            return {
                'result': result,
                'execution_time': execution_time,
                'performance': performance_data
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log failed query performance
            self.performance_log.append({
                'query': query[:100] + '...' if len(query) > 100 else query,
                'execution_time': execution_time,
                'timestamp': datetime.now(),
                'error': str(e),
                'failed': True
            })
            
            raise
    
    def get_slow_queries(self, threshold_seconds: float = 1.0) -> List[Dict[str, Any]]:
        """Get queries that exceed performance threshold"""
        return [
            log for log in self.performance_log
            if log.get('execution_time', 0) > threshold_seconds
        ]
    
    def optimize_query_suggestions(self, query: str) -> List[str]:
        """Provide optimization suggestions for queries"""
        suggestions = []
        query_lower = query.lower()
        
        # Check for common optimization opportunities
        if 'select *' in query_lower:
            suggestions.append("Avoid SELECT * - specify only needed columns")
        
        if 'where' not in query_lower:
            suggestions.append("Consider adding WHERE clause to limit results")
        
        if 'limit' not in query_lower and 'count' not in query_lower:
            suggestions.append("Consider adding LIMIT clause for large result sets")
        
        if 'order by' in query_lower and 'index' not in query_lower:
            suggestions.append("Ensure ORDER BY columns are indexed")
        
        if query_lower.count('join') > 3:
            suggestions.append("Complex joins detected - consider query restructuring")
        
        return suggestions
```

:::danger[Transaction Management]
Always follow these transaction patterns:
- **Always use try-except blocks** around transactions
- **Call rollback() in exception handlers** to maintain data consistency
- **Keep transactions short** to minimize lock time
- **Don't nest transactions** unless using savepoints
- **Test transaction rollback scenarios** thoroughly
:::

:::tip[EntityManager Best Practices]
- **Always use EntityManagerInterface** instead of EntityManager directly
- **Understand session boundaries** and entity lifecycle
- **Use explicit transaction control** for complex operations
- **Monitor connection pool health** in production
- **Implement proper error handling** and rollback strategies
:::

:::note[Performance Considerations]
- **Profile long-running queries** and optimize accordingly
- **Use connection timeouts** for external database connections
- **Monitor transaction duration** and break up long operations
- **Implement proper indexing** for frequently queried columns
- **Use batch operations** for bulk data modifications
:::
