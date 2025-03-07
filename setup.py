from setuptools import find_packages, setup

setup(
    name="framefox",
    version="1.0.2",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer==0.15.1",
        "fastapi==0.115.7",
        "uvicorn==0.34.0",
        "starlette==0.45.3",
        "sqlmodel==0.0.22",
        "python-dotenv==1.0.1",
        "pyYAML==6.0.2",
        "colorlog==6.9.0",
        "jinja2==3.1.4",
        "rich==13.9.4",
        "pydantic-settings==2.7.1",
        "click==8.1.8",
        "passlib==1.7.4",
        "pyjwt==2.10.1",
        "bcrypt==4.0.1",
        "python-multipart==0.0.20",
        "pymysql==1.1.1",
        "psycopg2-binary==2.9.10",
        "ruamel.yaml==0.18.10",
        "alembic==1.14.1",
        "pytest==8.3.4",
        "httpx==0.28.1",
        "cryptography==44.0.2",
    ],
    entry_points={
        "console_scripts": [
            "framefox=framefox.cli:app",
        ],
    },
    package_data={
        "framefox": [
            "framefox/**",
            "terminal/templates/**/*",
        ],
    },
)
