from src.batch_processor import BatchProcessor
import pandas as pd

print("📦 Processamento em LOTE de sites reais...")

# Lista de sites para monitoramento de preços/dados
sites_monitoramento = [
    "https://www.gov.br/economia",
    "https://www.bcb.gov.br/estatisticas", 
    "https://www.ibge.gov.br/estatisticas",
    "https://www.bndes.gov.br",
    "https://www.cvm.gov.br",
    "https://www.bb.com.br",
    "https://www.caixa.gov.br",
    "https://www.petrobras.com.br",
    "https://www.vale.com",
    "https://ri.magazine.luiza.com.br",  # Investor Relations - geralmente permite
]

# Configurar processador
processor = BatchProcessor(
    user_agent="MonitorPrecos/1.0 (+https://meusite.com/sobre; contato@meusite.com)",
    max_workers=2,  # Só 2 threads para ser respeitoso
    default_delay=4.0,  # 4 segundos entre requests
    timeout=15.0
)

def callback_progresso(url, resultado):
    status = "✅ PERMITIDO" if resultado.allowed else "❌ BLOQUEADO"
    print(f"   {status}: {url}")

print("🚀 Iniciando processamento...")
print("⏱️  Isso vai demorar uns 2-3 minutos (delays de 4s)")

# Processar em lote
resultados, stats = processor.processar_lote(
    sites_monitoramento,
    paralelo=True,
    callback_progresso=callback_progresso
)

# Mostrar estatísticas
print(f"\n📊 RESULTADOS:")
print(f"   🔗 Total processado: {stats.total_urls}")
print(f"   ✅ Permitidos: {stats.allowed}")
print(f"   ❌ Bloqueados: {stats.blocked}")
print(f"   💥 Erros: {stats.failed}")
print(f"   📄 Com robots.txt: {stats.robots_found}")

# Salvar relatórios
print(f"\n💾 Salvando relatórios...")

# CSV detalhado
processor.exportar_csv(resultados, "relatorio_sites_reais.csv")
print("   📄 Salvo: relatorio_sites_reais.csv")

# JSON para análise
processor.exportar_json(resultados, "relatorio_sites_reais.json")
print("   📄 Salvo: relatorio_sites_reais.json")

# Mostrar sites permitidos
sites_permitidos = [url for url, res in resultados.items() if res.allowed]
if sites_permitidos:
    print(f"\n🎯 SITES PERMITIDOS PARA SCRAPING:")
    for site in sites_permitidos[:5]:  # Mostrar só os primeiros 5
        delay = resultados[site].crawl_delay
        delay_info = f" (delay: {delay}s)" if delay else ""
        print(f"   ✅ {site}{delay_info}")

print(f"\n💡 PRÓXIMOS PASSOS:")
print(f"   1. Abra relatorio_sites_reais.csv no Excel/Numbers")
print(f"   2. Foque nos sites com 'allowed': True")
print(f"   3. Respeite os crawl-delays especificados")
print(f"   4. Teste páginas específicas dos sites permitidos")