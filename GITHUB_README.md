# 🤖 ScraperÉtico

Uma biblioteca Python para **web scraping ético** que respeita automaticamente as regras do robots.txt, implementa rate limiting e fornece ferramentas avançadas de análise para **monitoramento de preços públicos**.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)

## 🎯 Características Principais

- ✅ **Verificação automática de robots.txt** antes de qualquer acesso
- ⏱️ **Rate limiting configurável** para respeitar os servidores  
- 🤖 **User-agent customizável** para identificação adequada
- 📊 **Análise avançada** de arquivos robots.txt (crawl-delay, sitemaps, regras)
- 🔄 **Processamento em lote** com suporte a paralelização
- 📈 **Exportação de relatórios** em CSV e JSON
- 🚨 **Error handling robusto** para falhas de rede
- 📝 **Logs detalhados** com timestamps para auditoria
- 💾 **Cache inteligente** para evitar downloads desnecessários

## 🚀 Instalação Rápida

```bash
# Clone o repositório
git clone https://github.com/SEU-USUARIO/scraper-etico.git
cd scraper-etico

# Instale as dependências
pip install -r requirements.txt

# Configure suas credenciais
cp config_producao.example.py config_producao.py
nano config_producao.py  # Edite com seus dados

# Teste a instalação
python3 example_usage.py
```

## 📖 Uso Básico

### Verificação Simples de URL

```python
from src.scraper_etico import ScraperEtico

# Criar instância do scraper
scraper = ScraperEtico(
    user_agent="MeuBot/1.0 (+http://meusite.com/contato)",
    default_delay=2.0
)

# Verificar se uma URL pode ser acessada
pode_acessar = scraper.can_fetch("https://example.com/pagina")
print(f"Pode acessar: {pode_acessar}")

# Fazer request com rate limiting automático  
response = scraper.get("https://example.com/pagina")
if response:
    print(f"Conteúdo obtido: {len(response.text)} caracteres")
```

### Processamento em Lote com Export

```python
from src.batch_processor import BatchProcessor

# URLs para verificar
urls = [
    "https://portal.compras.gov.br",
    "https://transparencia.gov.br",
    "https://www.gov.br/economia"
]

# Processar em lote
processor = BatchProcessor()
processor.scraper = ScraperEtico(
    user_agent="MeuBot/1.0",
    default_delay=5.0  # Respeitoso para sites gov
)

job_state = processor.process_batch(urls, max_workers=2)

# Export automático para CSV e JSON
processor.export_to_csv(job_state, "resultados.csv")
processor.export_to_json(job_state, "resultados.json")
```

## 🎓 Tutorial Completo

Execute o notebook tutorial interativo:

```bash
cd notebooks/
jupyter notebook tutorial_scraper_etico.ipynb
```

## 🏗️ Arquitetura

```
scraper_etico/
├── src/                          # Código fonte principal
│   ├── scraper_etico.py         # Classe principal de scraping
│   ├── analyzer.py              # Análise avançada de robots.txt
│   ├── batch_processor.py       # Processamento em lote
│   └── utils.py                 # Funções utilitárias
├── tests/                       # Testes unitários
├── notebooks/                   # Tutoriais Jupyter
├── config_producao.example.py   # Exemplo de configuração
└── requirements.txt            # Dependências
```

## ⚙️ Configuração de Produção

1. **Copie o arquivo de exemplo:**
   ```bash
   cp config_producao.example.py config_producao.py
   ```

2. **Edite suas configurações:**
   ```python
   # Identifique seu bot adequadamente
   USER_AGENT = "MeuProjeto/1.0 (+https://meusite.com; contato@meusite.com)"
   
   # Configure delays respeitosos
   DEFAULT_DELAY = 5.0  # Sites governamentais
   
   # Adicione seus sites
   SITES_PRODUCAO = [
       "https://portal.compras.gov.br",
       "https://transparencia.gov.br",
       # Seus sites...
   ]
   ```

3. **Execute produção:**
   ```bash
   python3 rodar_producao.py
   ```

## 🧪 Testes

```bash
# Executar todos os testes
python3 tests/run_tests.py

# Teste de produção completo
python3 teste_producao.py

# Testar seus sites específicos
python3 teste_meus_sites.py
```

## 📊 Análise de Dados

```bash
# Analisar resultados automaticamente
python3 analisar_resultados.py

# Ver dados no Excel/Sheets
open dados_producao/monitoramento_*.csv
```

## 🛡️ Princípios Éticos

Esta biblioteca segue rigorosamente as **melhores práticas de web scraping ético**:

### ✅ Sempre Faça:
- Verificar robots.txt antes de qualquer acesso
- Usar delays adequados entre requests (mínimo 1s para sites gov: 5s+)
- Identificar seu bot com user-agent descritivo
- Incluir informações de contato no user-agent
- Monitorar logs para detectar problemas
- Respeitar rate limits e crawl-delays especificados

### ❌ Nunca Faça:
- Ignorar regras do robots.txt
- Fazer requests simultâneos excessivos
- Usar user-agents falsos de navegadores
- Fazer scraping 24/7 sem pausas
- Ignorar erros HTTP ou de rede

## 📝 Casos de Uso

- 🏛️ **Monitoramento de Licitações Públicas**
- 💰 **Análise de Preços Governamentais** 
- 📊 **Pesquisa Acadêmica** sobre dados públicos
- 🔍 **Auditoria de Transparência** governamental
- 📈 **Análise de Mercado Público**

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## ⚠️ Disclaimer

Esta ferramenta foi desenvolvida para **uso ético e educacional**. Os usuários são responsáveis por:
- Respeitar os termos de uso dos sites
- Verificar a legalidade do scraping em sua jurisdição
- Não sobrecarregar servidores
- Usar apenas para fins legítimos

## 🆘 Suporte

- 📖 **Documentação**: Veja notebooks/ e README.md
- 🐛 **Issues**: Abra uma issue no GitHub  
- 💬 **Discussões**: Use GitHub Discussions
- 📧 **Contato**: [Abrir Issue](https://github.com/SEU-USUARIO/scraper-etico/issues)

---

## 🌟 **Scraping Ético é Scraping Responsável** 🌟

*"Com grandes poderes vêm grandes responsabilidades"* - Use esta biblioteca para construir uma internet mais respeitosa e colaborativa.

**Made with ❤️ for ethical web scraping**