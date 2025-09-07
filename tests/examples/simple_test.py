from src.scraper_etico import ScraperEtico

print("🤖 Testando ScraperÉtico...")

scraper = ScraperEtico(
    user_agent="TestBot/1.0 (teste@email.com)",
    default_delay=2.0
)

sites = [
    "https://httpbin.org",
    "https://example.com"
]

for site in sites:
    print(f"\n🔍 Testando: {site}")
    pode = scraper.can_fetch(site)
    print(f"   {'✅ PERMITIDO' if pode else '❌ BLOQUEADO'}")
    
    if pode:
        response = scraper.get(site)
        if response:
            print(f"   📄 Sucesso! {len(response.text)} caracteres")
        else:
            print("   ⚠️  Erro no request")

print("\n🎉 Teste concluído!")