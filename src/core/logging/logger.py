# logger.py
import logging
import os


class Logger:
    """
    A Logger class that sets up logging for the application.

    Attributes:
        logger (logging.Logger): The root logger instance.

    Methods:
        __init__(): Initializes the Logger instance, sets up file and stream handlers, and configures the formatter.
        get_logger(): Returns the root logger instance.
    """

    def __init__(self):
        log_dir = os.path.join(os.path.dirname(__file__), "../../../var/log")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "app.log")

        # Get the root logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # Create a file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Create a stream handler (console)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        # Create a formatter and add it to the handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Add the handlers to the root logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def get_logger(self):
        return self.logger
