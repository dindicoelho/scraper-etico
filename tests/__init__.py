"""
Pacote de testes para ScraperEtico

Este pacote contém testes unitários para todas as principais classes:
- ScraperEtico: Classe principal para verificação de robots.txt
- RobotsAnalyzer: Análise avançada de arquivos robots.txt  
- BatchProcessor: Processamento em lote e exportação de resultados

Para executar todos os testes:
    python -m pytest tests/

Para executar testes específicos:
    python -m pytest tests/test_scraper_etico.py
    python -m pytest tests/test_analyzer.py
    python -m pytest tests/test_batch_processor.py

Para executar com coverage:
    python -m pytest --cov=src tests/
"""