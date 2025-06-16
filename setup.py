#!/usr/bin/env python3
"""Setup script for DirtGenie."""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = (this_directory / "requirements.txt").read_text().strip().split('\n')

setup(
    name="dirtgenie",
    version="1.0.0",
    author="Alex Wallar",
    author_email="alex@wallar.me",
    description="AI-Powered Bikepacking Trip Planner",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/a20r/dirtgenie",
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
