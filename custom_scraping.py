#!/usr/bin/env python3
"""
CUSTOM SCRAPING - For when you want total control!
"""

from datetime import datetime
from pathlib import Path
from src.scraper_etico import ScraperEtico
from src.batch_processor import BatchProcessor

def custom_scraping(sites, project_name="MyScraping"):
    """
    Function for custom scraping with automatic export
    
    Args:
        sites: List of URLs for scraping
        project_name: Name to identify the files
    """
    
    print(f"🚀 CUSTOM SCRAPING: {project_name}")
    print("=" * 50)
    print(f"🔗 Sites to process: {len(sites)}")
    
    # 1. Configure scraper
    scraper = ScraperEtico(
        user_agent="PublicPriceMonitor/1.0 (+https://yoursite.com; youremail@example.com)",
        default_delay=3.0,  # 3 seconds between requests
        timeout=30.0
    )
    
    # 2. Configure batch processor
    processor = BatchProcessor()
    processor.scraper = scraper
    
    # 3. Execute scraping
    print("\n🔄 Starting scraping...")
    job_state = processor.process_batch(
        sites,
        max_workers=2,          # 2 parallel threads
        analyze_robots=True,    # Analyze complete robots.txt
        show_progress=True      # Show progress bar
    )
    
    # 4. Show results
    print(f"\n📊 RESULTS:")
    print(f"   Total processed: {job_state.processed_count}")
    print(f"   Successes: {len(job_state.completed_urls)}")
    print(f"   Failures: {len(job_state.failed_urls)}")
    print(f"   Success rate: {job_state.completion_percentage:.1f}%")
    
    # 5. Automatic export
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create results folder
    output_dir = Path("./custom_results")
    output_dir.mkdir(exist_ok=True)
    
    # Export CSV
    csv_file = output_dir / f"{project_name}_{timestamp}.csv"
    processor.export_to_csv(job_state, csv_file)
    print(f"📄 CSV saved: {csv_file}")
    
    # Export JSON
    json_file = output_dir / f"{project_name}_{timestamp}.json"
    processor.export_to_json(job_state, json_file)
    print(f"📄 JSON saved: {json_file}")
    
    # 6. Summary report
    processor.print_summary_report(job_state)
    
    return job_state, csv_file, json_file

# USAGE EXAMPLES:

if __name__ == "__main__":
    print("🎯 CUSTOM SCRAPING EXAMPLES")
    print("=" * 50)
    
    # Example 1: Government sites
    print("\n📋 EXAMPLE 1: Government sites")
    gov_sites = [
        "https://www.gov.br/compras/pt-br",
        "https://portal.tcu.gov.br",
        "https://www.bcb.gov.br"
    ]
    
    response = input("Execute example 1? (y/N): ").lower()
    if response == 'y':
        custom_scraping(gov_sites, "GovernmentSites")
    
    # Example 2: User-specific sites
    print("\n📋 EXAMPLE 2: Your custom sites")
    print("Edit the list below with your sites:")
    
    my_sites = [
        # ADD YOUR SITES HERE:
        # "https://site1.com",
        # "https://site2.com", 
    ]
    
    if my_sites:
        response = input("Execute scraping of your sites? (y/N): ").lower()
        if response == 'y':
            custom_scraping(my_sites, "MyProjects")
    else:
        print("⚠️ No sites configured. Edit the 'my_sites' list above.")
    
    print("\n✅ Custom scraping completed!")
    print("📁 Files saved in: ./custom_results/")