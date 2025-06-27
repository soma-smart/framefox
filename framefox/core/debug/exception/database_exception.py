from framefox.core.debug.exception.base_exception import FramefoxException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class DatabaseException(FramefoxException):
    """Base database exception"""

    pass


class TableNotFoundError(DatabaseException):
    """Raised when a required database table doesn't exist"""

    def __init__(self, table_name: str, original_error=None):
        message = f"Database table '{table_name}' does not exist. Please create the database or run database migrations."
        self.table_name = table_name
        super().__init__(message, original_error, "DB_TABLE_NOT_FOUND")


class DatabaseConnectionError(DatabaseException):
    """Raised when database connection fails"""

    def __init__(self, message="Unable to connect to database", original_error=None):
        super().__init__(message, original_error, "DB_CONNECTION_ERROR")


class DatabaseMigrationError(DatabaseException):
    """Raised when database migration fails"""

    def __init__(self, migration_name: str = None, original_error=None):
        message = f"Migration failed: {migration_name}" if migration_name else "Migration failed"
        self.migration_name = migration_name
        super().__init__(message, original_error, "DB_MIGRATION_ERROR")


class DatabaseIntegrityError(DatabaseException):
    """Raised when database integrity constraint is violated"""

    def __init__(self, constraint: str = None, original_error=None):
        message = f"Database integrity error: {constraint}" if constraint else "Database integrity error"
        self.constraint = constraint
        super().__init__(message, original_error, "DB_INTEGRITY_ERROR")


class DatabaseTransactionError(DatabaseException):
    """Raised when database transaction fails"""

    def __init__(self, message="Database transaction failed", original_error=None):
        super().__init__(message, original_error, "DB_TRANSACTION_ERROR")


class DatabaseCreationError(DatabaseException):
    """Raised when database creation fails"""

    def __init__(self, database_name: str, original_error=None):
        message = f"Failed to create database '{database_name}'"
        self.database_name = database_name
        super().__init__(message, original_error, "DB_CREATION_ERROR")


class DatabaseDropError(DatabaseException):
    """Raised when database drop operation fails"""

    def __init__(self, database_name: str, original_error=None):
        message = f"Failed to drop database '{database_name}'"
        self.database_name = database_name
        super().__init__(message, original_error, "DB_DROP_ERROR")


class DatabaseDriverError(DatabaseException):
    """Raised when database driver specific operation fails"""

    def __init__(self, driver_name: str, operation: str, original_error=None):
        message = f"{driver_name} driver error during {operation}"
        self.driver_name = driver_name
        self.operation = operation
        super().__init__(message, original_error, "DB_DRIVER_ERROR")


class UnsupportedDatabaseDriverError(DatabaseException):
    """Raised when an unsupported database driver is specified"""

    def __init__(self, driver_name: str, original_error=None):
        message = f"Unsupported database driver: '{driver_name}'. Supported drivers are: sqlite, mysql, postgresql"
        self.driver_name = driver_name
        super().__init__(message, original_error, "DB_UNSUPPORTED_DRIVER")
