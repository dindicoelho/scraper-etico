"""
Advanced Robots.txt Analyzer for ScraperEtico

This module provides comprehensive analysis capabilities for robots.txt files,
including rule parsing, user-agent analysis, sitemap extraction, and detailed reporting.
"""

import re
import logging
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from urllib.parse import urlparse, urljoin, urlunparse
from urllib.robotparser import RobotFileParser
from urllib.error import URLError, HTTPError
import requests
from requests.exceptions import RequestException


@dataclass
class UserAgentRules:
    """Container for rules specific to a user-agent."""
    
    user_agent: str
    allow_patterns: List[str] = field(default_factory=list)
    disallow_patterns: List[str] = field(default_factory=list)
    crawl_delay: Optional[float] = None
    request_rate: Optional[str] = None
    visit_time: Optional[str] = None
    
    def __post_init__(self):
        """Ensure patterns are stored as lists."""
        if isinstance(self.allow_patterns, str):
            self.allow_patterns = [self.allow_patterns]
        if isinstance(self.disallow_patterns, str):
            self.disallow_patterns = [self.disallow_patterns]


@dataclass
class RobotsAnalysisReport:
    """Comprehensive analysis report for a robots.txt file."""
    
    url: str
    raw_content: str
    user_agents: Dict[str, UserAgentRules] = field(default_factory=dict)
    sitemaps: List[str] = field(default_factory=list)
    invalid_sitemaps: List[str] = field(default_factory=list)
    comments: List[str] = field(default_factory=list)
    unknown_directives: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    file_size: int = 0
    line_count: int = 0
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)


class RobotsAnalyzer:
    """
    Advanced analyzer for robots.txt files with comprehensive parsing and analysis capabilities.
    
    This class provides detailed analysis of robots.txt files including:
    - User-agent specific rule extraction
    - Crawl-delay analysis across different user-agents
    - Sitemap URL parsing and validation
    - Pattern analysis and statistics
    - Permission comparison between user-agents
    - Detailed reporting and validation
    
    Attributes:
        timeout (float): Request timeout for fetching robots.txt files
        logger (logging.Logger): Logger instance for detailed logging
    """
    
    def __init__(self, timeout: float = 30.0, log_level: int = logging.INFO):
        """
        Initialize the RobotsAnalyzer.
        
        Args:
            timeout: Request timeout in seconds for fetching robots.txt files
            log_level: Logging level (default: logging.INFO)
        """
        self.timeout = timeout
        self.logger = self._setup_logger(log_level)
        
        # Compile regex patterns for efficient parsing
        self._user_agent_pattern = re.compile(r'^user-agent:\s*(.*)$', re.IGNORECASE)
        self._disallow_pattern = re.compile(r'^disallow:\s*(.*)$', re.IGNORECASE)
        self._allow_pattern = re.compile(r'^allow:\s*(.*)$', re.IGNORECASE)
        self._crawl_delay_pattern = re.compile(r'^crawl-delay:\s*(\d+(?:\.\d+)?)$', re.IGNORECASE)
        self._request_rate_pattern = re.compile(r'^request-rate:\s*(.*)$', re.IGNORECASE)
        self._visit_time_pattern = re.compile(r'^visit-time:\s*(.*)$', re.IGNORECASE)
        self._sitemap_pattern = re.compile(r'^sitemap:\s*(.*)$', re.IGNORECASE)
        self._comment_pattern = re.compile(r'^\s*#(.*)$')
        
    def _setup_logger(self, log_level: int) -> logging.Logger:
        """
        Set up logger with timestamp formatting.
        
        Args:
            log_level: The logging level to use
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(f"{self.__class__.__name__}")
        logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        logger.handlers = []
        
        # Create console handler with formatting
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def fetch_robots_txt(self, url: str) -> Optional[str]:
        """
        Fetch robots.txt content from a URL.
        
        Args:
            url: Base URL or direct robots.txt URL
            
        Returns:
            Raw robots.txt content or None if fetch failed
        """
        if not url.endswith('/robots.txt'):
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        else:
            robots_url = url
            
        try:
            self.logger.info(f"Fetching robots.txt from: {robots_url}")
            headers = {'User-Agent': 'RobotsAnalyzer/1.0 (Analysis Tool)'}
            response = requests.get(robots_url, timeout=self.timeout, headers=headers)
            response.raise_for_status()
            
            content = response.text
            self.logger.info(f"Successfully fetched robots.txt ({len(content)} chars)")
            return content
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Timeout fetching robots.txt from {robots_url}")
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Connection error fetching robots.txt from {robots_url}")
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error {e.response.status_code} fetching robots.txt from {robots_url}")
        except Exception as e:
            self.logger.error(f"Unexpected error fetching robots.txt from {robots_url}: {e}")
            
        return None
    
    def parse_robots_txt(self, content: str, source_url: str = "") -> RobotsAnalysisReport:
        """
        Parse robots.txt content and generate comprehensive analysis report.
        
        Args:
            content: Raw robots.txt content
            source_url: Source URL for the robots.txt file
            
        Returns:
            Comprehensive analysis report
        """
        report = RobotsAnalysisReport(
            url=source_url,
            raw_content=content,
            file_size=len(content),
            line_count=len(content.splitlines())
        )
        
        lines = content.splitlines()
        current_user_agents = []  # Track current user-agent context
        
        self.logger.debug(f"Parsing robots.txt with {len(lines)} lines")
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Extract comments
            comment_match = self._comment_pattern.match(original_line)
            if comment_match:
                comment = comment_match.group(1).strip()
                if comment:  # Only store non-empty comments
                    report.comments.append(comment)
                continue
            
            try:
                # Parse user-agent directive
                ua_match = self._user_agent_pattern.match(line)
                if ua_match:
                    user_agent = ua_match.group(1).strip()
                    if user_agent:
                        current_user_agents = [user_agent]
                        if user_agent not in report.user_agents:
                            report.user_agents[user_agent] = UserAgentRules(user_agent=user_agent)
                    continue
                
                # Parse disallow directive
                disallow_match = self._disallow_pattern.match(line)
                if disallow_match and current_user_agents:
                    path = disallow_match.group(1).strip()
                    for ua in current_user_agents:
                        if ua in report.user_agents:
                            report.user_agents[ua].disallow_patterns.append(path)
                    continue
                
                # Parse allow directive
                allow_match = self._allow_pattern.match(line)
                if allow_match and current_user_agents:
                    path = allow_match.group(1).strip()
                    for ua in current_user_agents:
                        if ua in report.user_agents:
                            report.user_agents[ua].allow_patterns.append(path)
                    continue
                
                # Parse crawl-delay directive
                crawl_delay_match = self._crawl_delay_pattern.match(line)
                if crawl_delay_match and current_user_agents:
                    delay = float(crawl_delay_match.group(1))
                    for ua in current_user_agents:
                        if ua in report.user_agents:
                            report.user_agents[ua].crawl_delay = delay
                    continue
                
                # Parse request-rate directive
                request_rate_match = self._request_rate_pattern.match(line)
                if request_rate_match and current_user_agents:
                    rate = request_rate_match.group(1).strip()
                    for ua in current_user_agents:
                        if ua in report.user_agents:
                            report.user_agents[ua].request_rate = rate
                    continue
                
                # Parse visit-time directive
                visit_time_match = self._visit_time_pattern.match(line)
                if visit_time_match and current_user_agents:
                    visit_time = visit_time_match.group(1).strip()
                    for ua in current_user_agents:
                        if ua in report.user_agents:
                            report.user_agents[ua].visit_time = visit_time
                    continue
                
                # Parse sitemap directive
                sitemap_match = self._sitemap_pattern.match(line)
                if sitemap_match:
                    sitemap_url = sitemap_match.group(1).strip()
                    if self._validate_sitemap_url(sitemap_url, source_url):
                        report.sitemaps.append(sitemap_url)
                    else:
                        report.invalid_sitemaps.append(sitemap_url)
                    continue
                
                # Track unknown directives
                if ':' in line and not line.startswith('#'):
                    directive = line.split(':', 1)[0].strip().lower()
                    known_directives = {
                        'user-agent', 'disallow', 'allow', 'crawl-delay',
                        'request-rate', 'visit-time', 'sitemap'
                    }
                    if directive not in known_directives:
                        report.unknown_directives.append(line)
                        
            except Exception as e:
                error_msg = f"Error parsing line {line_num}: '{line}' - {str(e)}"
                report.errors.append(error_msg)
                self.logger.warning(error_msg)
                report.is_valid = False
        
        # Generate statistics
        report.statistics = self._generate_statistics(report)
        
        self.logger.info(f"Parsed robots.txt: {len(report.user_agents)} user-agents, "
                        f"{len(report.sitemaps)} sitemaps, {len(report.errors)} errors")
        
        return report
    
    def _validate_sitemap_url(self, sitemap_url: str, base_url: str = "") -> bool:
        """
        Validate a sitemap URL.
        
        Args:
            sitemap_url: The sitemap URL to validate
            base_url: Base URL for resolving relative URLs
            
        Returns:
            True if the URL appears to be valid, False otherwise
        """
        try:
            # Handle relative URLs
            if base_url and not sitemap_url.startswith(('http://', 'https://')):
                sitemap_url = urljoin(base_url, sitemap_url)
            
            parsed = urlparse(sitemap_url)
            
            # Basic URL structure validation
            if not parsed.scheme or not parsed.netloc:
                return False
                
            # Check for common sitemap extensions
            path = parsed.path.lower()
            valid_extensions = ['.xml', '.txt', '.gz']
            
            # Allow URLs without extension (some sites use dynamic sitemaps)
            if not any(path.endswith(ext) for ext in valid_extensions) and '.' in path:
                return False
            
            return True
            
        except Exception:
            return False
    
    def _generate_statistics(self, report: RobotsAnalysisReport) -> Dict[str, Any]:
        """
        Generate comprehensive statistics for the robots.txt analysis.
        
        Args:
            report: The analysis report to generate statistics for
            
        Returns:
            Dictionary containing various statistics
        """
        stats = {}
        
        # Basic counts
        stats['total_user_agents'] = len(report.user_agents)
        stats['total_sitemaps'] = len(report.sitemaps)
        stats['total_comments'] = len(report.comments)
        stats['total_errors'] = len(report.errors)
        stats['unknown_directives'] = len(report.unknown_directives)
        
        # User agent analysis
        allow_counts = [len(ua.allow_patterns) for ua in report.user_agents.values()]
        disallow_counts = [len(ua.disallow_patterns) for ua in report.user_agents.values()]
        crawl_delays = [ua.crawl_delay for ua in report.user_agents.values() if ua.crawl_delay is not None]
        
        stats['total_allow_rules'] = sum(allow_counts)
        stats['total_disallow_rules'] = sum(disallow_counts)
        stats['avg_allow_rules_per_ua'] = sum(allow_counts) / len(allow_counts) if allow_counts else 0
        stats['avg_disallow_rules_per_ua'] = sum(disallow_counts) / len(disallow_counts) if disallow_counts else 0
        
        # Crawl delay analysis
        stats['user_agents_with_crawl_delay'] = len(crawl_delays)
        stats['min_crawl_delay'] = min(crawl_delays) if crawl_delays else None
        stats['max_crawl_delay'] = max(crawl_delays) if crawl_delays else None
        stats['avg_crawl_delay'] = sum(crawl_delays) / len(crawl_delays) if crawl_delays else None
        
        # Pattern analysis
        all_patterns = []
        for ua in report.user_agents.values():
            all_patterns.extend(ua.allow_patterns)
            all_patterns.extend(ua.disallow_patterns)
        
        pattern_counter = Counter(all_patterns)
        stats['most_common_patterns'] = pattern_counter.most_common(10)
        stats['unique_patterns'] = len(pattern_counter)
        
        # Special user agents
        special_uas = {'*', 'googlebot', 'bingbot', 'slurp', 'duckduckbot', 'baiduspider'}
        found_special = [ua for ua in report.user_agents.keys() 
                        if ua.lower() in special_uas or ua == '*']
        stats['special_user_agents'] = found_special
        
        return stats
    
    def extract_crawl_delays(self, report: RobotsAnalysisReport) -> Dict[str, Optional[float]]:
        """
        Extract crawl-delay values for all user-agents.
        
        Args:
            report: Analysis report to extract delays from
            
        Returns:
            Dictionary mapping user-agent to crawl delay (None if not specified)
        """
        delays = {}
        for user_agent, rules in report.user_agents.items():
            delays[user_agent] = rules.crawl_delay
        
        self.logger.debug(f"Extracted crawl delays for {len(delays)} user-agents")
        return delays
    
    def extract_sitemap_urls(self, report: RobotsAnalysisReport, validate: bool = True) -> List[str]:
        """
        Extract and optionally validate sitemap URLs.
        
        Args:
            report: Analysis report to extract sitemaps from
            validate: Whether to validate sitemap URLs (default: True)
            
        Returns:
            List of sitemap URLs
        """
        if validate:
            valid_sitemaps = []
            for sitemap in report.sitemaps:
                if self._validate_sitemap_url(sitemap, report.url):
                    valid_sitemaps.append(sitemap)
                else:
                    self.logger.warning(f"Invalid sitemap URL detected: {sitemap}")
            return valid_sitemaps
        
        return report.sitemaps.copy()
    
    def analyze_by_user_agent(self, report: RobotsAnalysisReport, user_agent: str = "*") -> Dict[str, Any]:
        """
        Analyze rules for a specific user-agent.
        
        Args:
            report: Analysis report to analyze
            user_agent: User-agent to analyze (default: "*" for all)
            
        Returns:
            Dictionary containing analysis results for the specified user-agent
        """
        # Find matching user agent rules (case insensitive)
        matching_ua = None
        for ua_name, rules in report.user_agents.items():
            if ua_name.lower() == user_agent.lower():
                matching_ua = rules
                break
        
        if not matching_ua:
            # If specific user agent not found, try wildcard
            matching_ua = report.user_agents.get("*")
        
        if not matching_ua:
            return {
                'user_agent': user_agent,
                'found': False,
                'message': f'No rules found for user-agent "{user_agent}"'
            }
        
        analysis = {
            'user_agent': user_agent,
            'found': True,
            'rules': {
                'allow_patterns': matching_ua.allow_patterns.copy(),
                'disallow_patterns': matching_ua.disallow_patterns.copy(),
                'crawl_delay': matching_ua.crawl_delay,
                'request_rate': matching_ua.request_rate,
                'visit_time': matching_ua.visit_time
            },
            'statistics': {
                'total_allow_rules': len(matching_ua.allow_patterns),
                'total_disallow_rules': len(matching_ua.disallow_patterns),
                'has_crawl_delay': matching_ua.crawl_delay is not None,
                'has_request_rate': matching_ua.request_rate is not None,
                'has_visit_time': matching_ua.visit_time is not None
            }
        }
        
        # Analyze pattern restrictiveness
        disallow_all = "/" in matching_ua.disallow_patterns
        analysis['statistics']['blocks_all_paths'] = disallow_all
        analysis['statistics']['restrictiveness_score'] = self._calculate_restrictiveness(matching_ua)
        
        return analysis
    
    def _calculate_restrictiveness(self, rules: UserAgentRules) -> float:
        """
        Calculate a restrictiveness score (0-1) for user agent rules.
        
        Args:
            rules: User agent rules to analyze
            
        Returns:
            Restrictiveness score between 0 (permissive) and 1 (very restrictive)
        """
        score = 0.0
        
        # Check for total disallow
        if "/" in rules.disallow_patterns:
            score += 0.5
        
        # Factor in number of disallow patterns
        disallow_count = len(rules.disallow_patterns)
        if disallow_count > 0:
            score += min(disallow_count / 20.0, 0.3)  # Max 0.3 points for many rules
        
        # Factor in crawl delay (higher delay = more restrictive)
        if rules.crawl_delay:
            score += min(rules.crawl_delay / 30.0, 0.2)  # Max 0.2 points for long delays
        
        return min(score, 1.0)
    
    def compare_user_agents(self, report: RobotsAnalysisReport, 
                          user_agents: List[str]) -> Dict[str, Any]:
        """
        Compare permissions and restrictions between different user-agents.
        
        Args:
            report: Analysis report containing user-agent rules
            user_agents: List of user-agents to compare
            
        Returns:
            Dictionary containing comparison results
        """
        comparison = {
            'user_agents': user_agents,
            'analysis': {},
            'summary': {}
        }
        
        # Analyze each user agent
        for ua in user_agents:
            comparison['analysis'][ua] = self.analyze_by_user_agent(report, ua)
        
        # Generate comparison summary
        found_uas = [ua for ua in user_agents 
                    if comparison['analysis'][ua]['found']]
        
        if len(found_uas) < 2:
            comparison['summary']['message'] = "Need at least 2 valid user-agents for comparison"
            return comparison
        
        # Compare restrictiveness
        restrictiveness = {ua: comparison['analysis'][ua]['statistics']['restrictiveness_score'] 
                          for ua in found_uas}
        
        most_restrictive = max(restrictiveness.items(), key=lambda x: x[1])
        least_restrictive = min(restrictiveness.items(), key=lambda x: x[1])
        
        comparison['summary'] = {
            'most_restrictive': most_restrictive,
            'least_restrictive': least_restrictive,
            'avg_restrictiveness': sum(restrictiveness.values()) / len(restrictiveness),
            'crawl_delays': {ua: comparison['analysis'][ua]['rules']['crawl_delay'] 
                           for ua in found_uas},
            'common_restrictions': self._find_common_patterns(
                [comparison['analysis'][ua]['rules']['disallow_patterns'] 
                 for ua in found_uas]
            )
        }
        
        return comparison
    
    def _find_common_patterns(self, pattern_lists: List[List[str]]) -> List[str]:
        """
        Find patterns common to all user agents.
        
        Args:
            pattern_lists: List of pattern lists to compare
            
        Returns:
            List of common patterns
        """
        if not pattern_lists:
            return []
        
        common = set(pattern_lists[0])
        for patterns in pattern_lists[1:]:
            common &= set(patterns)
        
        return list(common)
    
    def generate_analysis_report(self, report: RobotsAnalysisReport) -> str:
        """
        Generate a human-readable analysis report.
        
        Args:
            report: Analysis report to format
            
        Returns:
            Formatted string report
        """
        lines = []
        lines.append("=" * 60)
        lines.append("ROBOTS.TXT ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"Source URL: {report.url}")
        lines.append(f"File Size: {report.file_size} bytes")
        lines.append(f"Line Count: {report.line_count}")
        lines.append(f"Valid: {'Yes' if report.is_valid else 'No'}")
        
        if report.errors:
            lines.append(f"Errors: {len(report.errors)}")
            for error in report.errors[:5]:  # Show first 5 errors
                lines.append(f"  - {error}")
            if len(report.errors) > 5:
                lines.append(f"  ... and {len(report.errors) - 5} more")
        
        lines.append("")
        lines.append("STATISTICS")
        lines.append("-" * 30)
        stats = report.statistics
        lines.append(f"User Agents: {stats['total_user_agents']}")
        lines.append(f"Allow Rules: {stats['total_allow_rules']}")
        lines.append(f"Disallow Rules: {stats['total_disallow_rules']}")
        lines.append(f"Sitemaps: {stats['total_sitemaps']}")
        lines.append(f"Comments: {stats['total_comments']}")
        
        if stats.get('avg_crawl_delay'):
            lines.append(f"Average Crawl Delay: {stats['avg_crawl_delay']:.1f}s")
        
        lines.append("")
        lines.append("USER AGENTS")
        lines.append("-" * 30)
        for ua_name, rules in report.user_agents.items():
            lines.append(f"• {ua_name}")
            lines.append(f"  Allow: {len(rules.allow_patterns)} rules")
            lines.append(f"  Disallow: {len(rules.disallow_patterns)} rules")
            if rules.crawl_delay:
                lines.append(f"  Crawl Delay: {rules.crawl_delay}s")
            if rules.request_rate:
                lines.append(f"  Request Rate: {rules.request_rate}")
        
        if report.sitemaps:
            lines.append("")
            lines.append("SITEMAPS")
            lines.append("-" * 30)
            for sitemap in report.sitemaps:
                lines.append(f"• {sitemap}")
        
        if stats.get('most_common_patterns'):
            lines.append("")
            lines.append("MOST COMMON PATTERNS")
            lines.append("-" * 30)
            for pattern, count in stats['most_common_patterns'][:5]:
                lines.append(f"• {pattern} (used {count} times)")
        
        return "\n".join(lines)
    
    def analyze_url(self, url: str) -> Optional[RobotsAnalysisReport]:
        """
        Fetch and analyze robots.txt from a URL.
        
        Args:
            url: Base URL or direct robots.txt URL to analyze
            
        Returns:
            Analysis report or None if fetch/analysis failed
        """
        content = self.fetch_robots_txt(url)
        if content is None:
            return None
        
        return self.parse_robots_txt(content, url)