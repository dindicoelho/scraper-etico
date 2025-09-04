"""
ScraperEtico - Ethical Web Scraping Library
"""

from .scraper_etico import ScraperEtico
from .analyzer import RobotsAnalyzer, UserAgentRules, RobotsAnalysisReport

__version__ = "1.0.0"
__all__ = ["ScraperEtico", "RobotsAnalyzer", "UserAgentRules", "RobotsAnalysisReport"]