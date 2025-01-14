from setuptools import setup, find_packages

setup(
    name="framefox",
    version="0.1.15",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer",
        "injectable",
        "jinja2",
        'pyYAML',
        'python-dotenv',
        'sqlmodel',
        'pymysql',
        'psycopg2',
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
