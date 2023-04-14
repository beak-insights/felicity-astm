# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = "1.0.0"

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
        "pandas==1.3.4",
        "requests==2.24.0",
        "sqlalchemy==1.4.31",
        "schedule==0.6.0",
        "fastapi==0.92.0",
        "uvicorn==0.16.0",
        "jinja2==3.1.2",
        "ndg-httpsclient",
        "pyopenssl"
        "pyasn1"
    ],   
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Implementers',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: POSIX :: Linux', 
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
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
