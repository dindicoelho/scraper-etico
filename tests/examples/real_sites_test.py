from src.scraper_etico import ScraperEtico
from src.batch_processor import BatchProcessor
import time

print("🌐 Testando sites REAIS...")

# Configurar scraper mais educado para sites reais
scraper = ScraperEtico(
    user_agent="MonitorPrecos/1.0 (+https://meusite.com/contato; contato@meusite.com)",
    default_delay=3.0,  # 3 segundos entre requests (mais respeitoso)
    timeout=10.0
)

# Sites governamentais brasileiros (geralmente permitem)
sites_governamentais = [
    "https://www.gov.br",
    "https://www.ibge.gov.br",
    "https://www.bcb.gov.br",
    "https://www.receita.fazenda.gov.br"
]

# Sites de notícias (alguns podem bloquear)
sites_noticias = [
    "https://g1.globo.com",
    "https://www1.folha.uol.com.br", 
    "https://www.estadao.com.br",
    "https://www.bbc.com/portuguese"
]

# Sites de e-commerce (geralmente bloqueiam scraping)
sites_ecommerce = [
    "https://www.mercadolivre.com.br",
    "https://www.magazineluiza.com.br",
    "https://www.americanas.com.br"
]

def testar_categoria(nome, sites):
    print(f"\n{'='*50}")
    print(f"🎯 TESTANDO: {nome}")
    print(f"{'='*50}")
    
    for site in sites:
        print(f"\n🔍 Analisando: {site}")
        
        try:
            # Verificar se pode acessar
            pode_acessar = scraper.can_fetch(site)
            
            if pode_acessar:
                print(f"   ✅ ROBOTS.TXT: Permitido")
                
                # Tentar acessar página inicial
                response = scraper.get(site)
                
                if response:
                    print(f"   📄 REQUEST: Sucesso! {len(response.text)} caracteres")
                    print(f"   🌐 STATUS: {response.status_code}")
                else:
                    print(f"   ❌ REQUEST: Falhou (bloqueado ou erro)")
                    
            else:
                print(f"   🚫 ROBOTS.TXT: Bloqueado")
                
            # Verificar crawl-delay
            delay = scraper.get_crawl_delay(site)
            if delay:
                print(f"   ⏱️  CRAWL-DELAY: {delay}s (recomendado)")
            else:
                print(f"   ⏱️  CRAWL-DELAY: Não especificado")
                
        except Exception as e:
            print(f"   💥 ERRO: {str(e)}")
        
        # Pausa entre sites
        time.sleep(2)

# Executar testes
print("⚠️  ATENÇÃO: Testando com delays de 3 segundos entre requests")
print("📝 Sempre verifique se está respeitando os termos de uso!")

testar_categoria("SITES GOVERNAMENTAIS", sites_governamentais[:2])  # Só 2 pra não demorar
testar_categoria("SITES DE NOTÍCIAS", sites_noticias[:2])
testar_categoria("SITES DE E-COMMERCE", sites_ecommerce[:1])  # Só 1, eles geralmente bloqueiam

print(f"\n🎉 Teste concluído!")
print(f"💡 Dica: Sites que permitem podem ser usados para coleta de dados")
print(f"🚨 LEMBRE: Sempre respeite robots.txt e termos de uso!")