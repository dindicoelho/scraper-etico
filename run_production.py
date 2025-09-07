#!/usr/bin/env python3
"""
MAIN PRODUCTION SCRIPT - EthicalScraper
Execute this script to run safely in production!
"""

import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import signal

# Import configuration
from production_config import *
from src.scraper_etico import ScraperEtico
from src.batch_processor import BatchProcessor

class ProductionMonitor:
    def __init__(self):
        self.setup_directories()
        self.setup_logging()
        self.setup_scraper()
        self.running = True
        self.setup_signal_handlers()
        
    def setup_directories(self):
        """Create necessary directories"""
        for dir_path in [OUTPUT_DIR, BACKUP_DIR, LOG_DIR]:
            Path(dir_path).mkdir(exist_ok=True, parents=True)
        print(f"📁 Directories created: {OUTPUT_DIR}, {BACKUP_DIR}, {LOG_DIR}")
    
    def setup_logging(self):
        """Setup detailed logging"""
        log_file = Path(LOG_DIR) / f"production_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("ProductionMonitor")
        self.logger.info("🚀 Monitoring system started")
        
    def setup_scraper(self):
        """Configure scraper for production"""
        self.scraper = ScraperEtico(
            user_agent=USER_AGENT,
            default_delay=DEFAULT_DELAY,
            timeout=TIMEOUT
        )
        
        self.batch_processor = BatchProcessor()
        self.batch_processor.scraper = self.scraper
        
        self.logger.info(f"⚙️ Scraper configured - Delay: {DEFAULT_DELAY}s, Timeout: {TIMEOUT}s")
    
    def setup_signal_handlers(self):
        """Setup kill switch"""
        def signal_handler(sig, frame):
            self.logger.info("🛑 KILL SWITCH ACTIVATED - Stopping execution...")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def check_time_window(self):
        """Check if within allowed time window"""
        current_hour = datetime.now().hour
        if START_HOUR <= current_hour <= END_HOUR:
            return True
        else:
            self.logger.warning(f"⏰ Outside allowed hours: {current_hour}h (allowed: {START_HOUR}h-{END_HOUR}h)")
            return False
    
    def execute_batch(self, sites):
        """Execute a batch of sites"""
        self.logger.info(f"🔄 Starting batch with {len(sites)} sites")
        
        # Process batch
        job_state = self.batch_processor.process_batch(
            sites,
            max_workers=MAX_WORKERS,
            show_progress=True
        )
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(OUTPUT_DIR) / f"monitoring_{timestamp}"
        
        self.batch_processor.export_to_csv(job_state, f"{output_file}.csv")
        self.batch_processor.export_to_json(job_state, f"{output_file}.json")
        
        # Log statistics
        success_count = len(job_state.completed_urls)
        total = job_state.total_urls
        self.logger.info(f"📊 Batch completed: {success_count}/{total} successes ({(success_count/total)*100:.1f}%)")
        
        return job_state
    
    def run_production(self):
        """Execute production monitoring"""
        self.logger.info("🎯 STARTING PRODUCTION MONITORING")
        self.logger.info(f"📋 Sites configured: {len(PRODUCTION_SITES)}")
        
        if not PRODUCTION_SITES:
            self.logger.error("❌ ERROR: No sites configured in PRODUCTION_SITES!")
            return
        
        # Check if within time window
        if not self.check_time_window():
            self.logger.info("⏸️ Waiting for allowed time window...")
            return
        
        try:
            # Execute batch
            job_state = self.execute_batch(PRODUCTION_SITES)
            
            # Pause between batches
            self.logger.info(f"⏸️ Pause of {PAUSE_BETWEEN_BATCHES}s before next batch...")
            time.sleep(PAUSE_BETWEEN_BATCHES)
            
        except Exception as e:
            self.logger.error(f"💥 CRITICAL ERROR: {str(e)}")
            raise
        
        self.logger.info("✅ Production cycle completed")

def main():
    print("🤖 PRODUCTION MONITOR - EthicalScraper")
    print("=" * 50)
    print("⚠️  ATTENTION: Make sure you have edited production_config.py!")
    print("🛑 To stop: Ctrl+C (kill switch)")
    print("=" * 50)
    
    # Check if configurations were edited
    if "mysite.com" in USER_AGENT or "contact@mysite.com" in USER_AGENT:
        print("❌ ERROR: You need to edit production_config.py first!")
        print("📝 Edit USER_AGENT with YOUR real website and email!")
        sys.exit(1)
    
    if len(PRODUCTION_SITES) == 0 or "example.com" in str(PRODUCTION_SITES):
        print("❌ ERROR: Configure your real sites in PRODUCTION_SITES!")
        sys.exit(1)
    
    # Confirm start
    response = input("🤔 Confirm production start? (y/N): ").lower()
    if response != 'y':
        print("🛑 Production cancelled")
        sys.exit(0)
    
    # Start monitor
    monitor = ProductionMonitor()
    monitor.run_production()

if __name__ == "__main__":
    main()