---
title: QueryBuilder & Advanced Patterns
description: Master the QueryBuilder, repository patterns, and complex database operations in Framefox
---

The QueryBuilder is the centerpiece of Framefox's ORM system, providing a fluent interface for constructing complex queries without writing raw SQL. It integrates seamlessly with repositories and offers advanced patterns for sophisticated database operations.

:::note[QueryBuilder Architecture]
Framefox QueryBuilder provides:
- **Fluent Interface**: Chain methods for readable query construction
- **Type Safety**: Full Python type hints and IDE autocompletion
- **SQL Injection Protection**: Automatic parameter binding and escaping
- **Database Agnostic**: Works across SQLite, PostgreSQL, MySQL, and SQL Server
- **Performance Optimized**: Generates efficient SQL with proper indexing hints
- **Debugging Support**: Query introspection and execution plan analysis
:::

## QueryBuilder Fundamentals

### Basic QueryBuilder Usage

The QueryBuilder is available through repository methods and provides a fluent interface for query construction:

```python
from framefox.core.orm.abstract_repository import AbstractRepository
from framefox.core.orm.query_builder import QueryBuilder
from src.entity.user import User

class UserRepository(AbstractRepository[User]):
    def find_active_users(self) -> list[User]:
        return (self.query_builder()
                .where("is_active", True)
                .order_by("created_at", "desc")
                .limit(50)
                .get())
    
    def find_by_email(self, email: str) -> Optional[User]:
        return (self.query_builder()
                .where("email", email)
                .first())
    
    def search_users(self, search_term: str) -> list[User]:
        return (self.query_builder()
                .where("username", "like", f"%{search_term}%")
                .or_where("email", "like", f"%{search_term}%")
                .where("is_active", True)
                .order_by("username", "asc")
                .get())
```

### Where Conditions and Filtering

The QueryBuilder supports various types of where conditions:

```python
class GameRepository(AbstractRepository[Game]):
    def find_games_by_criteria(self, filters: dict) -> list[Game]:
        qb = self.query_builder()
        
        # Simple equality
        if filters.get('user_id'):
            qb.where("user_id", filters['user_id'])
        
        # Comparison operators
        if filters.get('min_score'):
            qb.where("score", ">=", filters['min_score'])
        
        if filters.get('max_score'):
            qb.where("score", "<=", filters['max_score'])
        
        # LIKE operations for text search
        if filters.get('title_search'):
            qb.where("title", "like", f"%{filters['title_search']}%")
        
        # IN operations for multiple values
        if filters.get('statuses'):
            qb.where_in("status", filters['statuses'])
        
        # NOT conditions
        if filters.get('exclude_user_ids'):
            qb.where_not_in("user_id", filters['exclude_user_ids'])
        
        # NULL checks
        if filters.get('has_description'):
            qb.where_not_null("description")
        else:
            qb.where_null("description")
        
        # Date range filtering
        if filters.get('created_after'):
            qb.where("created_at", ">=", filters['created_after'])
        
        if filters.get('created_before'):
            qb.where("created_at", "<=", filters['created_before'])
        
        return qb.get()
```

### Advanced Query Patterns

#### Complex Conditions with Grouping

```python
def find_premium_users(self) -> list[User]:
    """Find users who are either VIP or have high-scoring games"""
    return (self.query_builder()
            .where_group(lambda q: (
                q.where("subscription_type", "VIP")
                 .or_where_exists(
                     self.query_builder()
                     .select("1")
                     .from_table("games")
                     .where_raw("games.user_id = users.id")
                     .where("games.score", ">", 1000)
                 )
            ))
            .where("is_active", True)
            .get())

def advanced_user_search(self, criteria: dict) -> list[User]:
    """Complex search with nested conditions"""
    return (self.query_builder()
            .where_group(lambda q: (
                q.where("username", "like", f"%{criteria['search']}%")
                 .or_where("email", "like", f"%{criteria['search']}%")
                 .or_where("full_name", "like", f"%{criteria['search']}%")
            ))
            .where_group(lambda q: (
                q.where("account_type", "premium")
                 .or_where("total_spent", ">", 100)
            ))
            .where("is_active", True)
            .order_by("last_login", "desc")
            .get())
```

#### Joins and Relationships

```python
def find_users_with_games(self) -> list[User]:
    """Find users with their associated games using joins"""
    return (self.query_builder()
            .join("games", "users.id", "=", "games.user_id")
            .where("games.score", ">", 500)
            .where("users.is_active", True)
            .distinct()
            .with_relations(["games"])
            .get())

def get_high_scoring_users_with_categories(self) -> list[User]:
    """Complex join across multiple tables"""
    return (self.query_builder()
            .join("games", "users.id", "=", "games.user_id")
            .join("game_categories", "games.category_id", "=", "game_categories.id")
            .where("games.score", ">", 750)
            .where("game_categories.difficulty", ">=", 3)
            .group_by("users.id")
            .having("AVG(games.score)", ">", 800)
            .order_by("AVG(games.score)", "desc")
            .get())
```

#### Aggregations and Statistics

```python
def get_user_statistics(self, user_id: int) -> dict:
    """Get comprehensive user statistics using aggregations"""
    return (self.query_builder()
            .select([
                "users.id",
                "users.username",
                "COUNT(games.id) as total_games",
                "AVG(games.score) as average_score",
                "MAX(games.score) as highest_score",
                "SUM(CASE WHEN games.completed = 1 THEN 1 ELSE 0 END) as completed_games",
                "MIN(games.created_at) as first_game",
                "MAX(games.created_at) as latest_game"
            ])
            .join("games", "users.id", "=", "games.user_id")
            .where("users.id", user_id)
            .group_by("users.id", "users.username")
            .first())

def get_category_analytics(self) -> list[dict]:
    """Analytics across game categories"""
    return (self.query_builder()
            .select([
                "gc.name as category_name",
                "COUNT(g.id) as total_games",
                "AVG(g.score) as avg_score",
                "COUNT(DISTINCT g.user_id) as unique_players",
                "SUM(g.play_time) as total_play_time"
            ])
            .from_table("game_categories gc")
            .left_join("games g", "gc.id", "=", "g.category_id")
            .where("g.is_active", True)
            .group_by("gc.id", "gc.name")
            .having("COUNT(g.id)", ">", 0)
            .order_by("total_games", "desc")
            .get())
```

### Subqueries and Exists Operations

```python
def find_users_without_recent_activity(self, days: int = 30) -> list[User]:
    """Find users without recent game activity using NOT EXISTS"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    return (self.query_builder()
            .where("is_active", True)
            .where_not_exists(
                self.query_builder()
                .select("1")
                .from_table("games")
                .where_raw("games.user_id = users.id")
                .where("games.created_at", ">", cutoff_date)
            )
            .order_by("last_login", "asc")
            .get())

def find_top_performers_in_category(self, category_id: int, limit: int = 10) -> list[User]:
    """Find top performers using correlated subqueries"""
    return (self.query_builder()
            .where_exists(
                self.query_builder()
                .select("1")
                .from_table("games")
                .where_raw("games.user_id = users.id")
                .where("games.category_id", category_id)
                .where_raw(
                    "games.score >= (SELECT AVG(score) * 1.5 FROM games WHERE category_id = ?)",
                    [category_id]
                )
            )
            .order_by_raw(
                "(SELECT MAX(score) FROM games WHERE user_id = users.id AND category_id = ?) DESC",
                [category_id]
            )
            .limit(limit)
            .get())
```

## Advanced Repository Patterns

### Specification Pattern for Business Logic

Implement the Specification pattern to encapsulate complex business rules:

```python
from abc import ABC, abstractmethod
from typing import Protocol

class Specification(Protocol):
    """Specification interface for business rules"""
    
    def is_satisfied_by(self, entity: Any) -> bool:
        """Check if entity satisfies the specification"""
        ...
    
    def to_query_builder(self, qb: QueryBuilder) -> QueryBuilder:
        """Apply specification to query builder"""
        ...

class ActiveUserSpecification:
    """Specification for active users"""
    
    def is_satisfied_by(self, user: User) -> bool:
        return user.is_active and user.email_verified
    
    def to_query_builder(self, qb: QueryBuilder) -> QueryBuilder:
        return qb.where("is_active", True).where("email_verified", True)

class HighScoringPlayerSpecification:
    """Specification for high-scoring players"""
    
    def __init__(self, min_average_score: float = 750.0):
        self.min_average_score = min_average_score
    
    def is_satisfied_by(self, user: User) -> bool:
        if not user.games:
            return False
        avg_score = sum(game.score for game in user.games) / len(user.games)
        return avg_score >= self.min_average_score
    
    def to_query_builder(self, qb: QueryBuilder) -> QueryBuilder:
        return (qb.join("games", "users.id", "=", "games.user_id")
                .group_by("users.id")
                .having("AVG(games.score)", ">=", self.min_average_score))

class RecentActivitySpecification:
    """Specification for users with recent activity"""
    
    def __init__(self, days: int = 7):
        self.cutoff_date = datetime.now() - timedelta(days=days)
    
    def to_query_builder(self, qb: QueryBuilder) -> QueryBuilder:
        return qb.where("last_login", ">=", self.cutoff_date)

class CompositeSpecification:
    """Combine multiple specifications with AND logic"""
    
    def __init__(self, *specifications: Specification):
        self.specifications = specifications
    
    def to_query_builder(self, qb: QueryBuilder) -> QueryBuilder:
        for spec in self.specifications:
            qb = spec.to_query_builder(qb)
        return qb

# Repository using specifications
class UserRepository(AbstractRepository[User]):
    def find_by_specification(self, specification: Specification, 
                            limit: int = None, offset: int = None) -> list[User]:
        """Find users matching business specification"""
        qb = self.query_builder()
        qb = specification.to_query_builder(qb)
        
        if limit:
            qb = qb.limit(limit)
        if offset:
            qb = qb.offset(offset)
        
        return qb.get()
    
    def get_elite_active_players(self) -> list[User]:
        """Business query: active users with high scores and recent activity"""
        elite_spec = CompositeSpecification(
            ActiveUserSpecification(),
            HighScoringPlayerSpecification(800.0),
            RecentActivitySpecification(14)
        )
        
        return self.find_by_specification(elite_spec)
```

:::tip[QueryBuilder Best Practices]
Optimize your queries for better performance:
- **Use indexes** on frequently queried columns (`WHERE`, `JOIN`, `ORDER BY`)
- **Limit result sets** with `LIMIT` clauses to prevent memory issues
- **Use `EXISTS` instead of `IN`** for subqueries when possible
- **Avoid `SELECT *`** in production code - specify needed columns
- **Use `JOIN`s instead of separate queries** to prevent N+1 problems
- **Profile queries** with database EXPLAIN to understand execution plans
- **Cache expensive aggregations** and analytics queries
:::

:::note[Advanced Query Patterns]
Master complex querying techniques:
- **Specification Pattern**: Encapsulate business rules in reusable specifications
- **Dynamic Query Building**: Create flexible repositories that adapt to input criteria
- **Aggregation Queries**: Use `GROUP BY`, `HAVING`, and aggregate functions effectively
- **Subqueries and CTEs**: Leverage correlated subqueries and Common Table Expressions
- **Window Functions**: Use advanced SQL features for analytics and ranking
:::

:::caution[Performance Considerations]
When building complex queries:
- **Monitor query execution time** and optimize slow queries
- **Use pagination** for large result sets to prevent memory exhaustion
- **Consider caching** for expensive aggregation queries
- **Test with realistic data volumes** to identify performance bottlenecks
- **Use database-specific optimizations** when targeting specific database engines
:::
