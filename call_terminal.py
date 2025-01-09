from injectable import load_injection_container
from src.terminal.terminal import Terminal

if __name__ == "__main__":
    load_injection_container()
    Terminal().run()
