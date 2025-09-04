#!/usr/bin/env python3
"""
Example usage of the RobotsAnalyzer for comprehensive robots.txt analysis.

This example demonstrates the key features of the analyzer including:
- Parsing robots.txt content
- Extracting crawl delays for different user agents
- Analyzing sitemap URLs
- Comparing permissions between user agents
- Generating detailed analysis reports
"""

from src.analyzer import RobotsAnalyzer

def main():
    """Demonstrate key features of RobotsAnalyzer."""
    
    # Sample robots.txt content
    sample_robots = """
# Example robots.txt
User-agent: *
Crawl-delay: 1
Disallow: /private/
Disallow: /admin/
Allow: /public/

User-agent: Googlebot
Crawl-delay: 0.5
Disallow: /admin/
Allow: /

User-agent: BadBot
Disallow: /

Sitemap: https://example.com/sitemap.xml
Sitemap: https://example.com/products.xml
"""
    
    print("🤖 RobotsAnalyzer Example Usage")
    print("=" * 40)
    
    # Initialize analyzer
    analyzer = RobotsAnalyzer()
    
    # Parse the robots.txt content
    report = analyzer.parse_robots_txt(sample_robots, "https://example.com/robots.txt")
    
    # 1. Extract crawl delays
    print("\n⏰ Crawl Delays by User Agent:")
    crawl_delays = analyzer.extract_crawl_delays(report)
    for user_agent, delay in crawl_delays.items():
        print(f"  • {user_agent}: {delay}s" if delay else f"  • {user_agent}: Not specified")
    
    # 2. Extract and validate sitemaps
    print("\n🗺️  Sitemap URLs:")
    sitemaps = analyzer.extract_sitemap_urls(report, validate=True)
    for sitemap in sitemaps:
        print(f"  • {sitemap}")
    
    # 3. Analyze specific user agent
    print("\n🔍 User Agent Analysis for 'Googlebot':")
    googlebot_analysis = analyzer.analyze_by_user_agent(report, "Googlebot")
    if googlebot_analysis['found']:
        rules = googlebot_analysis['rules']
        stats = googlebot_analysis['statistics']
        print(f"  • Allow rules: {stats['total_allow_rules']}")
        print(f"  • Disallow rules: {stats['total_disallow_rules']}")
        print(f"  • Crawl delay: {rules['crawl_delay']}s")
        print(f"  • Restrictiveness score: {stats['restrictiveness_score']:.2f}")
    
    # 4. Compare different user agents
    print("\n⚖️  User Agent Comparison:")
    comparison = analyzer.compare_user_agents(report, ["*", "Googlebot", "BadBot"])
    summary = comparison['summary']
    print(f"  • Most restrictive: {summary['most_restrictive'][0]} ({summary['most_restrictive'][1]:.2f})")
    print(f"  • Least restrictive: {summary['least_restrictive'][0]} ({summary['least_restrictive'][1]:.2f})")
    
    # 5. Show statistics
    print("\n📊 Statistics:")
    stats = report.statistics
    print(f"  • Total user agents: {stats['total_user_agents']}")
    print(f"  • Total rules: {stats['total_allow_rules'] + stats['total_disallow_rules']}")
    print(f"  • Average crawl delay: {stats['avg_crawl_delay']:.1f}s")
    print(f"  • Most common pattern: {stats['most_common_patterns'][0][0] if stats['most_common_patterns'] else 'N/A'}")
    
    # 6. Generate full report
    print("\n📄 Full Analysis Report:")
    print("-" * 40)
    full_report = analyzer.generate_analysis_report(report)
    print(full_report)
    
    print("\n✅ Analysis complete!")

if __name__ == "__main__":
    main()