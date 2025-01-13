from setuptools import setup, find_packages

setup(
    name="framefox",
    version="0.1.10",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer",
        "injectable",
        "jinja2",
    ],
    entry_points={
        "console_scripts": [
            "framefox=framefox.cli:app",
        ],
    },
    package_data={
        '': ['*.py'],
        'framefox': [
            'terminal/templates/*',
            'terminal/templates/**/*',
            'terminal/commands/*',
            'terminal/common/*'],
    },
)
