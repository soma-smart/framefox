---
title: Base de données et ORM
description: Guide complet de l'ORM intégré de Framefox pour la gestion des données
---

# Base de données et ORM

Framefox inclut un ORM (Object-Relational Mapping) puissant qui simplifie l'interaction avec votre base de données. Compatible avec SQLite, MySQL, PostgreSQL et d'autres bases de données.

## Configuration de la base de données

### Fichier de configuration

Dans `config/orm.yaml` :

```yaml
database:
  connections:
    default:
      driver: sqlite
      database: database.db
      
    mysql:
      driver: mysql
      host: localhost
      port: 3306
      database: framefox_app
      username: user
      password: password
      charset: utf8mb4
      
    postgresql:
      driver: postgresql
      host: localhost
      port: 5432
      database: framefox_app
      username: user
      password: password
      
  default: default  # Connexion par défaut
```

### Installation des drivers

```bash
# Pour MySQL
pip install pymysql

# Pour PostgreSQL
pip install psycopg2-binary

# Pour SQLite (inclus avec Python)
# Aucune installation nécessaire
```

## Entités

### Création d'entités

Utilisez le terminal pour générer une entité :

```bash
framefox create entity User
```

Ou créez manuellement `src/entity/user.py` :

```python
from framefox.core.orm.entity import Entity
from framefox.core.orm.column import Column
from datetime import datetime

class User(Entity):
    __tablename__ = "users"
    
    # Clé primaire auto-incrémentée
    id = Column("id", type="INTEGER", primary_key=True, auto_increment=True)
    
    # Champs texte
    username = Column("username", type="VARCHAR(100)", nullable=False, unique=True)
    email = Column("email", type="VARCHAR(255)", nullable=False, unique=True)
    password = Column("password", type="VARCHAR(255)", nullable=False)
    
    # Champs optionnels
    first_name = Column("first_name", type="VARCHAR(100)")
    last_name = Column("last_name", type="VARCHAR(100)")
    bio = Column("bio", type="TEXT")
    
    # Champs booléens
    is_active = Column("is_active", type="BOOLEAN", default=True)
    is_admin = Column("is_admin", type="BOOLEAN", default=False)
    
    # Timestamps
    created_at = Column("created_at", type="DATETIME", default="CURRENT_TIMESTAMP")
    updated_at = Column("updated_at", type="DATETIME", default="CURRENT_TIMESTAMP", on_update="CURRENT_TIMESTAMP")
    
    def __str__(self):
        return f"User(id={self.id}, username={self.username})"
    
    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
```

### Types de colonnes

```python
from framefox.core.orm.column import Column

class Product(Entity):
    __tablename__ = "products"
    
    # Types numériques
    id = Column("id", type="INTEGER", primary_key=True)
    price = Column("price", type="DECIMAL(10,2)", nullable=False)
    stock = Column("stock", type="INTEGER", default=0)
    rating = Column("rating", type="FLOAT")
    
    # Types texte
    name = Column("name", type="VARCHAR(255)", nullable=False)
    description = Column("description", type="TEXT")
    slug = Column("slug", type="VARCHAR(255)", unique=True)
    
    # Types date/heure
    created_at = Column("created_at", type="DATETIME")
    published_at = Column("published_at", type="TIMESTAMP")
    
    # Types JSON (pour bases compatibles)
    metadata = Column("metadata", type="JSON")
    
    # Types binaires
    image = Column("image", type="BLOB")
```

## Relations

### One-to-Many (Un vers plusieurs)

```python
# Entité Post
class Post(Entity):
    __tablename__ = "posts"
    
    id = Column("id", type="INTEGER", primary_key=True, auto_increment=True)
    title = Column("title", type="VARCHAR(255)", nullable=False)
    content = Column("content", type="TEXT")
    user_id = Column("user_id", type="INTEGER", foreign_key="users.id")
    created_at = Column("created_at", type="DATETIME", default="CURRENT_TIMESTAMP")
    
    # Relation vers User
    def get_author(self):
        from src.repository.user_repository import UserRepository
        user_repo = UserRepository()
        return user_repo.find(self.user_id)

# Dans User, ajouter :
class User(Entity):
    # ... autres colonnes ...
    
    def get_posts(self):
        from src.repository.post_repository import PostRepository
        post_repo = PostRepository()
        return post_repo.find_by({"user_id": self.id})
```

### Many-to-Many (Plusieurs vers plusieurs)

```python
# Table de liaison
class UserRole(Entity):
    __tablename__ = "user_roles"
    
    user_id = Column("user_id", type="INTEGER", foreign_key="users.id", primary_key=True)
    role_id = Column("role_id", type="INTEGER", foreign_key="roles.id", primary_key=True)
    assigned_at = Column("assigned_at", type="DATETIME", default="CURRENT_TIMESTAMP")

# Entité Role
class Role(Entity):
    __tablename__ = "roles"
    
    id = Column("id", type="INTEGER", primary_key=True, auto_increment=True)
    name = Column("name", type="VARCHAR(100)", nullable=False, unique=True)
    description = Column("description", type="TEXT")

# Dans User, ajouter :
class User(Entity):
    # ... autres colonnes ...
    
    def get_roles(self):
        from src.repository.user_role_repository import UserRoleRepository
        from src.repository.role_repository import RoleRepository
        
        user_role_repo = UserRoleRepository()
        role_repo = RoleRepository()
        
        user_roles = user_role_repo.find_by({"user_id": self.id})
        roles = []
        for user_role in user_roles:
            role = role_repo.find(user_role.role_id)
            if role:
                roles.append(role)
        return roles
```

## Repositories

### Repository de base

Créez `src/repository/user_repository.py` :

```python
from framefox.core.orm.repository import Repository
from src.entity.user import User

class UserRepository(Repository):
    def __init__(self):
        super().__init__(User)
    
    def find_by_username(self, username: str):
        """Trouve un utilisateur par son nom d'utilisateur"""
        return self.find_one_by({"username": username})
    
    def find_by_email(self, email: str):
        """Trouve un utilisateur par son email"""
        return self.find_one_by({"email": email})
    
    def find_active_users(self):
        """Retourne tous les utilisateurs actifs"""
        return self.find_by({"is_active": True})
    
    def search_users(self, query: str):
        """Recherche d'utilisateurs par nom ou email"""
        # Utilisation de requêtes SQL brutes pour la recherche
        sql = """
        SELECT * FROM users 
        WHERE (username LIKE ? OR email LIKE ? OR first_name LIKE ? OR last_name LIKE ?)
        AND is_active = 1
        ORDER BY username ASC
        """
        return self.query(sql, [f"%{query}%"] * 4)
    
    def get_users_with_posts_count(self):
        """Retourne les utilisateurs avec le nombre de posts"""
        sql = """
        SELECT u.*, COUNT(p.id) as posts_count
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
        GROUP BY u.id
        ORDER BY posts_count DESC
        """
        return self.query(sql)
    
    def create_user(self, data: dict):
        """Crée un nouvel utilisateur avec validation"""
        # Vérifier l'unicité de l'email
        if self.find_by_email(data.get('email')):
            raise ValueError("Un utilisateur avec cet email existe déjà")
        
        # Vérifier l'unicité du nom d'utilisateur
        if self.find_by_username(data.get('username')):
            raise ValueError("Ce nom d'utilisateur est déjà pris")
        
        return self.create(data)
```

### Repository avec requêtes complexes

```python
from framefox.core.orm.repository import Repository
from src.entity.post import Post

class PostRepository(Repository):
    def __init__(self):
        super().__init__(Post)
    
    def find_published_posts(self):
        """Retourne les posts publiés"""
        sql = """
        SELECT p.*, u.username as author_username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.published_at IS NOT NULL
        ORDER BY p.published_at DESC
        """
        return self.query(sql)
    
    def find_posts_by_tag(self, tag: str):
        """Trouve les posts par tag"""
        sql = """
        SELECT p.* FROM posts p
        JOIN post_tags pt ON p.id = pt.post_id
        JOIN tags t ON pt.tag_id = t.id
        WHERE t.name = ?
        ORDER BY p.created_at DESC
        """
        return self.query(sql, [tag])
    
    def get_popular_posts(self, limit: int = 10):
        """Retourne les posts les plus populaires"""
        sql = """
        SELECT p.*, COUNT(c.id) as comments_count
        FROM posts p
        LEFT JOIN comments c ON p.id = c.post_id
        GROUP BY p.id
        ORDER BY comments_count DESC
        LIMIT ?
        """
        return self.query(sql, [limit])
    
    def paginate_posts(self, page: int = 1, per_page: int = 10):
        """Pagination des posts"""
        offset = (page - 1) * per_page
        
        sql = """
        SELECT p.*, u.username as author_username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
        LIMIT ? OFFSET ?
        """
        
        posts = self.query(sql, [per_page, offset])
        
        # Compter le total
        count_sql = "SELECT COUNT(*) as total FROM posts"
        total = self.query(count_sql)[0]['total']
        
        return {
            'data': posts,
            'current_page': page,
            'per_page': per_page,
            'total': total,
            'last_page': (total + per_page - 1) // per_page
        }
```

## EntityManager

### Utilisation de l'EntityManager

```python
from framefox.core.orm.entity_manager import EntityManager
from src.entity.user import User

class UserService:
    def __init__(self, entity_manager: EntityManager):
        self.em = entity_manager
    
    def create_user_with_transaction(self, user_data: dict, profile_data: dict):
        """Crée un utilisateur et son profil dans une transaction"""
        try:
            self.em.begin_transaction()
            
            # Créer l'utilisateur
            user = User()
            user.username = user_data['username']
            user.email = user_data['email']
            user.password = self.hash_password(user_data['password'])
            
            self.em.persist(user)
            self.em.flush()  # Pour obtenir l'ID généré
            
            # Créer le profil
            profile = UserProfile()
            profile.user_id = user.id
            profile.bio = profile_data.get('bio', '')
            profile.avatar = profile_data.get('avatar')
            
            self.em.persist(profile)
            self.em.commit()
            
            return user
            
        except Exception as e:
            self.em.rollback()
            raise e
    
    def bulk_update_users(self, updates: list):
        """Met à jour plusieurs utilisateurs en lot"""
        try:
            self.em.begin_transaction()
            
            for update in updates:
                user = self.em.find(User, update['id'])
                if user:
                    for key, value in update['data'].items():
                        setattr(user, key, value)
                    self.em.persist(user)
            
            self.em.commit()
            
        except Exception as e:
            self.em.rollback()
            raise e
```

## Migrations

### Créer une migration

```bash
framefox database create-migration "create_users_table"
```

Cela génère un fichier dans `migrations/versions/` :

```python
# migrations/versions/001_create_users_table.py
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Appliquer la migration"""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    """Annuler la migration"""
    op.drop_table('users')
```

### Commandes de migration

```bash
# Appliquer toutes les migrations en attente
framefox database migrate

# Revenir à une migration spécifique
framefox database migrate --revision 001

# Créer la base de données
framefox database create

# Réinitialiser la base
framefox database reset

# Voir le statut des migrations
framefox database status
```

## Requêtes avancées

### Query Builder

```python
from framefox.core.orm.query_builder import QueryBuilder

class UserRepository(Repository):
    def get_advanced_search(self, filters: dict):
        """Recherche avancée avec QueryBuilder"""
        qb = QueryBuilder(self.entity_class)
        
        # Filtres de base
        if filters.get('username'):
            qb.where('username', 'LIKE', f"%{filters['username']}%")
        
        if filters.get('email'):
            qb.where('email', '=', filters['email'])
        
        if filters.get('is_active') is not None:
            qb.where('is_active', '=', filters['is_active'])
        
        # Filtres de date
        if filters.get('created_after'):
            qb.where('created_at', '>=', filters['created_after'])
        
        if filters.get('created_before'):
            qb.where('created_at', '<=', filters['created_before'])
        
        # Tri
        sort_field = filters.get('sort_by', 'created_at')
        sort_order = filters.get('sort_order', 'DESC')
        qb.order_by(sort_field, sort_order)
        
        # Pagination
        if filters.get('limit'):
            qb.limit(filters['limit'])
        
        if filters.get('offset'):
            qb.offset(filters['offset'])
        
        return qb.get()
```

### Requêtes SQL brutes

```python
class AnalyticsRepository:
    def __init__(self, entity_manager: EntityManager):
        self.em = entity_manager
    
    def get_user_statistics(self):
        """Statistiques utilisateurs"""
        sql = """
        SELECT 
            COUNT(*) as total_users,
            COUNT(CASE WHEN is_active = 1 THEN 1 END) as active_users,
            COUNT(CASE WHEN created_at >= DATE('now', '-30 days') THEN 1 END) as new_users_30d,
            AVG(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) * 100 as active_percentage
        FROM users
        """
        return self.em.execute(sql).fetchone()
    
    def get_monthly_registrations(self):
        """Inscriptions par mois"""
        sql = """
        SELECT 
            strftime('%Y-%m', created_at) as month,
            COUNT(*) as registrations
        FROM users
        WHERE created_at >= DATE('now', '-12 months')
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month ASC
        """
        return self.em.execute(sql).fetchall()
```

## Performance et optimisation

### Mise en cache

```python
from framefox.core.cache.cache_manager import CacheManager

class UserRepository(Repository):
    def __init__(self, cache_manager: CacheManager):
        super().__init__(User)
        self.cache = cache_manager
    
    def find_with_cache(self, user_id: int):
        """Trouve un utilisateur avec mise en cache"""
        cache_key = f"user:{user_id}"
        
        # Vérifier le cache
        user = self.cache.get(cache_key)
        if user:
            return user
        
        # Charger depuis la base
        user = self.find(user_id)
        if user:
            # Mettre en cache pour 1 heure
            self.cache.set(cache_key, user, 3600)
        
        return user
    
    def invalidate_user_cache(self, user_id: int):
        """Invalide le cache d'un utilisateur"""
        cache_key = f"user:{user_id}"
        self.cache.delete(cache_key)
```

### Index et optimisations

```python
# Dans vos entités, ajoutez des index pour les requêtes fréquentes
class User(Entity):
    __tablename__ = "users"
    __indexes__ = [
        {"columns": ["email"], "unique": True},
        {"columns": ["username"], "unique": True},
        {"columns": ["is_active", "created_at"]},
        {"columns": ["last_name", "first_name"]},
    ]
    
    # ... colonnes ...
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
