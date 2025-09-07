#!/usr/bin/env python3
"""
Setup script for EthicalScraper - Ethical Web Scraper
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Package information
setup(
    name="ethical-scraper",
    version="1.0.0",
    author="Public Price Monitor",
    author_email="contact@example.com",
    description="A Python library for ethical web scraping that automatically respects robots.txt",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dindicoelho/scraper-etico",
    project_urls={
        "Bug Tracker": "https://github.com/dindicoelho/scraper-etico/issues",
        "Documentation": "https://github.com/dindicoelho/scraper-etico/blob/main/README.md",
        "Tutorial": "https://github.com/dindicoelho/scraper-etico/blob/main/notebooks/ethical_scraper_tutorial.ipynb",
    },
    
    # Packages and modules
    packages=find_packages(),
    package_dir={"": "."},
    py_modules=["src.scraper_etico", "src.analyzer", "src.batch_processor", "src.utils"],
    
    # Dependencies
    install_requires=requirements,
    
    # Optional dependencies
    extras_require={
        'analysis': ['pandas>=1.0.0', 'matplotlib>=3.0.0'],
        'progress': ['tqdm>=4.0.0'],
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.0.0',
            'jupyter>=1.0.0',
        ],
        'all': [
            'pandas>=1.0.0', 
            'matplotlib>=3.0.0',
            'tqdm>=4.0.0',
            'jupyter>=1.0.0',
        ]
    },
    
    # PyPI classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    
    # Minimum Python version
    python_requires=">=3.8",
    
    # Keywords
    keywords=[
        "web-scraping", "robots.txt", "ethical-scraping", "rate-limiting",
        "web-crawler", "data-extraction", "compliance", "automation"
    ],
    
    # Command line scripts
    entry_points={
        'console_scripts': [
            'ethical-scraper=src.scraper_etico:main',
        ],
    },
    
    # Include additional files
    include_package_data=True,
    package_data={
        '': [
            'README.md',
            'requirements.txt',
            'notebooks/*.ipynb',
            'examples/*.py',
        ],
    },
    
    # Additional metadata
    zip_safe=False,
    platforms=['any'],
    
    # License
    license="MIT",
    
    # Download URL (would be the release link)
    download_url="https://github.com/dindicoelho/scraper-etico/archive/v1.0.0.tar.gz",
)