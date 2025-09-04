"""
Testes unitários para BatchProcessor
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
import sys
import time
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from batch_processor import BatchProcessor, BatchResult, ProcessingStats


class TestBatchResult(unittest.TestCase):
    """Testes para a classe BatchResult"""
    
    def test_batch_result_creation(self):
        """Teste criação de BatchResult"""
        result = BatchResult(
            url="https://example.com",
            domain="example.com",
            allowed=True,
            robots_found=True,
            crawl_delay=5.0,
            processing_time=1.5,
            error=None
        )
        
        self.assertEqual(result.url, "https://example.com")
        self.assertEqual(result.domain, "example.com")
        self.assertTrue(result.allowed)
        self.assertTrue(result.robots_found)
        self.assertEqual(result.crawl_delay, 5.0)
        self.assertEqual(result.processing_time, 1.5)
        self.assertIsNone(result.error)
    
    def test_batch_result_to_dict(self):
        """Teste conversão de BatchResult para dict"""
        result = BatchResult(
            url="https://example.com",
            domain="example.com", 
            allowed=False,
            robots_found=True,
            error="Test error"
        )
        
        result_dict = result.to_dict()
        
        self.assertEqual(result_dict['url'], "https://example.com")
        self.assertEqual(result_dict['domain'], "example.com")
        self.assertFalse(result_dict['allowed'])
        self.assertTrue(result_dict['robots_found'])
        self.assertEqual(result_dict['error'], "Test error")


class TestProcessingStats(unittest.TestCase):
    """Testes para a classe ProcessingStats"""
    
    def test_processing_stats_creation(self):
        """Teste criação de ProcessingStats"""
        stats = ProcessingStats()
        
        self.assertEqual(stats.total_urls, 0)
        self.assertEqual(stats.successful, 0)
        self.assertEqual(stats.failed, 0)
        self.assertEqual(stats.allowed, 0)
        self.assertEqual(stats.blocked, 0)
        self.assertEqual(stats.robots_found, 0)
    
    def test_processing_stats_update(self):
        """Teste atualização de ProcessingStats"""
        stats = ProcessingStats()
        
        # Resultado bem-sucedido e permitido
        result1 = BatchResult(
            url="https://example1.com",
            domain="example1.com",
            allowed=True,
            robots_found=True
        )
        stats.update(result1)
        
        self.assertEqual(stats.total_urls, 1)
        self.assertEqual(stats.successful, 1)
        self.assertEqual(stats.allowed, 1)
        self.assertEqual(stats.robots_found, 1)
        
        # Resultado bloqueado
        result2 = BatchResult(
            url="https://example2.com", 
            domain="example2.com",
            allowed=False,
            robots_found=True
        )
        stats.update(result2)
        
        self.assertEqual(stats.total_urls, 2)
        self.assertEqual(stats.successful, 2)
        self.assertEqual(stats.blocked, 1)
        
        # Resultado com erro
        result3 = BatchResult(
            url="https://example3.com",
            domain="example3.com", 
            allowed=False,
            robots_found=False,
            error="Connection failed"
        )
        stats.update(result3)
        
        self.assertEqual(stats.total_urls, 3)
        self.assertEqual(stats.failed, 1)


class TestBatchProcessor(unittest.TestCase):
    """Testes para a classe BatchProcessor"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.processor = BatchProcessor(
            user_agent="TestBot/1.0",
            max_workers=2,
            default_delay=0.1,  # Delay menor para testes
            timeout=5.0
        )
    
    def test_init_default_parameters(self):
        """Teste inicialização com parâmetros padrão"""
        processor = BatchProcessor()
        
        self.assertEqual(processor.max_workers, 3)
        self.assertEqual(processor.batch_delay, 0.5)
        self.assertIsNotNone(processor.scraper)
    
    def test_init_custom_parameters(self):
        """Teste inicialização com parâmetros customizados"""
        self.assertEqual(self.processor.max_workers, 2)
        self.assertEqual(self.processor.scraper.user_agent, "TestBot/1.0")
        self.assertEqual(self.processor.scraper.default_delay, 0.1)
    
    @patch('batch_processor.ScraperEtico')
    def test_processar_url_individual_sucesso(self, mock_scraper_class):
        """Teste processamento de URL individual com sucesso"""
        # Mock do scraper
        mock_scraper = Mock()
        mock_scraper.verificar_robots.return_value = {
            'permitido': True,
            'dominio': 'example.com',
            'robots_encontrado': True,
            'crawl_delay': 2.0,
            'timestamp': '2023-01-01T00:00:00'
        }
        mock_scraper_class.return_value = mock_scraper
        
        # Recriar processor para usar o mock
        processor = BatchProcessor()
        
        start_time = time.time()
        resultado = processor._processar_url_individual("https://example.com", start_time)
        
        self.assertIsInstance(resultado, BatchResult)
        self.assertEqual(resultado.url, "https://example.com")
        self.assertTrue(resultado.allowed)
        self.assertEqual(resultado.domain, "example.com")
        self.assertTrue(resultado.robots_found)
        self.assertEqual(resultado.crawl_delay, 2.0)
        self.assertIsNone(resultado.error)
    
    @patch('batch_processor.ScraperEtico')
    def test_processar_url_individual_erro(self, mock_scraper_class):
        """Teste processamento de URL individual com erro"""
        # Mock do scraper que gera exceção
        mock_scraper = Mock()
        mock_scraper.verificar_robots.side_effect = Exception("Network error")
        mock_scraper_class.return_value = mock_scraper
        
        processor = BatchProcessor()
        
        start_time = time.time()
        resultado = processor._processar_url_individual("https://example.com", start_time)
        
        self.assertIsInstance(resultado, BatchResult)
        self.assertFalse(resultado.allowed)
        self.assertIsNotNone(resultado.error)
        self.assertIn("Network error", resultado.error)
    
    @patch.object(BatchProcessor, '_processar_url_individual')
    def test_processar_lote_sequencial(self, mock_processar):
        """Teste processamento sequencial de lote"""
        # Mock dos resultados
        mock_results = [
            BatchResult("https://example1.com", "example1.com", True, True),
            BatchResult("https://example2.com", "example2.com", False, True),
        ]
        mock_processar.side_effect = mock_results
        
        urls = ["https://example1.com", "https://example2.com"]
        resultados, stats = self.processor.processar_lote(urls, paralelo=False)
        
        self.assertEqual(len(resultados), 2)
        self.assertEqual(stats.total_urls, 2)
        self.assertEqual(stats.successful, 2)
        self.assertEqual(stats.allowed, 1)
        self.assertEqual(stats.blocked, 1)
    
    @patch.object(BatchProcessor, '_processar_url_individual')
    def test_processar_lote_paralelo(self, mock_processar):
        """Teste processamento paralelo de lote"""
        mock_results = [
            BatchResult("https://example1.com", "example1.com", True, True),
            BatchResult("https://example2.com", "example2.com", True, False),
        ]
        mock_processar.side_effect = mock_results
        
        urls = ["https://example1.com", "https://example2.com"]
        resultados, stats = self.processor.processar_lote(urls, paralelo=True)
        
        self.assertEqual(len(resultados), 2)
        self.assertEqual(stats.total_urls, 2)
        self.assertEqual(stats.allowed, 2)
    
    def test_processar_lote_lista_vazia(self):
        """Teste processamento de lista vazia"""
        resultados, stats = self.processor.processar_lote([])
        
        self.assertEqual(len(resultados), 0)
        self.assertEqual(stats.total_urls, 0)
    
    def test_processar_lote_com_callback(self):
        """Teste processamento com callback de progresso"""
        callback_calls = []
        
        def callback_test(url, resultado):
            callback_calls.append((url, resultado.allowed))
        
        with patch.object(self.processor, '_processar_url_individual') as mock_processar:
            mock_processar.return_value = BatchResult("https://example.com", "example.com", True, True)
            
            urls = ["https://example.com"]
            self.processor.processar_lote(urls, callback_progresso=callback_test)
            
            self.assertEqual(len(callback_calls), 1)
            self.assertEqual(callback_calls[0][0], "https://example.com")
            self.assertTrue(callback_calls[0][1])


class TestBatchProcessorExport(unittest.TestCase):
    """Testes para funcionalidades de export do BatchProcessor"""
    
    def setUp(self):
        self.processor = BatchProcessor()
        
        # Resultados de exemplo para testes
        self.sample_results = [
            BatchResult(
                url="https://example1.com",
                domain="example1.com", 
                allowed=True,
                robots_found=True,
                crawl_delay=1.0
            ),
            BatchResult(
                url="https://example2.com",
                domain="example2.com",
                allowed=False, 
                robots_found=True,
                crawl_delay=2.0
            )
        ]
    
    def test_exportar_csv(self):
        """Teste exportação para CSV"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            arquivo_csv = f.name
        
        try:
            self.processor.exportar_csv(self.sample_results, arquivo_csv)
            
            # Verificar se arquivo foi criado
            self.assertTrue(os.path.exists(arquivo_csv))
            
            # Verificar conteúdo
            with open(arquivo_csv, 'r') as f:
                conteudo = f.read()
                self.assertIn('url,domain,allowed', conteudo)
                self.assertIn('example1.com', conteudo)
                self.assertIn('example2.com', conteudo)
        
        finally:
            # Limpar arquivo de teste
            if os.path.exists(arquivo_csv):
                os.unlink(arquivo_csv)
    
    def test_exportar_json(self):
        """Teste exportação para JSON"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            arquivo_json = f.name
        
        try:
            self.processor.exportar_json(self.sample_results, arquivo_json)
            
            # Verificar se arquivo foi criado
            self.assertTrue(os.path.exists(arquivo_json))
            
            # Verificar conteúdo
            import json
            with open(arquivo_json, 'r') as f:
                dados = json.load(f)
                self.assertEqual(len(dados), 2)
                self.assertEqual(dados[0]['url'], 'https://example1.com')
                self.assertTrue(dados[0]['allowed'])
        
        finally:
            # Limpar arquivo de teste
            if os.path.exists(arquivo_json):
                os.unlink(arquivo_json)


class TestBatchProcessorResume(unittest.TestCase):
    """Testes para funcionalidade de resume do BatchProcessor"""
    
    def setUp(self):
        self.processor = BatchProcessor()
        
        # Criar diretório temporário para testes
        self.temp_dir = tempfile.mkdtemp()
        self.processor.estado_dir = Path(self.temp_dir)
    
    def tearDown(self):
        """Limpeza após testes"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_salvar_estado(self):
        """Teste salvamento de estado"""
        urls = ["https://example1.com", "https://example2.com"]
        resultados = [
            BatchResult("https://example1.com", "example1.com", True, True)
        ]
        
        batch_id = self.processor._salvar_estado(urls, resultados, 1)
        
        # Verificar se arquivo foi criado
        arquivo_estado = self.processor.estado_dir / f"batch_{batch_id}.pkl"
        self.assertTrue(arquivo_estado.exists())
    
    def test_carregar_estado(self):
        """Teste carregamento de estado"""
        # Primeiro, salvar um estado
        urls = ["https://example1.com", "https://example2.com"]
        resultados = [
            BatchResult("https://example1.com", "example1.com", True, True)
        ]
        
        batch_id = self.processor._salvar_estado(urls, resultados, 1)
        
        # Depois, carregar o estado
        estado_carregado = self.processor._carregar_estado(batch_id)
        
        self.assertIsNotNone(estado_carregado)
        self.assertEqual(len(estado_carregado['urls_originais']), 2)
        self.assertEqual(len(estado_carregado['resultados_processados']), 1)
        self.assertEqual(estado_carregado['indice_atual'], 1)
    
    def test_carregar_estado_inexistente(self):
        """Teste carregamento de estado inexistente"""
        estado = self.processor._carregar_estado("batch_inexistente")
        self.assertIsNone(estado)


if __name__ == '__main__':
    # Configurar logging para os testes  
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Executar testes
    unittest.main(verbosity=2)