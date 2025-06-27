from framefox.core.debug.exception.base_exception import FramefoxException

"""
Framefox Framework developed by SOMA
Github: https://github.com/soma-smart/framefox
----------------------------
Author: BOUMAZA Rayen
Github: https://github.com/RayenBou
"""


class FileException(FramefoxException):
    """Base file exception"""

    pass


class FileNotFoundError(FileException):
    """Raised when file is not found"""

    def __init__(self, file_path: str, original_error=None):
        self.file_path = file_path
        message = f"File not found: {file_path}"
        super().__init__(message, original_error, "FILE_NOT_FOUND")


class FilePermissionError(FileException):
    """Raised when file permission is denied"""

    def __init__(self, file_path: str, operation: str = None, original_error=None):
        self.file_path = file_path
        self.operation = operation
        if operation:
            message = f"Permission denied for {operation} operation on file: {file_path}"
        else:
            message = f"Permission denied for file: {file_path}"
        super().__init__(message, original_error, "FILE_PERMISSION_DENIED")


class FileUploadError(FileException):
    """Raised when file upload fails"""

    def __init__(self, filename: str = None, reason: str = None, original_error=None):
        self.filename = filename
        self.reason = reason
        if filename and reason:
            message = f"File upload failed for '{filename}': {reason}"
        elif filename:
            message = f"File upload failed for '{filename}'"
        else:
            message = "File upload failed"
        super().__init__(message, original_error, "FILE_UPLOAD_ERROR")


class FileSizeError(FileException):
    """Raised when file size exceeds limits"""

    def __init__(self, filename: str, actual_size: int, max_size: int, original_error=None):
        self.filename = filename
        self.actual_size = actual_size
        self.max_size = max_size
        message = f"File '{filename}' size ({actual_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        super().__init__(message, original_error, "FILE_SIZE_ERROR")
