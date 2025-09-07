# 🤖 EthicalScraper

A Python library for **ethical web scraping** that automatically respects robots.txt rules, implements rate limiting, and provides advanced analysis tools for **public price monitoring**.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Production%20Ready-brightgreen.svg)

## 🎯 Key Features

- ✅ **Automatic robots.txt verification** before any access
- ⏱️ **Configurable rate limiting** to respect servers  
- 🤖 **Customizable user-agent** for proper identification
- 📊 **Advanced analysis** of robots.txt files (crawl-delay, sitemaps, rules)
- 🔄 **Batch processing** with parallelization support
- 📈 **Report export** in CSV and JSON formats
- 🚨 **Robust error handling** for network failures
- 📝 **Detailed logs** with timestamps for auditing
- 💾 **Smart caching** to avoid unnecessary downloads

## 🚀 Quick Installation

```bash
# Clone the repository
git clone https://github.com/dindicoelho/scraper-etico.git
cd scraper-etico

# Install dependencies
pip install -r requirements.txt

# Configure your credentials
cp production_config.example.py production_config.py
nano production_config.py  # Edit with your data

# Test installation
python3 example_usage.py
```

## 📖 Basic Usage

### Simple URL Verification

```python
from src.scraper_etico import ScraperEtico

# Create scraper instance
scraper = ScraperEtico(
    user_agent="MyBot/1.0 (+http://mysite.com/contact)",
    default_delay=2.0
)

# Check if a URL can be accessed
can_access = scraper.can_fetch("https://example.com/page")
print(f"Can access: {can_access}")

# Make request with automatic rate limiting  
response = scraper.get("https://example.com/page")
if response:
    print(f"Content retrieved: {len(response.text)} characters")
```

### Batch Processing with Export

```python
from src.batch_processor import BatchProcessor

# URLs to verify
urls = [
    "https://portal.compras.gov.br",
    "https://transparencia.gov.br",
    "https://www.gov.br/economia"
]

# Process in batch
processor = BatchProcessor()
processor.scraper = ScraperEtico(
    user_agent="MyBot/1.0",
    default_delay=5.0  # Respectful for gov sites
)

job_state = processor.process_batch(urls, max_workers=2)

# Automatic export to CSV and JSON
processor.export_to_csv(job_state, "results.csv")
processor.export_to_json(job_state, "results.json")
```

## 🎓 Complete Tutorial

Run the interactive tutorial notebook:

```bash
cd notebooks/
jupyter notebook tutorial_scraper_etico.ipynb
```

## 🏗️ System Architecture

### Directory Structure
```
ethical_scraper/
├── src/                          # Main source code
│   ├── scraper_etico.py         # Main scraping class
│   ├── analyzer.py              # Advanced robots.txt analysis
│   ├── batch_processor.py       # Concurrent batch processing
│   └── utils.py                 # Utility functions
├── tests/                       # Automated tests
├── notebooks/                   # Interactive tutorials
├── production_data/             # Execution results
├── data_backup/                 # Automatic backup
├── logs/                        # Execution logs
├── batch_states/               # Job states for resumption
├── production_config.example.py # Configuration example
└── requirements.txt            # Dependencies
```

### Main Components

#### 1. **ScraperEtico** (`src/scraper_etico.py`)
**Responsibility**: Individual ethical scraping with automatic compliance

**Features**:
- ✅ Automatic robots.txt verification
- ⏱️ Intelligent rate limiting per domain  
- 🔄 robots.txt caching for performance
- 📝 Detailed logging with timestamps
- 🛡️ Robust network error handling
- 🕐 Automatic crawl-delay detection

**Execution flow**:
```
URL Input → Robots.txt Check → Rate Limiting → HTTP Request → Response
```

#### 2. **RobotsAnalyzer** (`src/analyzer.py`) 
**Responsibility**: Advanced and detailed robots.txt file analysis

**Features**:
- 🔍 Complete robots.txt parsing with validation
- 📊 Detailed statistics per user-agent
- 🗺️ Sitemap extraction and validation
- ⚖️ Comparison between different user-agents
- 📈 Restrictiveness and pattern analysis
- 📋 Formatted report generation

**Use cases**:
- robots.txt policy auditing
- Scraping strategy planning
- robots.txt change monitoring

#### 3. **BatchProcessor** (`src/batch_processor.py`)
**Responsibility**: Concurrent and efficient processing of multiple URLs

**Features**:
- 🔄 Concurrent processing with ThreadPoolExecutor
- 💾 Persistent state for interrupted job resumption
- 📊 Real-time progress bar (tqdm)
- 📤 Automatic export to CSV and JSON
- 📈 Detailed statistical reports  
- 🛡️ Coordinated rate limiting between threads
- 🔍 Integration with robots.txt analysis

**Threading architecture**:
```
BatchProcessor → ThreadPoolExecutor → [Worker1, Worker2, Worker3...] → Domain Locks → ScraperEtico
```

### Rate Limiting System

The system implements multiple layers of thread-safe rate limiting:

```
1. Global Rate Limiting (ScraperEtico)
   ↓
2. Domain-specific Rate Limiting (BatchProcessor)  
   ↓
3. Robots.txt Crawl-Delay Compliance
   ↓
4. Thread-safe Domain Locks
```

### Complete Data Flow

```
URL List → BatchProcessor → JobState
     ↓
ThreadPoolExecutor → Worker Threads
     ↓
Domain Rate Limiting → ScraperEtico
     ↓
Robots.txt Check → HTTP Request → Response
     ↓
RobotsAnalyzer → BatchResult
     ↓
Persistent State → Exports (CSV/JSON) → Reports
```

### Persistence and Resumption

The system maintains persistent state using `.pkl` files in `batch_states/`:
- **JobState**: Job metadata and progress
- **Completed URLs**: URLs already processed
- **Failed URLs**: URLs that failed
- **Results**: Detailed results for each URL

### Performance and Scalability

**Implemented optimizations**:
- 💾 Smart robots.txt caching
- 🔄 HTTP connection reuse with requests.Session
- 📊 Asynchronous processing with ThreadPool
- 🧵 Scalable thread pool (configurable)
- 💿 Persistent state for long jobs
- 🔐 Thread-safe domain locking

**Recommended limits**:
- Max workers: 5-10 (depending on target server)
- Default delay: 1-2 seconds (5s+ for gov sites)
- Timeout: 30 seconds
- Batch size: 100-1000 URLs

## ⚙️ Production Configuration

1. **Copy the example file:**
   ```bash
   cp production_config.example.py production_config.py
   ```

2. **Edit your settings:**
   ```python
   # Identify your bot properly
   USER_AGENT = "MyProject/1.0 (+https://mysite.com; contact@mysite.com)"
   
   # Configure respectful delays
   DEFAULT_DELAY = 5.0  # Government sites
   
   # Add your sites
   PRODUCTION_SITES = [
       "https://portal.compras.gov.br",
       "https://transparencia.gov.br",
       # Your sites...
   ]
   ```

3. **Execute production:**
   ```bash
   python3 run_production.py
   ```

## 🧪 Testing

```bash
# Run all tests
python3 tests/run_tests.py

# Complete production test
python3 tests/production_test.py

# Test your specific sites
python3 tests/examples/my_monitoring.py
```

## 📊 Data Analysis

```bash
# Automatically analyze results
python3 analyze_results.py

# View data in Excel/Sheets
open production_data/monitoring_*.csv
```

## 🛡️ Ethical Principles

This library strictly follows **web scraping ethical best practices**:

### ✅ Always Do:
- Check robots.txt before any access
- Use adequate delays between requests (minimum 1s, for gov sites: 5s+)
- Identify your bot with descriptive user-agent
- Include contact information in user-agent
- Monitor logs to detect problems
- Respect rate limits and specified crawl-delays

### ❌ Never Do:
- Ignore robots.txt rules
- Make excessive simultaneous requests
- Use fake browser user-agents
- Scrape 24/7 without breaks
- Ignore HTTP or network errors

## 📝 Use Cases

- 🏛️ **Public Bidding Monitoring**
- 💰 **Government Price Analysis** 
- 📊 **Academic Research** on public data
- 🔍 **Government Transparency Auditing**
- 📈 **Public Market Analysis**

## 🤝 Contributing

1. Fork the project
2. Create a branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## ⚠️ Disclaimer

This tool was developed for **ethical and educational use**. Users are responsible for:
- Respecting website terms of service
- Checking the legality of scraping in their jurisdiction
- Not overloading servers
- Using only for legitimate purposes

## 🆘 Support

- 📖 **Documentation**: See notebooks/ and README.md
- 🐛 **Issues**: Open an issue on GitHub  
- 💬 **Discussions**: Use GitHub Discussions
- 📧 **Contact**: [Open Issue](https://github.com/dindicoelho/scraper-etico/issues)

---

## 🌟 **Ethical Scraping is Responsible Scraping** 🌟

*"With great power comes great responsibility"* - Use this library to build a more respectful and collaborative internet.

**Made with ❤️ for ethical web scraping**