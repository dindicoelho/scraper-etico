# 🤖 ScraperÉtico

Uma biblioteca Python completa para **web scraping ético** que respeita automaticamente robots.txt, implementa rate limiting e fornece análise avançada - **perfeita para monitoramento de preços públicos**.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)

## 🚀 Começando em 5 Minutos

### 1. Clone e Instale
```bash
git clone https://github.com/SEU-USUARIO/scraper-etico.git
cd scraper-etico
pip install -r requirements.txt
```

### 2. Configure suas credenciais
```bash
cp config_producao.example.py config_producao.py
nano config_producao.py  # Edite com seus dados reais
```

### 3. Teste básico
```bash
python3 example_usage.py
```

### 4. Execute scraping em produção
```bash
python3 rodar_producao.py
```

**Pronto! 🎉** Seus dados vão aparecer em `dados_producao/`

## 💡 Por que usar o ScraperÉtico?

### ✅ **O que esta biblioteca faz POR VOCÊ:**
- 🛡️ **Verifica robots.txt automaticamente** - Nunca vai quebrar regras
- ⏱️ **Rate limiting inteligente** - Nunca vai sobrecarregar servidores
- 📊 **Export automático** para CSV e JSON - Dados prontos para análise
- 🔄 **Processamento paralelo** - Processa centenas de sites rapidamente
- 📝 **Logs completos** - Auditoria total do que aconteceu
- 🚨 **Error handling robusto** - Continua funcionando mesmo com problemas

### ❌ **O que você NÃO precisa se preocupar:**
- ❌ Criar verificação de robots.txt manual
- ❌ Implementar delays entre requests
- ❌ Tratar erros de rede e timeouts
- ❌ Converter dados para CSV/JSON
- ❌ Gerenciar logs e auditoria
- ❌ Configurar processamento paralelo

## 📋 Casos de Uso Reais

### 🏛️ **Monitoramento de Licitações**
```python
sites_licitacoes = [
    "https://portal.compras.gov.br",
    "https://www.gov.br/compras/pt-br",
    "https://transparencia.gov.br"
]
# Resultado: CSV com status de cada site, dados extraídos, timestamps
```

### 💰 **Análise de Preços Governamentais**
```python
sites_precos = [
    "https://www.bcb.gov.br/controleinflacao",
    "https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos",
    "https://www.ipea.gov.br/portal/"
]
# Resultado: JSON com dados estruturados, métricas, relatórios
```

## 📖 Guia Completo de Uso

### 🔰 **Nível 1: Uso Básico (1 site)**
```python
from src.scraper_etico import ScraperEtico

# Configurar com SEUS dados
scraper = ScraperEtico(
    user_agent="MeuProjeto/1.0 (+https://meusite.com; contato@email.com)",
    default_delay=3.0  # 3 segundos entre requests
)

# Verificar se pode acessar
if scraper.can_fetch("https://example.com"):
    response = scraper.get("https://example.com")
    print(f"Sucesso! Dados: {len(response.text)} caracteres")
else:
    print("Site bloqueou o acesso")
```

### 📊 **Nível 2: Processamento em Lote (múltiplos sites)**
```python
from src.batch_processor import BatchProcessor

# Lista de sites para monitorar
urls = [
    "https://portal.compras.gov.br",
    "https://transparencia.gov.br",
    "https://www.gov.br/economia"
]

# Processar todos de uma vez
processor = BatchProcessor()
processor.scraper = ScraperEtico(
    user_agent="MeuBot/1.0 (+https://meusite.com; eu@email.com)",
    default_delay=5.0  # Respeitoso para sites gov
)

# Executar (vai demorar uns minutos)
job_state = processor.process_batch(
    urls,
    max_workers=2,      # 2 sites em paralelo
    show_progress=True  # Mostrar barra de progresso
)

# Export automático
processor.export_to_csv(job_state, "meus_resultados.csv")
processor.export_to_json(job_state, "meus_resultados.json")

print(f"✅ Processados: {job_state.processed_count} sites")
print(f"📊 Sucessos: {len(job_state.completed_urls)}")
```

### 🚀 **Nível 3: Produção Automatizada (rodar todo dia)**

**1. Configure uma vez:**
```bash
# Editar configurações
nano config_producao.py

# Adicionar seus sites
SITES_PRODUCAO = [
    "https://portal.compras.gov.br",
    "https://transparencia.gov.br",
    # Seus sites aqui...
]

# Configurar seu user-agent
USER_AGENT = "MeuProjeto/1.0 (+https://meusite.com; eu@email.com)"
```

**2. Execute diariamente:**
```bash
python3 rodar_producao.py
```

**3. Veja os resultados:**
```bash
# Arquivos gerados automaticamente
ls dados_producao/
# monitoramento_20241204_143022.csv
# monitoramento_20241204_143022.json

# Abrir CSV no Excel
open dados_producao/monitoramento_*.csv

# Análise automática
python3 analisar_resultados.py
```

## 📁 **O que você recebe (Arquivos Gerados)**

### 📄 **Arquivo CSV** (Excel/Google Sheets)
```csv
url,domain,success,robots_allowed,status_code,response_size,timestamp
https://portal.compras.gov.br,portal.compras.gov.br,True,True,200,45621,2024-01-15T14:30:22
https://site-bloqueado.com,site-bloqueado.com,False,False,403,0,2024-01-15T14:30:27
```

### 📊 **Arquivo JSON** (Análise programática)
```json
{
  "job_metadata": {
    "total_urls": 10,
    "success_count": 8,
    "completion_percentage": 80.0,
    "duration": "00:03:45"
  },
  "results": [
    {
      "url": "https://portal.compras.gov.br",
      "success": true,
      "status_code": 200,
      "response_size": 45621,
      "response_time": 2.3,
      "robots_allowed": true,
      "timestamp": "2024-01-15T14:30:22"
    }
  ]
}
```

### 📋 **Logs Detalhados** (`logs/producao_YYYYMMDD.log`)
```
2024-01-15 14:30:15 - ScraperEtico - INFO - Checking robots.txt for https://portal.compras.gov.br
2024-01-15 14:30:16 - ScraperEtico - INFO - Access allowed, applying 5.0s delay
2024-01-15 14:30:22 - ScraperEtico - INFO - Request successful: 200 OK (45621 bytes)
```

## ⚙️ **Configuração Detalhada**

### 🤖 **User-Agent (OBRIGATÓRIO configurar)**
```python
# ❌ ERRADO - Genérico demais
USER_AGENT = "MeuBot/1.0"

# ✅ CORRETO - Identificação completa
USER_AGENT = "MonitorPrecos/1.0 (+https://github.com/usuario/projeto; contato@email.com)"
USER_AGENT = "PesquisaAcademica/1.0 (+https://universidade.br/projeto; prof@univ.br)"
USER_AGENT = "AnaliseMercado/1.0 (+https://empresa.com/sobre-bot; dev@empresa.com)"
```

### ⏱️ **Delays Recomendados**
```python
# Sites governamentais (seja muito respeitoso)
DEFAULT_DELAY = 5.0  # 5 segundos

# Sites comerciais
DEFAULT_DELAY = 2.0  # 2 segundos

# Sites pessoais/blogs
DEFAULT_DELAY = 1.0  # 1 segundo
```

### 🧵 **Workers (Paralelização)**
```python
# Sites governamentais
MAX_WORKERS = 1  # Um de cada vez

# Sites comerciais
MAX_WORKERS = 2  # Até 2 paralelos

# Sites robustos (Google, GitHub, etc)
MAX_WORKERS = 3  # Até 3 paralelos
```

## 🧪 **Testando Antes de Usar**

### **1. Teste seus sites específicos**
```bash
# Editar lista de sites
nano teste_meus_sites.py

# Executar teste
python3 teste_meus_sites.py
```

### **2. Teste completo de produção**
```bash
python3 teste_producao.py
```

### **3. Tutorial interativo**
```bash
jupyter notebook notebooks/tutorial_scraper_etico.ipynb
```

## 📊 **Análise dos Resultados**

### **Análise automática**
```bash
python3 analisar_resultados.py
# Escolha opção 1: Analisar dados_producao/
```

**Resultado:**
```
📊 RELATÓRIO COMPLETO DE SCRAPING
================================
📁 Pasta analisada: dados_producao
📄 Arquivos CSV: 5
✅ URLs com sucesso: 85 (78.7%)
❌ URLs com falha: 23 (21.3%)
🌐 TOP 5 DOMÍNIOS:
   portal.compras.gov.br: 15 URLs
   transparencia.gov.br: 12 URLs
   ...
```

### **Excel/Google Sheets**
```bash
# Abrir último arquivo
open dados_producao/monitoramento_*.csv

# Copiar para área de trabalho
cp dados_producao/monitoramento_*.csv ~/Desktop/
```

## 🛡️ **Princípios Éticos (Muito Importante!)**

### ✅ **Esta biblioteca SEMPRE faz:**
- Verifica robots.txt antes de QUALQUER request
- Aplica delays apropriados entre requests
- Identifica claramente o bot com user-agent descritivo
- Respeita crawl-delay especificado pelos sites
- Para imediatamente se receber erro 429 (Too Many Requests)
- Gera logs completos para auditoria

### ❌ **Esta biblioteca NUNCA faz:**
- Ignora robots.txt
- Faz requests simultâneos excessivos
- Usa user-agents falsos de navegadores
- Esconde a identidade do bot
- Continua tentando após ser bloqueada

### 🚨 **Responsabilidades do Usuário:**
- ✅ Configure user-agent com SEUS dados reais
- ✅ Use delays adequados (mínimo 1s, recomendado 3-5s)
- ✅ Monitore logs regularmente
- ✅ Respeite termos de uso dos sites
- ✅ Tenha um propósito legítimo para o scraping

## 🔧 **API Referência Rápida**

### **ScraperEtico**
```python
scraper = ScraperEtico(
    user_agent="Obrigatório: MeuBot/1.0 (+site; email)",
    default_delay=3.0,      # Segundos entre requests
    timeout=30.0            # Timeout por request
)

# Métodos principais
scraper.can_fetch(url)      # bool: pode acessar?
scraper.get(url)           # requests.Response ou None
scraper.get_crawl_delay(url) # float: delay específico do site
```

### **BatchProcessor**
```python
processor = BatchProcessor()
processor.scraper = ScraperEtico(...)

job_state = processor.process_batch(
    urls,                   # Lista de URLs
    max_workers=2,          # Threads paralelas
    show_progress=True      # Barra de progresso
)

# Export
processor.export_to_csv(job_state, "resultado.csv")
processor.export_to_json(job_state, "resultado.json")
```

## 🐛 **Troubleshooting**

### **"ModuleNotFoundError: No module named 'src'"**
```bash
# Certifique-se de estar na pasta correta
cd scraper_etico
python3 -c "import sys; print(sys.path[0])"  # Deve mostrar a pasta atual
```

### **"Access disallowed by robots.txt"**
```
✅ Comportamento normal! O site não permite bots.
❌ NÃO tente contornar - respeite a decisão do site
💡 Considere usar API oficial se disponível
```

### **"Too many requests (429)"**
```
✅ Biblioteca para automaticamente
💡 Aumente DEFAULT_DELAY para 5-10 segundos
💡 Reduza MAX_WORKERS para 1
```

### **Arquivos CSV não abrem no Excel**
```bash
# Converta encoding se necessário
iconv -f UTF-8 -t ISO-8859-1 dados_producao/arquivo.csv > arquivo_excel.csv
```

## 📦 **Dependências**

### **Obrigatórias** (já no requirements.txt)
- `requests >= 2.28.0` - HTTP requests
- Python 3.8+ (built-in urllib para robots.txt)

### **Opcionais** (para recursos avançados)
```bash
# Para tutorial Jupyter
pip install jupyter pandas matplotlib

# Para testes
pip install pytest pytest-cov

# Para barras de progresso
pip install tqdm
```

## 🎯 **Casos de Uso Específicos**

### **Monitoramento Diário de Licitações**
```python
# config_producao.py
SITES_PRODUCAO = [
    "https://portal.compras.gov.br",
    "https://www.licitacoes-e.com.br", 
    "https://transparencia.gov.br"
]
DEFAULT_DELAY = 10.0  # Muito respeitoso
MAX_WORKERS = 1       # Um de cada vez
```

### **Pesquisa Acadêmica**
```python
USER_AGENT = "PesquisaTCC/1.0 (+https://universidade.br/projeto-tcc; aluno@univ.br)"
DEFAULT_DELAY = 3.0
# Documente tudo para orientador
```

### **Análise de Mercado**
```python
USER_AGENT = "EstudoMercado/1.0 (+https://empresa.com/pesquisa; pesquisa@empresa.com)"
# Foque em sites que permitem scraping
# Considere APIs oficiais quando possível
```

## 🚀 **Rotina de Produção Recomendada**

### **Setup inicial (uma vez só):**
```bash
git clone [repositório]
cd scraper_etico
pip install -r requirements.txt
cp config_producao.example.py config_producao.py
nano config_producao.py  # Configurar
python3 teste_meus_sites.py  # Testar
```

### **Execução diária:**
```bash
# 8h da manhã
python3 rodar_producao.py

# 9h da manhã - análise
python3 analisar_resultados.py
open dados_producao/monitoramento_*.csv
```

### **Manutenção semanal:**
```bash
# Backup
cp -r dados_producao/ backup_$(date +%Y%m%d)/

# Limpeza de logs antigos
find logs/ -name "*.log" -mtime +7 -delete

# Verificar espaço em disco
df -h
```

## 📄 **Licença**

MIT License - Use livremente, mas mantenha os créditos.

## 🆘 **Suporte**

- 📖 **Documentação**: Este README + notebook tutorial
- 🐛 **Bugs**: Abra issue no GitHub
- 💬 **Dúvidas**: GitHub Discussions
- 📧 **Contato**: Issues do GitHub

## ⚠️ **Disclaimer Legal**

Esta ferramenta é para **uso ético e educacional**. Usuários são responsáveis por:
- ✅ Respeitar robots.txt e termos de uso
- ✅ Verificar legalidade do scraping em sua jurisdição
- ✅ Não sobrecarregar servidores
- ✅ Ter propósito legítimo para coleta de dados

---

## 🌟 **Scraping Ético é Scraping Responsável** 

*"Com grandes poderes vêm grandes responsabilidades"* 

**Made with ❤️ for ethical web scraping**