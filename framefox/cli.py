import sys

from framefox.terminal.terminal import Terminal


def main():
    """
    Point d'entrée principal de l'application CLI Framefox.
    """
    console = Terminal()
    return console.run()


# Ne pas appeler directement app() dans le point d'entrée
if __name__ == "__main__":
    sys.exit(main())
else:
    app = main  # Ceci est important pour que `python -m framefox` fonctionne
