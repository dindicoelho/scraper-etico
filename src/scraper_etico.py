"""
ScraperEtico - Ethical Web Scraper with robots.txt compliance
"""

import time
import logging
from typing import Optional, Dict, Any, Union
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from urllib.error import URLError, HTTPError
from datetime import datetime
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError


class ScraperEtico:
    """
    An ethical web scraper that respects robots.txt rules and implements rate limiting.
    
    This class provides a responsible way to scrape websites by:
    - Checking robots.txt permissions before accessing URLs
    - Implementing configurable rate limiting
    - Using customizable user-agent strings
    - Providing detailed logging with timestamps
    - Handling network errors gracefully
    
    Attributes:
        user_agent (str): The user-agent string to use for requests
        default_delay (float): Default delay between requests in seconds
        timeout (float): Request timeout in seconds
        logger (logging.Logger): Logger instance for detailed logging
    """
    
    def __init__(
        self,
        user_agent: str = "ScraperEtico/1.0 (Ethical Web Scraper)",
        default_delay: float = 1.0,
        timeout: float = 30.0,
        log_level: int = logging.INFO
    ):
        """
        Initialize the ScraperEtico instance.
        
        Args:
            user_agent: User-agent string to identify the scraper
            default_delay: Default delay between requests in seconds (minimum 0.1)
            timeout: Request timeout in seconds
            log_level: Logging level (default: logging.INFO)
        """
        self.user_agent = user_agent
        self.default_delay = max(0.1, default_delay)  # Ensure minimum delay
        self.timeout = timeout
        self._last_request_time: Dict[str, float] = {}  # Track last request time per domain
        self._robots_cache: Dict[str, RobotFileParser] = {}  # Cache robots.txt parsers
        
        # Setup logging
        self.logger = self._setup_logger(log_level)
        self.logger.info(f"ScraperEtico initialized with user-agent: {self.user_agent}")
        
    def _setup_logger(self, log_level: int) -> logging.Logger:
        """
        Set up logger with timestamp formatting.
        
        Args:
            log_level: The logging level to use
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(self.__class__.__name__)
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
    
    def can_fetch(self, url: str, force_refresh: bool = False) -> bool:
        """
        Check if the given URL can be fetched according to robots.txt rules.
        
        Args:
            url: The URL to check
            force_refresh: Force refresh of cached robots.txt (default: False)
            
        Returns:
            True if the URL can be fetched, False otherwise
        """
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        # Get or create robots parser for this domain
        if robots_url not in self._robots_cache or force_refresh:
            self.logger.debug(f"Fetching robots.txt from: {robots_url}")
            robot_parser = self._fetch_robots_txt(robots_url)
            if robot_parser:
                self._robots_cache[robots_url] = robot_parser
            else:
                # If robots.txt is not available, assume we can fetch
                self.logger.warning(f"No robots.txt found for {parsed_url.netloc}, assuming access is allowed")
                return True
        
        robot_parser = self._robots_cache.get(robots_url)
        if robot_parser:
            can_fetch = robot_parser.can_fetch(self.user_agent, url)
            self.logger.debug(f"Robots.txt check for {url}: {'allowed' if can_fetch else 'disallowed'}")
            return can_fetch
        
        return True
    
    def _fetch_robots_txt(self, robots_url: str) -> Optional[RobotFileParser]:
        """
        Fetch and parse robots.txt file.
        
        Args:
            robots_url: URL of the robots.txt file
            
        Returns:
            RobotFileParser instance or None if fetch failed
        """
        robot_parser = RobotFileParser()
        robot_parser.set_url(robots_url)
        
        try:
            robot_parser.read()
            self.logger.info(f"Successfully fetched robots.txt from {robots_url}")
            return robot_parser
        except (URLError, HTTPError) as e:
            self.logger.warning(f"Failed to fetch robots.txt from {robots_url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching robots.txt from {robots_url}: {e}")
            return None
    
    def _apply_rate_limit(self, domain: str, custom_delay: Optional[float] = None) -> None:
        """
        Apply rate limiting for the given domain.
        
        Args:
            domain: The domain to rate limit
            custom_delay: Custom delay to use instead of default
        """
        delay = custom_delay if custom_delay is not None else self.default_delay
        
        if domain in self._last_request_time:
            elapsed = time.time() - self._last_request_time[domain]
            if elapsed < delay:
                sleep_time = delay - elapsed
                self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self._last_request_time[domain] = time.time()
    
    def get(
        self,
        url: str,
        custom_delay: Optional[float] = None,
        check_robots: bool = True,
        **kwargs: Any
    ) -> Optional[requests.Response]:
        """
        Perform a GET request with robots.txt checking and rate limiting.
        
        Args:
            url: The URL to fetch
            custom_delay: Custom delay for this request (overrides default)
            check_robots: Whether to check robots.txt (default: True)
            **kwargs: Additional arguments to pass to requests.get()
            
        Returns:
            Response object if successful, None if request failed or was disallowed
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check robots.txt if enabled
        if check_robots and not self.can_fetch(url):
            self.logger.warning(f"Access to {url} is disallowed by robots.txt")
            return None
        
        # Apply rate limiting
        self._apply_rate_limit(domain, custom_delay)
        
        # Prepare request headers
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = self.user_agent
        
        # Set default timeout if not provided
        timeout = kwargs.pop('timeout', self.timeout)
        
        try:
            self.logger.info(f"Fetching URL: {url}")
            start_time = time.time()
            
            response = requests.get(url, headers=headers, timeout=timeout, **kwargs)
            
            elapsed_time = time.time() - start_time
            self.logger.info(
                f"Request completed: status={response.status_code}, "
                f"size={len(response.content)} bytes, time={elapsed_time:.2f}s"
            )
            
            response.raise_for_status()
            return response
            
        except Timeout:
            self.logger.error(f"Request timeout for URL: {url}")
            return None
        except ConnectionError as e:
            self.logger.error(f"Connection error for URL {url}: {e}")
            return None
        except HTTPError as e:
            self.logger.error(f"HTTP error for URL {url}: {e}")
            return None
        except RequestException as e:
            self.logger.error(f"Request failed for URL {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error fetching URL {url}: {e}")
            return None
    
    def get_crawl_delay(self, url: str) -> Optional[float]:
        """
        Get the crawl delay specified in robots.txt for the given URL.
        
        Args:
            url: The URL to check
            
        Returns:
            Crawl delay in seconds, or None if not specified
        """
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        if robots_url not in self._robots_cache:
            self.can_fetch(url)  # This will populate the cache
        
        robot_parser = self._robots_cache.get(robots_url)
        if robot_parser:
            try:
                # Get crawl delay for our user agent
                delay = robot_parser.crawl_delay(self.user_agent)
                if delay is not None:
                    self.logger.debug(f"Crawl delay for {parsed_url.netloc}: {delay}s")
                return delay
            except AttributeError:
                # crawl_delay might not be available in older Python versions
                self.logger.debug("Crawl delay information not available")
                return None
        
        return None
    
    def clear_cache(self) -> None:
        """Clear the robots.txt cache and request time tracking."""
        self._robots_cache.clear()
        self._last_request_time.clear()
        self.logger.info("Cleared robots.txt cache and request time tracking")
    
    def set_user_agent(self, user_agent: str) -> None:
        """
        Update the user agent string.
        
        Args:
            user_agent: New user agent string
        """
        self.user_agent = user_agent
        # Clear robots cache as permissions might change with different user agent
        self._robots_cache.clear()
        self.logger.info(f"Updated user agent to: {user_agent}")