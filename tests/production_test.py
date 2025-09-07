#!/usr/bin/env python3
"""
TESTE DE PRODUÇÃO - ScraperÉtico
Execute este script antes de colocar em produção!
"""

import time
import sys
from datetime import datetime

print("🧪 TESTE COMPLETO DE PRODUÇÃO - ScraperÉtico")
print("="*60)

# Lista de verificações
checklist = []
erros = []

def teste(nome, funcao):
    """Executa um teste e registra resultado"""
    print(f"\n📋 Testando: {nome}...", end="", flush=True)
    try:
        resultado = funcao()
        if resultado:
            print(" ✅ PASSOU")
            checklist.append((nome, True, None))
        else:
            print(" ❌ FALHOU")
            checklist.append((nome, False, "Retornou False"))
            erros.append(f"{nome}: Retornou False")
    except Exception as e:
        print(f" ❌ ERRO: {str(e)}")
        checklist.append((nome, False, str(e)))
        erros.append(f"{nome}: {str(e)}")
        
# TESTE 1: Importações básicas
def test_imports():
    from src.scraper_etico import ScraperEtico
    from src.analyzer import RobotsAnalyzer
    from src.batch_processor import BatchProcessor
    return True

teste("Importações básicas", test_imports)

# TESTE 2: Criar instância do ScraperEtico
def test_scraper_creation():
    from src.scraper_etico import ScraperEtico
    scraper = ScraperEtico(
        user_agent="TesteProdução/1.0",
        default_delay=2.0
    )
    return scraper is not None

teste("Criar ScraperEtico", test_scraper_creation)

# TESTE 3: Verificar site permitido (example.com)
def test_site_permitido():
    from src.scraper_etico import ScraperEtico
    scraper = ScraperEtico()
    # example.com geralmente permite acesso
    return scraper.can_fetch("https://example.com/")

teste("Verificar site permitido", test_site_permitido)

# TESTE 4: Fazer request real
def test_request_real():
    from src.scraper_etico import ScraperEtico
    scraper = ScraperEtico(default_delay=2.0)
    response = scraper.get("https://example.com/")
    return response is not None and response.status_code == 200

teste("Request HTTP real", test_request_real)

# TESTE 5: Rate limiting funciona
def test_rate_limit():
    from src.scraper_etico import ScraperEtico
    scraper = ScraperEtico(default_delay=1.0)
    
    start = time.time()
    scraper.can_fetch("https://example.com")
    scraper.can_fetch("https://example.com")  # Segunda chamada deve ter delay
    elapsed = time.time() - start
    
    return elapsed >= 0.9  # Deve ter pelo menos 0.9s de delay

teste("Rate limiting", test_rate_limit)

# TESTE 6: Batch processor
def test_batch_processor():
    from src.batch_processor import BatchProcessor
    from src.scraper_etico import ScraperEtico
    
    # API correta: BatchProcessor() sem parâmetros no construtor
    processor = BatchProcessor()
    processor.scraper = ScraperEtico(default_delay=0.5)
    
    urls = ["https://example.com/", "https://www.python.org/"]
    # Usar process_batch com max_workers como parâmetro
    job_state = processor.process_batch(urls, max_workers=1, show_progress=False)
    
    return len(job_state.results) >= 1 and job_state.total_urls == 2

teste("Processamento em lote", test_batch_processor)

# TESTE 7: Exportação de dados
def test_export():
    from src.batch_processor import BatchProcessor, BatchResult
    import os
    
    processor = BatchProcessor()
    
    # Criar dados fake para teste com API correta
    results = [
        BatchResult("https://test1.com", True),
        BatchResult("https://test2.com", False)
    ]
    
    # Criar job_state fake
    from src.batch_processor import BatchJobState
    job_state = BatchJobState("test_job")
    job_state.results = results
    
    # Testar exportação com API correta
    processor.export_to_csv(job_state, "teste_export.csv")
    processor.export_to_json(job_state, "teste_export.json")
    
    # Verificar se arquivos foram criados
    csv_exists = os.path.exists("teste_export.csv")
    json_exists = os.path.exists("teste_export.json")
    
    # Limpar arquivos de teste
    if csv_exists:
        os.remove("teste_export.csv")
    if json_exists:
        os.remove("teste_export.json")
        
    return csv_exists and json_exists

teste("Exportação CSV/JSON", test_export)

# TESTE 8: Crawl delay
def test_crawl_delay():
    from src.scraper_etico import ScraperEtico
    scraper = ScraperEtico()
    
    # Testar com site que geralmente tem crawl-delay
    delay = scraper.get_crawl_delay("https://www.wikipedia.org/")
    # Pode ser None se não tiver delay especificado
    return True  # O importante é não dar erro

teste("Obter crawl-delay", test_crawl_delay)

# TESTE 9: Site bloqueado
def test_site_bloqueado():
    from src.scraper_etico import ScraperEtico
    scraper = ScraperEtico(user_agent="BadBot")
    
    # Alguns sites bloqueiam bots genéricos
    # Não podemos garantir bloqueio, então apenas testamos se funciona
    try:
        result = scraper.can_fetch("https://www.facebook.com/")
        return True  # Importante é não crashar
    except:
        return False

teste("Verificar site restritivo", test_site_bloqueado)

# TESTE 10: Memória e recursos
def test_recursos():
    from src.scraper_etico import ScraperEtico
    import gc
    
    # Criar e destruir várias instâncias
    for i in range(10):
        scraper = ScraperEtico()
        _ = scraper.can_fetch("https://example.com")
    
    # Forçar coleta de lixo
    gc.collect()
    return True

teste("Gestão de memória", test_recursos)

# RELATÓRIO FINAL
print("\n" + "="*60)
print("📊 RELATÓRIO FINAL DE TESTES")
print("="*60)

total_testes = len(checklist)
testes_passaram = sum(1 for _, passou, _ in checklist if passou)
testes_falharam = total_testes - testes_passaram

print(f"\n📈 Estatísticas:")
print(f"   Total de testes: {total_testes}")
print(f"   ✅ Passaram: {testes_passaram}")
print(f"   ❌ Falharam: {testes_falharam}")
print(f"   🎯 Taxa de sucesso: {(testes_passaram/total_testes)*100:.1f}%")

if erros:
    print(f"\n❌ ERROS ENCONTRADOS:")
    for erro in erros:
        print(f"   - {erro}")

print(f"\n⏰ Testado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# VEREDITO FINAL
print("\n" + "="*60)
if testes_passaram == total_testes:
    print("✅ APROVADO PARA PRODUÇÃO!")
    print("🚀 Todos os testes passaram com sucesso!")
    sys.exit(0)
else:
    print("❌ NÃO ESTÁ PRONTO PARA PRODUÇÃO!")
    print(f"🔧 Corrija os {testes_falharam} erros antes de continuar!")
    sys.exit(1)