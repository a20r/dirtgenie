#!/usr/bin/env python3
"""Setup script for DirtGenie."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = (this_directory / "requirements.txt").read_text().strip().split('\n')

setup(
    name="dirtgenie",
    version="1.0.0",
    author="Alex Roper",
    author_email="a20r@example.com",
    description="AI-Powered Bikepacking Trip Planner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a20r/DirtGenie",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Other/Nonlisted Topic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "dirtgenie=dirtgenie.planner:main",
            "dirtgenie-web=dirtgenie.web_app:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
