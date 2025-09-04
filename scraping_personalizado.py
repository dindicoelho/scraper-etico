#!/usr/bin/env python3
"""
SCRAPING PERSONALIZADO - Para quando você quer controle total!
"""

from datetime import datetime
from pathlib import Path
from src.scraper_etico import ScraperEtico
from src.batch_processor import BatchProcessor

def scraping_personalizado(sites, nome_projeto="MeuScraping"):
    """
    Função para scraping personalizado com export automático
    
    Args:
        sites: Lista de URLs para scraping
        nome_projeto: Nome para identificar os arquivos
    """
    
    print(f"🚀 SCRAPING PERSONALIZADO: {nome_projeto}")
    print("=" * 50)
    print(f"🔗 Sites para processar: {len(sites)}")
    
    # 1. Configurar scraper
    scraper = ScraperEtico(
        user_agent="MonitorPrecosPublicos/1.0 (+https://seusite.com; seuemail@exemplo.com)",
        default_delay=3.0,  # 3 segundos entre requests
        timeout=30.0
    )
    
    # 2. Configurar batch processor
    processor = BatchProcessor()
    processor.scraper = scraper
    
    # 3. Executar scraping
    print("\n🔄 Iniciando scraping...")
    job_state = processor.process_batch(
        sites,
        max_workers=2,          # 2 threads paralelas
        analyze_robots=True,    # Analisar robots.txt completo
        show_progress=True      # Mostrar barra de progresso
    )
    
    # 4. Mostrar resultados
    print(f"\n📊 RESULTADOS:")
    print(f"   Total processado: {job_state.processed_count}")
    print(f"   Sucessos: {len(job_state.completed_urls)}")
    print(f"   Falhas: {len(job_state.failed_urls)}")
    print(f"   Taxa de sucesso: {job_state.completion_percentage:.1f}%")
    
    # 5. Export automático
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Criar pasta de resultados
    output_dir = Path("./resultados_personalizados")
    output_dir.mkdir(exist_ok=True)
    
    # Export CSV
    csv_file = output_dir / f"{nome_projeto}_{timestamp}.csv"
    processor.export_to_csv(job_state, csv_file)
    print(f"📄 CSV salvo: {csv_file}")
    
    # Export JSON
    json_file = output_dir / f"{nome_projeto}_{timestamp}.json"
    processor.export_to_json(job_state, json_file)
    print(f"📄 JSON salvo: {json_file}")
    
    # 6. Relatório resumido
    processor.print_summary_report(job_state)
    
    return job_state, csv_file, json_file

# EXEMPLOS DE USO:

if __name__ == "__main__":
    print("🎯 EXEMPLOS DE SCRAPING PERSONALIZADO")
    print("=" * 50)
    
    # Exemplo 1: Sites governamentais
    print("\n📋 EXEMPLO 1: Sites governamentais")
    sites_gov = [
        "https://www.gov.br/compras/pt-br",
        "https://portal.tcu.gov.br",
        "https://www.bcb.gov.br"
    ]
    
    resposta = input("Executar exemplo 1? (s/N): ").lower()
    if resposta == 's':
        scraping_personalizado(sites_gov, "SitesGovernamentais")
    
    # Exemplo 2: Sites específicos do usuário
    print("\n📋 EXEMPLO 2: Seus sites personalizados")
    print("Edite a lista abaixo com seus sites:")
    
    meus_sites = [
        # ADICIONE SEUS SITES AQUI:
        # "https://site1.com",
        # "https://site2.com", 
    ]
    
    if meus_sites:
        resposta = input("Executar scraping dos seus sites? (s/N): ").lower()
        if resposta == 's':
            scraping_personalizado(meus_sites, "MeusProjetos")
    else:
        print("⚠️ Nenhum site configurado. Edite a lista 'meus_sites' acima.")
    
    print("\n✅ Scraping personalizado concluído!")
    print("📁 Arquivos salvos em: ./resultados_personalizados/")