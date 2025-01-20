from setuptools import setup, find_packages

setup(
    name="framefox",
    version="0.1.36",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer==0.15.1",
        "fastapi==0.115.6",
        "uvicorn==0.32.1",
        "starlette==0.41.3",
        "sqlmodel==0.0.22",
        "python-dotenv==1.0.1",
        "pyYAML==6.0.2",
        "colorlog==6.9.0",
        "jinja2==3.1.4",
        "rich==13.9.4",
        "pydantic-settings==2.7.0",
        "click==8.1.8",
        "passlib==1.7.4",
        "pyjwt==2.10.1",
        "bcrypt==4.0.1",
        "python-multipart==0.0.20",
        "pymysql==1.1.1",
        "psycopg2-binary==2.9.10",
        "ruamel.yaml==0.18.10",
    ],
    entry_points={
        "console_scripts": [
            "framefox=framefox.cli:app",
        ],
    },
    package_data={
        # '': ['*.py'],
        # 'framefox': [
        #     'terminal/templates/*',
        #     'terminal/templates/**/*',
        #     'terminal/commands/*',
        #     'terminal/common/*'],
        'framefox': [
            'framefox/**',
            'terminal/templates/**/*',
        ],
    },
)
