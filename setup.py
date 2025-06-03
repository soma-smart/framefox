from setuptools import find_packages, setup

# def parse_requirements(filename):
#     with open(filename, "r") as file:
#         return file.read().splitlines()


setup(
    name="framefox",
    version="1.0.30",
    packages=find_packages(),
    include_package_data=True,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Boumaza Rayen",
    author_email="boumaza.rayen@outlook.fr",
    install_requires=[
        "sqlmodel==0.0.22",
        "typer==0.15.1",
        "fastapi==0.115.7",
        "uvicorn==0.34.0",
        "starlette==0.45.3",
        "python-multipart==0.0.20",
        "httpx==0.28.1",
        "ruamel.yaml==0.18.10",
        "python-dotenv>=1.0.1",
        "pyYAML>=6.0.2",
        "colorlog>=6.9.0",
        "jinja2>=3.1.4",
        "rich>=13.9.4",
        "pydantic-settings>=2.7.1",
        "click>=8.1.8",
        "passlib>=1.7.4",
        "pyjwt>=2.10.1",
        "bcrypt>=4.0.1",
        "pymysql>=1.1.1",
        "psycopg2-binary>=2.9.10",
        "alembic>=1.14.1",
        "pytest>=8.3.4",
        "cryptography>=44.0.2",
        "aiosmtplib>=4.0.0",
        "pika>=1.3.2",
    ],
    # install_requires=parse_requirements("requirements.txt"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "console_scripts": [
            "framefox=framefox.cli:app",
        ],
    },
    package_dir={"src": "src"},
    package_data={
        "framefox": [
            "core/**/*",
            "terminal/**/*",
            "terminal/templates/**/*",
            "terminal/commands/**/*",
            "terminal/common/**/*",
        ],
        "": ["src/**/*"],
    },
)
