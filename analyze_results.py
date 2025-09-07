#!/usr/bin/env python3
"""
RESULTS ANALYSIS - To understand your scraping data
"""

import json
import csv
from pathlib import Path
from collections import Counter
from datetime import datetime

def analyze_csv(csv_file):
    """Analyze results from a CSV file"""
    print(f"📊 ANALYZING: {csv_file}")
    print("-" * 50)
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    print(f"📋 Total records: {len(data)}")
    
    # Success analysis
    successes = [d for d in data if d.get('success') == 'True']
    failures = [d for d in data if d.get('success') == 'False']
    
    print(f"✅ Successes: {len(successes)} ({len(successes)/len(data)*100:.1f}%)")
    print(f"❌ Failures: {len(failures)} ({len(failures)/len(data)*100:.1f}%)")
    
    # Domain analysis
    domains = Counter(d.get('domain', 'N/A') for d in data)
    print(f"\n🌐 TOP 5 DOMAINS:")
    for domain, count in domains.most_common(5):
        print(f"   {domain}: {count} URLs")
    
    # Status code analysis
    status_codes = Counter(d.get('status_code', 'N/A') for d in successes)
    print(f"\n📊 STATUS CODES:")
    for status, count in status_codes.most_common(5):
        print(f"   {status}: {count} times")
    
    # Error analysis
    if failures:
        errors = Counter(d.get('error_type', 'N/A') for d in failures)
        print(f"\n❌ ERROR TYPES:")
        for error, count in errors.most_common(3):
            print(f"   {error}: {count} times")
    
    # Sites that blocked
    blocked = [d for d in data if d.get('robots_allowed') == 'False']
    if blocked:
        print(f"\n🚫 SITES THAT BLOCKED:")
        for site in blocked[:5]:
            print(f"   {site.get('url', 'N/A')[:50]}...")
    
    return data

def analyze_json(json_file):
    """Analyze results from a JSON file"""
    print(f"📊 ANALYZING: {json_file}")
    print("-" * 50)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Job metadata
    if 'job_metadata' in data:
        meta = data['job_metadata']
        print(f"🆔 Job ID: {meta.get('job_id', 'N/A')}")
        print(f"📈 Success rate: {meta.get('success_count', 0)}/{meta.get('total_urls', 0)}")
        
        if 'duration' in meta and meta['duration']:
            print(f"⏱️  Total time: {meta['duration'].get('human_readable', 'N/A')}")
    
    # Results analysis
    if 'results' in data:
        results = data['results']
        print(f"\n📋 Total results: {len(results)}")
        
        # Average response size
        sizes = [r.get('response_size', 0) for r in results if r.get('response_size')]
        if sizes:
            avg_size = sum(sizes) / len(sizes)
            print(f"📏 Average page size: {avg_size:.0f} bytes")
        
        # Average response time
        times = [r.get('response_time', 0) for r in results if r.get('response_time')]
        if times:
            avg_time = sum(times) / len(times)
            print(f"⏱️  Average response time: {avg_time:.2f}s")
    
    return data

def generate_complete_report(data_folder="production_data"):
    """Generate complete report of all files"""
    print("📋 COMPLETE SCRAPING REPORT")
    print("=" * 60)
    
    folder = Path(data_folder)
    if not folder.exists():
        print(f"❌ Folder {data_folder} not found!")
        return
    
    # Find files
    csvs = list(folder.glob("*.csv"))
    jsons = list(folder.glob("*.json"))
    
    print(f"📁 Analyzed folder: {folder}")
    print(f"📄 CSV files: {len(csvs)}")
    print(f"📄 JSON files: {len(jsons)}")
    
    if not csvs and not jsons:
        print("⚠️ No data files found!")
        return
    
    # Analyze most recent file
    if csvs:
        recent_csv = max(csvs, key=lambda x: x.stat().st_mtime)
        print(f"\n🔍 ANALYZING MOST RECENT FILE:")
        csv_data = analyze_csv(recent_csv)
    
    if jsons:
        recent_json = max(jsons, key=lambda x: x.stat().st_mtime)
        print(f"\n🔍 DETAILED ANALYSIS (JSON):")
        json_data = analyze_json(recent_json)
    
    # Execution history
    print(f"\n📈 EXECUTION HISTORY:")
    all_files = sorted(csvs + jsons, key=lambda x: x.stat().st_mtime, reverse=True)
    
    for i, file in enumerate(all_files[:10]):  # Last 10
        modified = datetime.fromtimestamp(file.stat().st_mtime)
        size = file.stat().st_size
        print(f"   {i+1:2d}. {file.name} ({size} bytes) - {modified.strftime('%Y-%m-%d %H:%M')}")
    
    print(f"\n💡 HOW TO VIEW DATA:")
    print(f"   open {folder}/")
    print(f"   head -10 {recent_csv.name if csvs else 'file.csv'}")
    print(f"   cat {recent_json.name if jsons else 'file.json'} | python3 -m json.tool")

if __name__ == "__main__":
    print("🎯 SCRAPING RESULTS ANALYZER")
    print("=" * 50)
    
    # Options menu
    print("📋 OPTIONS:")
    print("1. Analyze production_data/ folder")
    print("2. Analyze custom_results/ folder")
    print("3. Analyze specific file")
    print("4. Complete report")
    
    option = input("\n🤔 Choose an option (1-4): ").strip()
    
    if option == "1":
        generate_complete_report("production_data")
    
    elif option == "2":
        generate_complete_report("custom_results")
    
    elif option == "3":
        file_path = input("📄 Enter file path: ").strip()
        file_obj = Path(file_path)
        if file_obj.exists():
            if file_path.endswith('.csv'):
                analyze_csv(file_obj)
            elif file_path.endswith('.json'):
                analyze_json(file_obj)
            else:
                print("❌ Unsupported format. Use CSV or JSON.")
        else:
            print(f"❌ File not found: {file_path}")
    
    elif option == "4":
        print("📊 COMPLETE REPORTS:")
        generate_complete_report("production_data")
        print("\n" + "="*60)
        generate_complete_report("custom_results")
    
    else:
        print("❌ Invalid option!")
    
    print("\n✅ Analysis complete!")