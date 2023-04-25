# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = "1.1.1"

setup(
    name="felicity.serial",
    version=version,
    description="",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="",
    author="Aurthur Musendame",
    author_email="aurthurmusendame@gmail.com",
    url="",
    packages=find_packages(include=['felicity', 'felicity.serial', 'felicity.*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "pyserial==3.5",
        "alembic==1.9.2",
        "pymysql==1.0.2",
        "pandas==1.1.5",
        "requests==2.24.0",
        "sqlalchemy==1.4.31",
        "schedule==0.6.0",
        "fastapi==0.83.0",
        "uvicorn==0.16.0",
        "jinja2==3.0.3",
        # "ndg-httpsclient",
        # "pyopenssl",
        # "pyasn1"
    ],   
    python_requires='>=3.6',
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        "dev": [
            "pytest",
            "coverage",
        ]
    },
    entry_points={
        "console_scripts": ["serial=felicity.felserial.cli:main"]
    }
)
