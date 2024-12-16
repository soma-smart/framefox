# logger.py
import logging
import os


class Logger:
    def __init__(self):
        log_dir = os.path.join(os.path.dirname(__file__), '../../../var/log')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')

        # Obtenir le logger racine
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # Créer un gestionnaire de fichier
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Créer un gestionnaire de flux (console)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        # Créer un formatteur et l'ajouter aux gestionnaires
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Ajouter les gestionnaires au logger racine
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def get_logger(self):
        return self.logger
