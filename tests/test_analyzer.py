"""
Testes unitários para RobotsAnalyzer
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analyzer import RobotsAnalyzer


class TestRobotsAnalyzer(unittest.TestCase):
    """Testes para a classe RobotsAnalyzer"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.analyzer = RobotsAnalyzer()
    
    def test_init(self):
        """Teste inicialização"""
        self.assertIsInstance(self.analyzer, RobotsAnalyzer)
        self.assertIsNotNone(self.analyzer.scraper)
    
    def test_extrair_user_agents_simples(self):
        """Teste extração de user-agents simples"""
        robots_content = """
        User-agent: *
        Disallow: /admin
        
        User-agent: Googlebot
        Disallow: /private
        """
        
        user_agents = self.analyzer._extrair_user_agents(robots_content)
        
        self.assertIn('*', user_agents)
        self.assertIn('Googlebot', user_agents)
        self.assertEqual(len(user_agents), 2)
    
    def test_extrair_user_agents_case_insensitive(self):
        """Teste extração de user-agents com case variations"""
        robots_content = """
        user-agent: *
        disallow: /admin
        
        USER-AGENT: Googlebot
        DISALLOW: /private
        """
        
        user_agents = self.analyzer._extrair_user_agents(robots_content)
        
        self.assertIn('*', user_agents)
        self.assertIn('Googlebot', user_agents)
    
    def test_extrair_user_agents_vazio(self):
        """Teste extração de user-agents de conteúdo vazio"""
        user_agents = self.analyzer._extrair_user_agents("")
        self.assertEqual(len(user_agents), 0)
    
    def test_extrair_sitemaps(self):
        """Teste extração de sitemaps"""
        robots_content = """
        User-agent: *
        Disallow: /admin
        
        Sitemap: https://example.com/sitemap.xml
        Sitemap: https://example.com/sitemap-news.xml
        """
        
        sitemaps = self.analyzer._extrair_sitemaps(robots_content)
        
        self.assertIn('https://example.com/sitemap.xml', sitemaps)
        self.assertIn('https://example.com/sitemap-news.xml', sitemaps)
        self.assertEqual(len(sitemaps), 2)
    
    def test_extrair_sitemaps_case_insensitive(self):
        """Teste extração de sitemaps com case variations"""
        robots_content = """
        sitemap: https://example.com/sitemap1.xml
        SITEMAP: https://example.com/sitemap2.xml
        """
        
        sitemaps = self.analyzer._extrair_sitemaps(robots_content)
        
        self.assertEqual(len(sitemaps), 2)
    
    def test_extrair_crawl_delays(self):
        """Teste extração de crawl-delays"""
        robots_content = """
        User-agent: *
        Crawl-delay: 5
        Disallow: /admin
        
        User-agent: Googlebot
        Crawl-delay: 10
        Disallow: /private
        """
        
        crawl_delays = self.analyzer._extrair_crawl_delays(robots_content)
        
        self.assertEqual(crawl_delays['*'], 5.0)
        self.assertEqual(crawl_delays['Googlebot'], 10.0)
    
    def test_extrair_crawl_delays_invalidos(self):
        """Teste extração de crawl-delays com valores inválidos"""
        robots_content = """
        User-agent: *
        Crawl-delay: invalid
        
        User-agent: Googlebot
        Crawl-delay: -5
        """
        
        crawl_delays = self.analyzer._extrair_crawl_delays(robots_content)
        
        # Valores inválidos devem ser ignorados
        self.assertEqual(len(crawl_delays), 0)
    
    def test_contar_regras(self):
        """Teste contagem de regras"""
        robots_content = """
        User-agent: *
        Disallow: /admin
        Disallow: /private
        Allow: /public
        
        User-agent: Googlebot
        Disallow: /secret
        """
        
        total_regras = self.analyzer._contar_regras(robots_content)
        
        # 3 regras para * + 1 regra para Googlebot = 4 total
        self.assertEqual(total_regras, 4)
    
    def test_contar_regras_vazio(self):
        """Teste contagem de regras com conteúdo vazio"""
        total_regras = self.analyzer._contar_regras("")
        self.assertEqual(total_regras, 0)
    
    @patch.object(RobotsAnalyzer, '_baixar_robots_txt')
    def test_analisar_site_sucesso(self, mock_baixar):
        """Teste análise completa de site com sucesso"""
        robots_content = """
        User-agent: *
        Crawl-delay: 5
        Disallow: /admin
        Allow: /public
        
        User-agent: Googlebot
        Disallow: /private
        
        Sitemap: https://example.com/sitemap.xml
        """
        mock_baixar.return_value = robots_content
        
        resultado = self.analyzer.analisar_site("https://example.com")
        
        self.assertTrue(resultado['robots_encontrado'])
        self.assertEqual(resultado['dominio'], 'example.com')
        self.assertEqual(len(resultado['user_agents']), 2)
        self.assertIn('*', resultado['user_agents'])
        self.assertIn('Googlebot', resultado['user_agents'])
        self.assertEqual(len(resultado['sitemaps']), 1)
        self.assertEqual(resultado['total_regras'], 3)
        self.assertEqual(resultado['crawl_delays']['*'], 5.0)
        self.assertIsNotNone(resultado['timestamp'])
    
    @patch.object(RobotsAnalyzer, '_baixar_robots_txt')
    def test_analisar_site_robots_nao_encontrado(self, mock_baixar):
        """Teste análise de site sem robots.txt"""
        mock_baixar.return_value = None
        
        resultado = self.analyzer.analisar_site("https://example.com")
        
        self.assertFalse(resultado['robots_encontrado'])
        self.assertEqual(resultado['dominio'], 'example.com')
        self.assertEqual(len(resultado['user_agents']), 0)
        self.assertEqual(len(resultado['sitemaps']), 0)
        self.assertEqual(resultado['total_regras'], 0)
        self.assertEqual(len(resultado['crawl_delays']), 0)
    
    def test_analisar_site_url_invalida(self):
        """Teste análise com URL inválida"""
        with self.assertRaises(ValueError):
            self.analyzer.analisar_site("url-invalida")
    
    @patch.object(RobotsAnalyzer, '_baixar_robots_txt')
    def test_analisar_lote_sites(self, mock_baixar):
        """Teste análise em lote de múltiplos sites"""
        def mock_robots_response(url):
            if 'example1' in url:
                return "User-agent: *\nDisallow: /admin"
            elif 'example2' in url:
                return "User-agent: *\nDisallow: /private"
            return None
        
        mock_baixar.side_effect = mock_robots_response
        
        urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com"
        ]
        
        resultados = self.analyzer.analisar_lote(urls)
        
        self.assertEqual(len(resultados), 3)
        self.assertTrue(resultados["https://example1.com"]['robots_encontrado'])
        self.assertTrue(resultados["https://example2.com"]['robots_encontrado'])
        self.assertFalse(resultados["https://example3.com"]['robots_encontrado'])
    
    def test_analisar_lote_lista_vazia(self):
        """Teste análise em lote com lista vazia"""
        resultados = self.analyzer.analisar_lote([])
        self.assertEqual(len(resultados), 0)
    
    def test_analisar_lote_url_invalida(self):
        """Teste análise em lote com URL inválida"""
        urls = ["https://example.com", "url-invalida"]
        
        with self.assertRaises(ValueError):
            self.analyzer.analisar_lote(urls)
    
    def test_extrair_robots_complexo(self):
        """Teste extração de robots.txt complexo com múltiplas seções"""
        robots_content = """
        # Comentário
        User-agent: *
        Disallow: /admin
        Disallow: /temp
        Allow: /admin/public
        Crawl-delay: 1
        
        User-agent: Googlebot
        Disallow: /nodex
        Allow: /
        
        User-agent: Bingbot
        Crawl-delay: 2
        Disallow: /private
        
        Sitemap: https://example.com/sitemap.xml
        Sitemap: https://example.com/sitemap-images.xml
        
        # Outro comentário
        User-agent: BadBot
        Disallow: /
        """
        
        # Testar user-agents
        user_agents = self.analyzer._extrair_user_agents(robots_content)
        expected_agents = {'*', 'Googlebot', 'Bingbot', 'BadBot'}
        self.assertEqual(set(user_agents), expected_agents)
        
        # Testar sitemaps
        sitemaps = self.analyzer._extrair_sitemaps(robots_content)
        self.assertEqual(len(sitemaps), 2)
        
        # Testar crawl-delays
        crawl_delays = self.analyzer._extrair_crawl_delays(robots_content)
        self.assertEqual(crawl_delays['*'], 1.0)
        self.assertEqual(crawl_delays['Bingbot'], 2.0)
        self.assertNotIn('Googlebot', crawl_delays)  # Não tem crawl-delay
        
        # Testar contagem de regras
        total_regras = self.analyzer._contar_regras(robots_content)
        # * tem 3 regras, Googlebot tem 2, Bingbot tem 1, BadBot tem 1 = 7 total
        self.assertEqual(total_regras, 7)


class TestRobotsAnalyzerUtils(unittest.TestCase):
    """Testes para funções utilitárias do RobotsAnalyzer"""
    
    def setUp(self):
        self.analyzer = RobotsAnalyzer()
    
    def test_robots_txt_multiline_parsing(self):
        """Teste parsing de robots.txt com múltiplas linhas por diretiva"""
        robots_content = """
        User-agent: *
        Disallow: /admin
        Disallow: /temp
        Disallow: /private
        Allow: /public
        Allow: /images
        """
        
        total_regras = self.analyzer._contar_regras(robots_content)
        self.assertEqual(total_regras, 5)  # 3 Disallow + 2 Allow
    
    def test_robots_txt_whitespace_handling(self):
        """Teste handling de espaços em branco"""
        robots_content = """
          User-agent:    *   
          Disallow:   /admin   
          Allow:     /public
          
          Sitemap:   https://example.com/sitemap.xml   
        """
        
        user_agents = self.analyzer._extrair_user_agents(robots_content)
        self.assertIn('*', user_agents)
        
        sitemaps = self.analyzer._extrair_sitemaps(robots_content)
        self.assertIn('https://example.com/sitemap.xml', sitemaps)


if __name__ == '__main__':
    # Configurar logging para os testes
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Executar testes
    unittest.main(verbosity=2)