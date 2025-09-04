#!/usr/bin/env python3
"""
EXEMPLO DE CONFIGURAÇÕES DE PRODUÇÃO - ScraperÉtico

INSTRUÇÕES:
1. Copie este arquivo para: config_producao.py
2. Edite as configurações com seus dados reais
3. NUNCA commite o config_producao.py no git!

Comando: cp config_producao.example.py config_producao.py
"""

# 🤖 IDENTIFICAÇÃO DO SEU BOT (MUDE ISSO!)
USER_AGENT = "MeuBot/1.0 (+https://meusite.com; contato@meusite.com)"
# ⚠️ IMPORTANTE: Substitua por SEU site e SEU email reais!
# Exemplos válidos:
# "MonitorPrecos/1.0 (+https://github.com/usuario/repo; usuario@email.com)"
# "PesquisaAcademica/1.0 (+https://universidade.edu.br/projeto; prof@univ.edu.br)"

# ⏱️ CONFIGURAÇÕES DE TIMING (Para sites governamentais - seja respeitoso!)
DEFAULT_DELAY = 5.0      # 5 segundos entre requests (conservador)
TIMEOUT = 30.0           # 30 segundos para timeout
MAX_WORKERS = 2          # Máximo 2 threads (conservador)

# 📅 HORÁRIOS PERMITIDOS (Evite sobrecarregar à noite)
HORARIO_INICIO = 8       # 8h da manhã
HORARIO_FIM = 18         # 18h da tarde

# 📝 CONFIGURAÇÕES DE LOG
LOG_LEVEL = "INFO"       # INFO, DEBUG, WARNING, ERROR
LOG_FILE = "producao.log"

# 🚨 CONFIGURAÇÕES DE SEGURANÇA
MAX_SITES_POR_DIA = 100  # Limite diário de sites
MAX_REQUESTS_POR_HORA = 200  # Limite por hora
PAUSE_ENTRE_LOTES = 300  # 5 minutos entre lotes

# 📊 SITES PARA MONITORAR (EDITE AQUI!)
SITES_PRODUCAO = [
    # Exemplos de sites governamentais brasileiros:
    # "https://portal.compras.gov.br",
    # "https://www.gov.br/economia", 
    # "https://transparencia.gov.br",
    # "https://www.bcb.gov.br/controleinflacao",
    # "https://www.ibge.gov.br/estatisticas",
    
    # ADICIONE SEUS SITES AQUI:
    # "https://site1.com",
    # "https://site2.gov.br",
    
    # Sites de exemplo (REMOVER em produção):
    "https://example.com",
]

# 📁 DIRETÓRIOS
OUTPUT_DIR = "./dados_producao"
BACKUP_DIR = "./backup_dados"  
LOG_DIR = "./logs"

# Validações básicas
if __name__ == "__main__":
    print("📋 CONFIGURAÇÕES DE EXEMPLO CARREGADAS")
    print(f"🤖 User-agent: {USER_AGENT}")
    print(f"⏱️  Delay: {DEFAULT_DELAY}s")
    print(f"🔗 Sites configurados: {len(SITES_PRODUCAO)}")
    print(f"⚠️  LEMBRE-SE: Copie para config_producao.py e edite!")
    
    # Avisos
    if "meusite.com" in USER_AGENT:
        print("❌ AVISO: USER_AGENT ainda é exemplo - edite com seus dados!")
    
    if "example.com" in str(SITES_PRODUCAO):
        print("❌ AVISO: SITES_PRODUCAO ainda tem exemplos - edite com sites reais!")
        
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. cp config_producao.example.py config_producao.py")
    print("2. nano config_producao.py  # Editar configurações")
    print("3. python3 rodar_producao.py  # Executar")