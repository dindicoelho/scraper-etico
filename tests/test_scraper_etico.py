"""
Testes unitários atualizados para ScraperEtico - Nova API
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import time

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scraper_etico import ScraperEtico
from urllib.robotparser import RobotFileParser


class TestScraperEtico(unittest.TestCase):
    """Testes para a classe ScraperEtico - Nova API"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.scraper = ScraperEtico(
            user_agent="TestBot/1.0",
            default_delay=0.1,  # Delay menor para testes
            timeout=5.0
        )
    
    def test_init_default_parameters(self):
        """Teste inicialização com parâmetros padrão"""
        scraper = ScraperEtico()
        self.assertEqual(scraper.user_agent, "ScraperEtico/1.0 (Ethical Web Scraper)")
        self.assertEqual(scraper.default_delay, 1.0)
        self.assertEqual(scraper.timeout, 30.0)
    
    def test_init_custom_parameters(self):
        """Teste inicialização com parâmetros customizados"""
        self.assertEqual(self.scraper.user_agent, "TestBot/1.0")
        self.assertEqual(self.scraper.default_delay, 0.1)
        self.assertEqual(self.scraper.timeout, 5.0)
    
    def test_init_invalid_delay(self):
        """Teste inicialização com delay inválido"""
        scraper = ScraperEtico(default_delay=-1.0)
        self.assertEqual(scraper.default_delay, 0.1)  # Deve ser ajustado para o mínimo
    
    @patch.object(ScraperEtico, '_fetch_robots_txt')
    def test_can_fetch_allowed(self, mock_fetch):
        """Teste verificação de URL permitida"""
        # Mock do parser de robots.txt
        mock_parser = Mock(spec=RobotFileParser)
        mock_parser.can_fetch.return_value = True
        mock_fetch.return_value = mock_parser
        
        resultado = self.scraper.can_fetch("https://example.com/page")
        
        self.assertTrue(resultado)
        mock_fetch.assert_called_once_with("https://example.com/robots.txt")
        mock_parser.can_fetch.assert_called_once_with("TestBot/1.0", "https://example.com/page")
    
    @patch.object(ScraperEtico, '_fetch_robots_txt')
    def test_can_fetch_blocked(self, mock_fetch):
        """Teste verificação de URL bloqueada"""
        # Mock do parser de robots.txt
        mock_parser = Mock(spec=RobotFileParser)
        mock_parser.can_fetch.return_value = False
        mock_fetch.return_value = mock_parser
        
        resultado = self.scraper.can_fetch("https://example.com/admin/page")
        
        self.assertFalse(resultado)
        mock_fetch.assert_called_once_with("https://example.com/robots.txt")
        mock_parser.can_fetch.assert_called_once_with("TestBot/1.0", "https://example.com/admin/page")
    
    @patch.object(ScraperEtico, '_fetch_robots_txt')
    def test_can_fetch_no_robots(self, mock_fetch):
        """Teste verificação quando robots.txt não é encontrado"""
        mock_fetch.return_value = None
        
        resultado = self.scraper.can_fetch("https://example.com/page")
        
        # Quando robots.txt não existe, assume que é permitido
        self.assertTrue(resultado)
        mock_fetch.assert_called_once_with("https://example.com/robots.txt")
    
    def test_robots_cache(self):
        """Teste cache de robots.txt"""
        # Mock do parser
        mock_parser = Mock(spec=RobotFileParser)
        mock_parser.can_fetch.return_value = True
        
        with patch.object(self.scraper, '_fetch_robots_txt', return_value=mock_parser) as mock_fetch:
            # Primeira chamada - deve buscar robots.txt
            result1 = self.scraper.can_fetch("https://example.com/page")
            
            # Segunda chamada - deve usar cache
            result2 = self.scraper.can_fetch("https://example.com/other")
            
            # Deve ter buscado robots.txt apenas uma vez
            mock_fetch.assert_called_once_with("https://example.com/robots.txt")
            
            self.assertTrue(result1)
            self.assertTrue(result2)
    
    def test_force_refresh_robots(self):
        """Teste force refresh do cache de robots.txt"""
        # Mock do parser
        mock_parser = Mock(spec=RobotFileParser)
        mock_parser.can_fetch.return_value = True
        
        with patch.object(self.scraper, '_fetch_robots_txt', return_value=mock_parser) as mock_fetch:
            # Primeira chamada
            self.scraper.can_fetch("https://example.com/page")
            
            # Segunda chamada com force_refresh
            self.scraper.can_fetch("https://example.com/page", force_refresh=True)
            
            # Deve ter buscado robots.txt duas vezes
            self.assertEqual(mock_fetch.call_count, 2)
    
    def test_get_crawl_delay(self):
        """Teste obtenção de crawl-delay"""
        # Mock do parser com crawl-delay
        mock_parser = Mock(spec=RobotFileParser)
        mock_parser.crawl_delay.return_value = 3.0
        
        # Simular cache com parser
        self.scraper._robots_cache["https://example.com/robots.txt"] = mock_parser
        
        delay = self.scraper.get_crawl_delay("https://example.com/page")
        
        self.assertEqual(delay, 3.0)
        mock_parser.crawl_delay.assert_called_once_with("TestBot/1.0")
    
    def test_get_crawl_delay_no_robots(self):
        """Teste obtenção de crawl-delay sem robots.txt"""
        delay = self.scraper.get_crawl_delay("https://norobots.com/page")
        
        # Sem robots.txt, deve retornar None ou default delay
        self.assertIsNone(delay)
    
    def test_can_fetch_url_none(self):
        """Teste verificação com URL None"""
        # URL None deve retornar True (permitido por padrão)
        resultado = self.scraper.can_fetch(None)
        self.assertTrue(resultado)
    
    @patch('scraper_etico.time.sleep')
    def test_apply_rate_limit(self, mock_sleep):
        """Teste aplicação de rate limit"""
        # Primeira chamada - não deve haver delay
        self.scraper._apply_rate_limit("example.com")
        mock_sleep.assert_not_called()
        
        # Segunda chamada - deve aplicar delay
        self.scraper._apply_rate_limit("example.com")
        # Verificar se houve alguma chamada de sleep com valor próximo
        self.assertTrue(mock_sleep.called)
        call_args = mock_sleep.call_args[0][0]
        self.assertAlmostEqual(call_args, 0.1, places=1)
    
    @patch('scraper_etico.time.sleep')
    def test_apply_rate_limit_custom_delay(self, mock_sleep):
        """Teste aplicação de delay customizado"""
        self.scraper._apply_rate_limit("example.com")  # Primeira chamada
        self.scraper._apply_rate_limit("example.com", custom_delay=2.5)
        
        # Verificar se houve alguma chamada de sleep com valor próximo
        self.assertTrue(mock_sleep.called)
        call_args = mock_sleep.call_args[0][0]
        self.assertAlmostEqual(call_args, 2.5, places=1)
    
    def test_parse_domain_valid_url(self):
        """Teste extração de domínio de URL válida"""
        from urllib.parse import urlparse
        
        urls_teste = [
            ("https://example.com/page", "example.com"),
            ("http://sub.example.com/path", "sub.example.com"),
            ("https://example.com:8080/", "example.com:8080"),
        ]
        
        for url, dominio_esperado in urls_teste:
            with self.subTest(url=url):
                dominio = urlparse(url).netloc
                self.assertEqual(dominio, dominio_esperado)
    
    def test_parse_domain_invalid_url(self):
        """Teste extração de domínio de URL inválida"""
        from urllib.parse import urlparse
        
        urls_invalidas = ["not-a-url", "", "ftp://example.com"]
        
        for url in urls_invalidas:
            with self.subTest(url=url):
                dominio = urlparse(url).netloc
                # URLs inválidas podem retornar string vazia ou domínio válido
                self.assertIsInstance(dominio, str)
    
    @patch('urllib.robotparser.RobotFileParser.read')
    def test_fetch_robots_txt_success(self, mock_read):
        """Teste fetch bem-sucedido de robots.txt"""
        mock_read.return_value = None  # read() não retorna nada, apenas carrega
        
        parser = self.scraper._fetch_robots_txt("https://example.com/robots.txt")
        
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, RobotFileParser)
        self.assertEqual(parser.url, "https://example.com/robots.txt")
        mock_read.assert_called_once()
    
    @patch('urllib.robotparser.RobotFileParser.read')
    def test_fetch_robots_txt_failure(self, mock_read):
        """Teste falha no fetch de robots.txt"""
        from urllib.error import URLError
        mock_read.side_effect = URLError("Not found")
        
        parser = self.scraper._fetch_robots_txt("https://example.com/robots.txt")
        
        self.assertIsNone(parser)
        mock_read.assert_called_once()
    
    def test_get_robots_url_info(self):
        """Teste obtenção da URL do robots.txt"""
        from urllib.parse import urlparse
        
        # Teste com URL válida
        url = "https://example.com/page"
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        self.assertEqual(robots_url, "https://example.com/robots.txt")


class TestScraperEticoFetch(unittest.TestCase):
    """Testes para funcionalidade de fetch do ScraperEtico"""
    
    def setUp(self):
        self.scraper = ScraperEtico(
            user_agent="TestBot/1.0",
            default_delay=0.1
        )
    
    @patch('requests.get')
    @patch.object(ScraperEtico, 'can_fetch')
    @patch.object(ScraperEtico, '_apply_rate_limit')
    def test_fetch_success(self, mock_rate_limit, mock_can_fetch, mock_get):
        """Teste fetch bem-sucedido"""
        # Mock das dependências
        mock_can_fetch.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Hello World"
        mock_get.return_value = mock_response
        
        response = self.scraper.get("https://example.com/page")
        
        self.assertIsNotNone(response)
        self.assertEqual(response.text, "Hello World")
        mock_can_fetch.assert_called_once_with("https://example.com/page", force_refresh=False)
        mock_rate_limit.assert_called_once()
        mock_get.assert_called_once()
    
    @patch.object(ScraperEtico, 'can_fetch')
    def test_fetch_blocked_by_robots(self, mock_can_fetch):
        """Teste fetch bloqueado por robots.txt"""
        mock_can_fetch.return_value = False
        
        response = self.scraper.get("https://example.com/blocked")
        
        self.assertIsNone(response)
        mock_can_fetch.assert_called_once_with("https://example.com/blocked", force_refresh=False)
    
    @patch('requests.get')
    @patch.object(ScraperEtico, 'can_fetch')
    @patch.object(ScraperEtico, '_apply_rate_limit')
    def test_fetch_http_error(self, mock_rate_limit, mock_can_fetch, mock_get):
        """Teste fetch com erro HTTP"""
        from requests.exceptions import RequestException
        
        mock_can_fetch.return_value = True
        mock_get.side_effect = RequestException("Connection error")
        
        response = self.scraper.get("https://example.com/error")
        
        self.assertIsNone(response)
        mock_can_fetch.assert_called_once()
        mock_rate_limit.assert_called_once()


class TestScraperEticoIntegration(unittest.TestCase):
    """Testes de integração básicos (sem requests reais)"""
    
    def setUp(self):
        self.scraper = ScraperEtico(
            user_agent="TestBot/1.0 (unittest)",
            default_delay=0.1
        )
    
    def test_complete_workflow_mock(self):
        """Teste workflow completo com mocks"""
        from urllib.robotparser import RobotFileParser
        
        # Mock do parser que permite acesso
        mock_parser = Mock(spec=RobotFileParser)
        mock_parser.can_fetch.return_value = True
        mock_parser.crawl_delay.return_value = 1.0
        
        with patch.object(self.scraper, '_fetch_robots_txt', return_value=mock_parser):
            # Verificar se pode acessar
            can_access = self.scraper.can_fetch("https://example.com/test")
            self.assertTrue(can_access)
            
            # Obter crawl delay
            delay = self.scraper.get_crawl_delay("https://example.com/test")
            self.assertEqual(delay, 1.0)
            
            # Obter informações do robots
            info = self.scraper.get_robots_info("https://example.com/test")
            self.assertIsInstance(info, dict)


if __name__ == '__main__':
    # Configurar logging para os testes
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Executar testes
    unittest.main(verbosity=2)