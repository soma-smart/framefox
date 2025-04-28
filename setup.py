from setuptools import find_packages, setup

def parse_requirements(filename):
    with open(filename, "r") as file:
        return file.read().splitlines()

setup(
    name="framefox",
    version="1.0.24",
    packages=find_packages(),
    include_package_data=True,
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Boumaza Rayen",
    author_email="boumaza.rayen@outlook.fr",
    install_requires=parse_requirements("requirements.txt"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
