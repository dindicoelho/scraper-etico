from src.scraper_etico import ScraperEtico
from src.analyzer import RobotsAnalyzer
import time
from datetime import datetime

print("💰 MONITOR DE PREÇOS PÚBLICOS")
print("="*50)

# Seus sites específicos (substitua pelos reais)
sites_licitacoes = [
    "https://www.comprasgovernamentais.gov.br",
    "https://www.gov.br/compras/pt-br",
    "https://www.bndes.gov.br/wps/portal/site/home/transparencia",
    # Adicione seus sites específicos aqui
]

sites_economicos = [
    "https://www.bcb.gov.br/controleinflacao/historicotaxasjuros",
    "https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos",
    "https://www.ipea.gov.br/portal/",
    # Adicione outros sites econômicos
]

# Configuração para sites governamentais (mais conservadora)
scraper = ScraperEtico(
    user_agent="MonitorPrecosPublicos/1.0 (+https://seusite.com/contato; seuemail@exemplo.com)",
    default_delay=5.0,  # 5 segundos - muito respeitoso
    timeout=20.0
)

analyzer = RobotsAnalyzer()

def analisar_site_detalhado(url, categoria):
    print(f"\n🔍 ANALISANDO: {url}")
    print(f"📂 Categoria: {categoria}")
    
    try:
        # Análise completa do robots.txt
        analise = analyzer.analisar_site(url)
        
        if analise['robots_encontrado']:
            print(f"   📋 Robots.txt: ✅ Encontrado")
            print(f"   🤖 User-agents: {len(analise['user_agents'])}")
            print(f"   📏 Total regras: {analise['total_regras']}")
            
            if analise['crawl_delays']:
                for ua, delay in analise['crawl_delays'].items():
                    print(f"   ⏱️  Delay para {ua}: {delay}s")
            
            if analise['sitemaps']:
                print(f"   🗺️  Sitemaps encontrados: {len(analise['sitemaps'])}")
                for sitemap in analise['sitemaps'][:2]:  # Mostrar só 2
                    print(f"      - {sitemap}")
        else:
            print(f"   📋 Robots.txt: ❌ Não encontrado")
        
        # Testar acesso específico
        pode_acessar = scraper.can_fetch(url)
        
        if pode_acessar:
            print(f"   🚦 Acesso: ✅ PERMITIDO")
            
            # Tentar request real
            response = scraper.get(url)
            if response:
                print(f"   📊 Request: ✅ Sucesso ({response.status_code})")
                print(f"   📄 Tamanho: {len(response.text)} caracteres")
                
                # Verificar se tem dados úteis
                if any(palavra in response.text.lower() for palavra in ['preço', 'valor', 'custo', 'licitação']):
                    print(f"   💰 Dados úteis: ✅ Possível conteúdo relevante")
                else:
                    print(f"   💰 Dados úteis: ⚠️  Conteúdo não identificado")
            else:
                print(f"   📊 Request: ❌ Falhou")
        else:
            print(f"   🚦 Acesso: ❌ BLOQUEADO pelo robots.txt")
            
    except Exception as e:
        print(f"   💥 ERRO: {str(e)}")
    
    print(f"   ⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Pausa respeitosa
    time.sleep(3)

# Executar análises
print(f"🎯 Iniciando análise de sites...")
print(f"⚠️  Usando delays de 5 segundos (muito conservador)")

print(f"\n" + "="*30)
print(f"💼 SITES DE LICITAÇÕES/COMPRAS")
print(f"="*30)

for site in sites_licitacoes[:2]:  # Só 2 para teste
    analisar_site_detalhado(site, "Licitações")

print(f"\n" + "="*30)
print(f"💹 SITES ECONÔMICOS")
print(f"="*30)

for site in sites_economicos[:2]:  # Só 2 para teste
    analisar_site_detalhado(site, "Econômicos")

print(f"\n🎉 Análise concluída!")
print(f"\n💡 PRÓXIMAS AÇÕES:")
print(f"   1. Foque nos sites que mostram ✅ PERMITIDO")
print(f"   2. Respeite os crawl-delays encontrados")
print(f"   3. Teste URLs específicas dos sites permitidos")
print(f"   4. Configure monitoramento automático apenas para sites permitidos")
print(f"\n⚖️  LEMBRE: Sempre verifique os termos de uso além do robots.txt!")