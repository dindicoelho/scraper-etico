#!/usr/bin/env python3
"""
Setup script para ScraperÉtico - Ethical Web Scraper
"""

from setuptools import setup, find_packages
import os
from pathlib import Path

# Ler README para descrição longa
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Ler requirements.txt
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

# Informações do pacote
setup(
    name="scraper-etico",
    version="1.0.0",
    author="Monitor Preços Públicos",
    author_email="contato@example.com",
    description="Uma biblioteca Python para web scraping ético que respeita robots.txt automaticamente",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/scraper-etico",
    project_urls={
        "Bug Tracker": "https://github.com/example/scraper-etico/issues",
        "Documentation": "https://github.com/example/scraper-etico/blob/main/README.md",
        "Tutorial": "https://github.com/example/scraper-etico/blob/main/notebooks/tutorial_scraper_etico.ipynb",
    },
    
    # Pacotes e módulos
    packages=find_packages(),
    package_dir={"": "."},
    py_modules=["src.scraper_etico", "src.analyzer", "src.batch_processor", "src.utils"],
    
    # Dependências
    install_requires=requirements,
    
    # Dependências opcionais
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
    
    # Classificadores PyPI
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
        "Natural Language :: Portuguese (Brazilian)",
    ],
    
    # Versão mínima do Python
    python_requires=">=3.8",
    
    # Palavras-chave
    keywords=[
        "web-scraping", "robots.txt", "ethical-scraping", "rate-limiting",
        "web-crawler", "data-extraction", "compliance", "automation"
    ],
    
    # Scripts de linha de comando
    entry_points={
        'console_scripts': [
            'scraper-etico=src.scraper_etico:main',
        ],
    },
    
    # Incluir arquivos adicionais
    include_package_data=True,
    package_data={
        '': [
            'README.md',
            'requirements.txt',
            'notebooks/*.ipynb',
            'examples/*.py',
        ],
    },
    
    # Metadados adicionais
    zip_safe=False,
    platforms=['any'],
    
    # Licença
    license="MIT",
    
    # Download URL (seria o link do release)
    download_url="https://github.com/example/scraper-etico/archive/v1.0.0.tar.gz",
)