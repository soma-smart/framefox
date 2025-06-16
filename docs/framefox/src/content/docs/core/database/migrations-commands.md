---
title: Database Migrations & Commands
description: Advanced migration strategies, database commands, and deployment patterns for Framefox applications
---

This guide covers advanced migration techniques, comprehensive database command usage, and production deployment strategies for managing database schemas in Framefox applications.

## Advanced Migration Strategies

### Complex Migration Patterns

#### Data Migration with Transformation

```python
# migrations/versions/20240115_002_migrate_product_data.py
"""Migrate product data with complex transformations

Revision ID: 20240115_002
Revises: 20240115_001
Create Date: 2024-01-15 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, Text, DateTime, Boolean, Decimal
import json
from datetime import datetime

revision = '20240115_002'
down_revision = '20240115_001'
branch_labels = None
depends_on = None

def upgrade():
    """Complex data migration with transformations"""
    
    # First, add new columns to existing table
    op.add_column('products', sa.Column('specifications', sa.JSON(), nullable=True))
    op.add_column('products', sa.Column('metadata', sa.JSON(), nullable=True))
    op.add_column('products', sa.Column('migrated_at', sa.DateTime(), nullable=True))
    
    # Create temporary table for data transformation
    op.create_table(
        'product_specs_temp',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('spec_key', sa.String(100), nullable=False),
        sa.Column('spec_value', sa.Text(), nullable=True),
    )
    
    # Define table references for data manipulation
    products_table = table('products',
        column('id', Integer),
        column('name', String),
        column('description', Text),
        column('specifications', sa.JSON),
        column('metadata', sa.JSON),
        column('migrated_at', DateTime)
    )
    
    # Get database connection
    connection = op.get_bind()
    
    # Process products in batches to avoid memory issues
    batch_size = 1000
    offset = 0
    
    while True:
        # Fetch batch of products
        result = connection.execute(
            sa.text("""
                SELECT id, name, description, old_spec_field 
                FROM products 
                WHERE migrated_at IS NULL
                ORDER BY id 
                LIMIT :batch_size OFFSET :offset
            """),
            {'batch_size': batch_size, 'offset': offset}
        )
        
        products = result.fetchall()
        if not products:
            break
        
        # Transform and update each product
        for product in products:
            # Parse existing specification data
            specifications = parse_legacy_specifications(product.old_spec_field)
            
            # Create metadata from product properties
            metadata = {
                'migration_source': 'legacy_system',
                'original_format': 'csv_specs',
                'migration_date': datetime.now().isoformat(),
                'data_quality_score': calculate_data_quality(product)
            }
            
            # Update product with new JSON data
            connection.execute(
                products_table.update()
                .where(products_table.c.id == product.id)
                .values(
                    specifications=specifications,
                    metadata=metadata,
                    migrated_at=datetime.now()
                )
            )
        
        offset += batch_size
        
        # Progress logging
        print(f"Migrated batch: {offset} products processed")
    
    # Remove temporary table
    op.drop_table('product_specs_temp')
    
    # Remove old specification column after migration
    op.drop_column('products', 'old_spec_field')

def parse_legacy_specifications(spec_string):
    """Parse legacy CSV specification format to JSON"""
    if not spec_string:
        return {}
    
    specifications = {}
    try:
        # Legacy format: "key1:value1,key2:value2,key3:value3"
        for spec_pair in spec_string.split(','):
            if ':' in spec_pair:
                key, value = spec_pair.split(':', 1)
                specifications[key.strip()] = value.strip()
    except Exception as e:
        # Log parsing errors for review
        print(f"Error parsing specifications '{spec_string}': {e}")
        specifications['_parse_error'] = str(e)
        specifications['_original_value'] = spec_string
    
    return specifications

def calculate_data_quality(product):
    """Calculate data quality score for migration tracking"""
    score = 100
    
    if not product.name or len(product.name) < 3:
        score -= 20
    
    if not product.description:
        score -= 15
    
    if not product.old_spec_field:
        score -= 10
    
    return max(0, score)

def downgrade():
    """Reverse the migration"""
    
    # Add back old specification column
    op.add_column('products', sa.Column('old_spec_field', sa.Text(), nullable=True))
    
    # Define table reference
    products_table = table('products',
        column('id', Integer),
        column('specifications', sa.JSON),
        column('old_spec_field', Text)
    )
    
    connection = op.get_bind()
    
    # Convert JSON specifications back to CSV format
    result = connection.execute(
        sa.text("SELECT id, specifications FROM products WHERE specifications IS NOT NULL")
    )
    
    for row in result:
        if row.specifications:
            # Convert JSON back to CSV format
            csv_specs = ','.join([f"{k}:{v}" for k, v in row.specifications.items() 
                                 if not k.startswith('_')])  # Skip migration metadata
            
            connection.execute(
                products_table.update()
                .where(products_table.c.id == row.id)
                .values(old_spec_field=csv_specs)
            )
    
    # Remove new columns
    op.drop_column('products', 'migrated_at')
    op.drop_column('products', 'metadata')
    op.drop_column('products', 'specifications')
```

#### Zero-Downtime Schema Changes

```python
# migrations/versions/20240115_003_zero_downtime_column_change.py
"""Zero-downtime column type change using shadow table approach

Revision ID: 20240115_003
Revises: 20240115_002
Create Date: 2024-01-15 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '20240115_003'
down_revision = '20240115_002'
branch_labels = None
depends_on = None

def upgrade():
    """
    Zero-downtime migration for changing column type
    Uses shadow table approach to avoid locking main table
    """
    
    # Step 1: Create shadow table with new schema
    op.create_table(
        'products_new',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sku', sa.String(100), nullable=False, unique=True),
        # New column type: changed from Integer to String for alphanumeric SKUs
        sa.Column('price', sa.String(20), nullable=False),  # Changed from Decimal
        sa.Column('stock_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        
        # Maintain all indexes and constraints
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sku', name='uq_products_new_sku')
    )
    
    # Step 2: Copy data with transformation
    connection = op.get_bind()
    
    # Use INSERT ... SELECT for efficient bulk copy with transformation
    connection.execute(sa.text("""
        INSERT INTO products_new (
            id, name, description, sku, price, stock_quantity, 
            is_active, created_at, updated_at
        )
        SELECT 
            id, 
            name, 
            description, 
            sku,
            CAST(price AS VARCHAR(20)) as price,  -- Transform decimal to string
            stock_quantity,
            is_active,
            created_at,
            updated_at
        FROM products
    """))
    
    # Step 3: Create indexes on new table
    op.create_index('ix_products_new_name', 'products_new', ['name'])
    op.create_index('ix_products_new_sku', 'products_new', ['sku'])
    op.create_index('ix_products_new_active_created', 'products_new', ['is_active', 'created_at'])
    
    # Step 4: Rename tables atomically (database-specific approach)
    # PostgreSQL/MySQL approach:
    connection.execute(sa.text("BEGIN"))
    try:
        connection.execute(sa.text("ALTER TABLE products RENAME TO products_old"))
        connection.execute(sa.text("ALTER TABLE products_new RENAME TO products"))
        connection.execute(sa.text("COMMIT"))
    except:
        connection.execute(sa.text("ROLLBACK"))
        raise
    
    # Step 5: Drop old table (can be done later for safety)
    # op.drop_table('products_old')  # Uncomment after verification

def downgrade():
    """Reverse the zero-downtime migration"""
    
    # Recreate original table structure
    op.create_table(
        'products_original',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sku', sa.String(100), nullable=False, unique=True),
        sa.Column('price', sa.Decimal(10, 2), nullable=False),  # Back to Decimal
        sa.Column('stock_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False)
    )
    
    # Copy data back with reverse transformation
    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO products_original (
            id, name, description, sku, price, stock_quantity, 
            is_active, created_at, updated_at
        )
        SELECT 
            id, 
            name, 
            description, 
            sku,
            CAST(price AS DECIMAL(10,2)) as price,  -- Transform back to decimal
            stock_quantity,
            is_active,
            created_at,
            updated_at
        FROM products
    """))
    
    # Atomic table swap
    connection.execute(sa.text("BEGIN"))
    try:
        connection.execute(sa.text("ALTER TABLE products RENAME TO products_string"))
        connection.execute(sa.text("ALTER TABLE products_original RENAME TO products"))
        connection.execute(sa.text("COMMIT"))
    except:
        connection.execute(sa.text("ROLLBACK"))
        raise
    
    # Cleanup
    op.drop_table('products_string')
```

## Advanced Database Commands

### Custom Database Management Commands

```python
# src/commands/database_maintenance.py
"""Custom database maintenance commands for Framefox"""

import click
from framefox.core.cli.command import Command
from framefox.core.orm.entity_manager_interface import EntityManagerInterface
from datetime import datetime, timedelta
import json

class DatabaseMaintenanceCommand(Command):
    """Advanced database maintenance operations"""
    
    def register(self, app):
        """Register maintenance commands with the CLI"""
        
        @app.cli.group()
        def db_maintenance():
            """Database maintenance operations"""
            pass
        
        @db_maintenance.command()
        @click.option('--days', default=30, help='Days of logs to keep')
        @click.option('--dry-run', is_flag=True, help='Show what would be deleted without deleting')
        def cleanup_audit_logs(days, dry_run):
            """Clean up old audit logs"""
            em = EntityManagerInterface()
            cutoff_date = datetime.now() - timedelta(days=days)
            
            try:
                with em.transaction():
                    # Count records to be deleted
                    count_query = em.execute(
                        "SELECT COUNT(*) FROM audit_logs WHERE created_at < :cutoff",
                        {'cutoff': cutoff_date}
                    ).scalar()
                    
                    click.echo(f"Found {count_query} audit log records older than {days} days")
                    
                    if not dry_run:
                        if click.confirm(f'Delete {count_query} old audit log records?'):
                            result = em.execute(
                                "DELETE FROM audit_logs WHERE created_at < :cutoff",
                                {'cutoff': cutoff_date}
                            )
                            click.echo(f"Deleted {result.rowcount} audit log records")
                        else:
                            click.echo("Operation cancelled")
                    else:
                        click.echo("Dry run - no records deleted")
                        
            except Exception as e:
                click.echo(f"Error cleaning up audit logs: {e}", err=True)
        
        @db_maintenance.command()
        @click.option('--table', help='Specific table to analyze')
        def analyze_performance():
            """Analyze database performance metrics"""
            em = EntityManagerInterface()
            
            try:
                # Get table sizes
                if em.get_bind().dialect.name == 'postgresql':
                    size_query = """
                        SELECT 
                            schemaname,
                            tablename,
                            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                        ORDER BY size_bytes DESC
                    """
                elif em.get_bind().dialect.name == 'mysql':
                    size_query = """
                        SELECT 
                            table_schema,
                            table_name,
                            ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb,
                            (data_length + index_length) as size_bytes
                        FROM information_schema.TABLES 
                        WHERE table_schema = DATABASE()
                        ORDER BY size_bytes DESC
                    """
                else:
                    click.echo("Performance analysis not available for this database type")
                    return
                
                result = em.execute(size_query).fetchall()
                
                click.echo("\nDatabase Table Sizes:")
                click.echo("-" * 60)
                for row in result:
                    if em.get_bind().dialect.name == 'postgresql':
                        click.echo(f"{row.tablename:<20} {row.size:>15}")
                    else:
                        click.echo(f"{row.table_name:<20} {row.size_mb:>10} MB")
                
                # Get slow query information (PostgreSQL specific)
                if em.get_bind().dialect.name == 'postgresql':
                    slow_query = """
                        SELECT 
                            query,
                            calls,
                            total_time,
                            mean_time,
                            rows
                        FROM pg_stat_statements 
                        ORDER BY total_time DESC 
                        LIMIT 10
                    """
                    
                    try:
                        slow_queries = em.execute(slow_query).fetchall()
                        click.echo("\nSlowest Queries:")
                        click.echo("-" * 60)
                        for query in slow_queries:
                            click.echo(f"Total: {query.total_time:.2f}ms, "
                                     f"Mean: {query.mean_time:.2f}ms, "
                                     f"Calls: {query.calls}")
                            click.echo(f"Query: {query.query[:100]}...")
                            click.echo()
                    except:
                        click.echo("pg_stat_statements extension not available")
                
            except Exception as e:
                click.echo(f"Error analyzing performance: {e}", err=True)
        
        @db_maintenance.command()
        @click.option('--output', default='backup.sql', help='Output file path')
        @click.option('--tables', help='Comma-separated list of tables to backup')
        def export_data(output, tables):
            """Export database data to SQL file"""
            em = EntityManagerInterface()
            
            try:
                table_list = tables.split(',') if tables else None
                
                # Get all tables if not specified
                if not table_list:
                    if em.get_bind().dialect.name == 'postgresql':
                        tables_query = """
                            SELECT tablename FROM pg_tables 
                            WHERE schemaname = 'public'
                        """
                    elif em.get_bind().dialect.name == 'mysql':
                        tables_query = """
                            SELECT table_name FROM information_schema.tables 
                            WHERE table_schema = DATABASE()
                        """
                    else:
                        click.echo("Export not supported for this database type")
                        return
                    
                    result = em.execute(tables_query).fetchall()
                    table_list = [row[0] for row in result]
                
                with open(output, 'w') as f:
                    f.write(f"-- Database export generated on {datetime.now()}\n")
                    f.write(f"-- Tables: {', '.join(table_list)}\n\n")
                    
                    for table in table_list:
                        click.echo(f"Exporting table: {table}")
                        
                        # Get table structure
                        f.write(f"-- Table: {table}\n")
                        
                        # Export data
                        data_query = f"SELECT * FROM {table}"
                        rows = em.execute(data_query).fetchall()
                        
                        if rows:
                            # Get column names
                            columns = list(rows[0].keys())
                            
                            for row in rows:
                                values = []
                                for col in columns:
                                    value = getattr(row, col)
                                    if value is None:
                                        values.append('NULL')
                                    elif isinstance(value, str):
                                        values.append(f"'{value.replace("'", "''")}'")
                                    elif isinstance(value, datetime):
                                        values.append(f"'{value.isoformat()}'")
                                    else:
                                        values.append(str(value))
                                
                                insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
                                f.write(insert_sql)
                        
                        f.write(f"\n-- End of table: {table}\n\n")
                
                click.echo(f"Export completed: {output}")
                
            except Exception as e:
                click.echo(f"Error exporting data: {e}", err=True)
```

### Production Deployment Commands

```python
# src/commands/production_deployment.py
"""Production deployment database commands"""

import click
from framefox.core.cli.command import Command
from framefox.core.orm.entity_manager_interface import EntityManagerInterface
import subprocess
import os
from datetime import datetime

class ProductionDeploymentCommand(Command):
    """Commands for production database deployment"""
    
    def register(self, app):
        """Register deployment commands"""
        
        @app.cli.group()
        def db_deploy():
            """Production deployment commands"""
            pass
        
        @db_deploy.command()
        @click.option('--backup/--no-backup', default=True, help='Create backup before migration')
        @click.option('--verify/--no-verify', default=True, help='Verify migration before applying')
        def migrate_production(backup, verify):
            """Safe production migration with backup and verification"""
            
            em = EntityManagerInterface()
            
            try:
                # Step 1: Create backup if requested
                if backup:
                    backup_file = f"backup_pre_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
                    click.echo(f"Creating backup: {backup_file}")
                    
                    if self._create_backup(backup_file):
                        click.echo(f"Backup created successfully: {backup_file}")
                    else:
                        click.echo("Backup failed - aborting migration", err=True)
                        return
                
                # Step 2: Verify migrations if requested
                if verify:
                    click.echo("Verifying migrations...")
                    if not self._verify_migrations():
                        click.echo("Migration verification failed - aborting", err=True)
                        return
                
                # Step 3: Apply migrations
                click.echo("Applying migrations...")
                result = subprocess.run(['framefox', 'database', 'upgrade'], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    click.echo("Migrations applied successfully")
                    click.echo(result.stdout)
                    
                    # Step 4: Verify database health
                    if self._verify_database_health():
                        click.echo("Database health check passed")
                    else:
                        click.echo("Database health check failed - manual review needed", err=True)
                else:
                    click.echo("Migration failed:", err=True)
                    click.echo(result.stderr, err=True)
                    
                    if backup:
                        click.echo(f"Backup available for rollback: {backup_file}")
                
            except Exception as e:
                click.echo(f"Error during production migration: {e}", err=True)
        
        @db_deploy.command()
        @click.argument('backup_file')
        def rollback_production(backup_file):
            """Rollback production database from backup"""
            
            if not os.path.exists(backup_file):
                click.echo(f"Backup file not found: {backup_file}", err=True)
                return
            
            if not click.confirm(f'This will restore database from {backup_file}. Continue?'):
                click.echo("Rollback cancelled")
                return
            
            try:
                click.echo(f"Restoring database from {backup_file}...")
                
                if self._restore_backup(backup_file):
                    click.echo("Database restored successfully")
                    
                    # Verify restored database
                    if self._verify_database_health():
                        click.echo("Restored database health check passed")
                    else:
                        click.echo("Restored database health check failed", err=True)
                else:
                    click.echo("Database restore failed", err=True)
                    
            except Exception as e:
                click.echo(f"Error during rollback: {e}", err=True)
    
    def _create_backup(self, backup_file: str) -> bool:
        """Create database backup"""
        try:
            database_url = os.getenv('DATABASE_URL')
            
            if database_url.startswith('postgresql'):
                # PostgreSQL backup
                cmd = ['pg_dump', database_url, '-f', backup_file]
            elif database_url.startswith('mysql'):
                # MySQL backup
                cmd = ['mysqldump', '--single-transaction', '--routines', '--triggers']
                # Parse MySQL URL and add connection parameters
                # ... implementation details ...
            else:
                # SQLite backup
                cmd = ['sqlite3', database_url.replace('sqlite:///', ''), f'.backup {backup_file}']
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _verify_migrations(self) -> bool:
        """Verify pending migrations are safe"""
        try:
            result = subprocess.run(['framefox', 'database', 'status'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                return False
            
            # Check for destructive operations in migration files
            # This is a simplified check - implement more sophisticated validation
            output = result.stdout.lower()
            dangerous_operations = ['drop table', 'drop column', 'drop index']
            
            for operation in dangerous_operations:
                if operation in output:
                    click.echo(f"Warning: Potentially destructive operation detected: {operation}")
                    if not click.confirm("Continue with potentially destructive migration?"):
                        return False
            
            return True
            
        except Exception:
            return False
    
    def _verify_database_health(self) -> bool:
        """Verify database health after migration"""
        try:
            em = EntityManagerInterface()
            
            # Basic connectivity test
            em.execute("SELECT 1").scalar()
            
            # Check for critical tables
            critical_tables = ['users', 'products']  # Adjust based on your application
            
            for table in critical_tables:
                try:
                    em.execute(f"SELECT COUNT(*) FROM {table}").scalar()
                except Exception:
                    click.echo(f"Critical table missing or inaccessible: {table}")
                    return False
            
            return True
            
        except Exception:
            return False
```

:::tip[Migration Best Practices]
Follow these guidelines for production migrations:
- **Always create backups** before applying migrations
- **Test migrations thoroughly** in staging environments
- **Use small, incremental changes** rather than large migrations
- **Monitor migration performance** on production data volumes
- **Have rollback plans** for every migration
- **Use zero-downtime techniques** for critical schema changes
:::

:::caution[Production Safety]
Production migration safety measures:
- **Schedule migrations** during maintenance windows
- **Monitor application health** during and after migrations
- **Have database administrator approval** for destructive changes
- **Test rollback procedures** before deployment
- **Keep migration logs** for troubleshooting
:::

:::note[Automation Integration]
Integrate database commands with CI/CD:
- **Automate backup creation** before deployments
- **Run migration verification** in CI pipelines
- **Monitor migration performance** in staging
- **Implement automatic rollback** on failure detection
- **Send notifications** for migration status updates
:::
