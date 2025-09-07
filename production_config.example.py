#!/usr/bin/env python3
"""
PRODUCTION CONFIGURATION EXAMPLE - EthicalScraper

INSTRUCTIONS:
1. Copy this file to: production_config.py
2. Edit the settings with your real data
3. NEVER commit production_config.py to git!

Command: cp production_config.example.py production_config.py
"""

# 🤖 BOT IDENTIFICATION (CHANGE THIS!)
USER_AGENT = "MyBot/1.0 (+https://mysite.com; contact@mysite.com)"
# ⚠️ IMPORTANT: Replace with YOUR website and YOUR real email!
# Valid examples:
# "PriceMonitor/1.0 (+https://github.com/user/repo; user@email.com)"
# "AcademicResearch/1.0 (+https://university.edu/project; prof@univ.edu)"

# ⏱️ TIMING CONFIGURATION (For government sites - be respectful!)
DEFAULT_DELAY = 5.0      # 5 seconds between requests (conservative)
TIMEOUT = 30.0           # 30 seconds for timeout
MAX_WORKERS = 2          # Maximum 2 threads (conservative)

# 📅 ALLOWED HOURS (Avoid overloading at night)
START_HOUR = 8           # 8 AM
END_HOUR = 18            # 6 PM

# 📝 LOG CONFIGURATION
LOG_LEVEL = "INFO"       # INFO, DEBUG, WARNING, ERROR
LOG_FILE = "production.log"

# 🚨 SECURITY CONFIGURATION
MAX_SITES_PER_DAY = 100        # Daily site limit
MAX_REQUESTS_PER_HOUR = 200    # Requests per hour limit
PAUSE_BETWEEN_BATCHES = 300    # 5 minutes between batches

# 📊 SITES TO MONITOR (EDIT HERE!)
PRODUCTION_SITES = [
    # Examples of Brazilian government sites:
    # "https://portal.compras.gov.br",
    # "https://www.gov.br/economia", 
    # "https://transparencia.gov.br",
    # "https://www.bcb.gov.br/controleinflacao",
    # "https://www.ibge.gov.br/estatisticas",
    
    # ADD YOUR SITES HERE:
    # "https://site1.com",
    # "https://site2.gov.br",
    
    # Example sites (REMOVE in production):
    "https://example.com",
]

# 📁 DIRECTORIES
OUTPUT_DIR = "./production_data"
BACKUP_DIR = "./data_backup"  
LOG_DIR = "./logs"

# Basic validations
if __name__ == "__main__":
    print("📋 EXAMPLE CONFIGURATION LOADED")
    print(f"🤖 User-agent: {USER_AGENT}")
    print(f"⏱️  Delay: {DEFAULT_DELAY}s")
    print(f"🔗 Sites configured: {len(PRODUCTION_SITES)}")
    print(f"⚠️  REMEMBER: Copy to production_config.py and edit!")
    
    # Warnings
    if "mysite.com" in USER_AGENT:
        print("❌ WARNING: USER_AGENT is still example - edit with your data!")
    
    if "example.com" in str(PRODUCTION_SITES):
        print("❌ WARNING: PRODUCTION_SITES still has examples - edit with real sites!")
        
    print("\n📋 NEXT STEPS:")
    print("1. cp production_config.example.py production_config.py")
    print("2. nano production_config.py  # Edit configuration")
    print("3. python3 run_production.py  # Execute")