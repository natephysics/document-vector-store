#!/usr/bin/env python

from setuptools import find_packages, setup

# Read the requirements from the requirements.txt file
with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    name="llm_testing",
    version="0.0.1",
    description="VectorDB",
    author="Nathan Belmore",
    author_email="nate.physics@gmail.com",
    url="",
    install_requires=requirements,
    packages=find_packages(),
    python_requires=">=3.11",
)
