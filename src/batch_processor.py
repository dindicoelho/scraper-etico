"""
Batch Processor for ScraperEtico - Advanced batch processing with export functionality

This module provides comprehensive batch processing capabilities for ethical web scraping
with robots.txt compliance, concurrent processing, progress tracking, resume functionality,
and detailed reporting with export options.
"""

import json
import csv
import pickle
import time
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable, Tuple
from urllib.parse import urlparse
import asyncio
from collections import defaultdict, Counter

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Fallback progress indicator
    class tqdm:
        def __init__(self, iterable=None, total=None, desc="", **kwargs):
            self.iterable = iterable
            self.total = total or (len(iterable) if iterable else 0)
            self.desc = desc
            self.n = 0
            
        def __iter__(self):
            for item in self.iterable:
                yield item
                self.update(1)
                
        def update(self, n=1):
            self.n += n
            if self.total > 0:
                percent = (self.n / self.total) * 100
                print(f"\r{self.desc}: {self.n}/{self.total} ({percent:.1f}%)", end="", flush=True)
                
        def close(self):
            print()  # New line after progress
            
        def __enter__(self):
            return self
            
        def __exit__(self, *args):
            self.close()

# Handle both relative and absolute imports
try:
    from .scraper_etico import ScraperEtico
    from .analyzer import RobotsAnalyzer, RobotsAnalysisReport
except ImportError:
    # Fallback for direct execution
    from scraper_etico import ScraperEtico
    from analyzer import RobotsAnalyzer, RobotsAnalysisReport


@dataclass
class BatchResult:
    """Container for individual URL processing results."""
    
    url: str
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Scraping results
    status_code: Optional[int] = None
    response_size: Optional[int] = None
    response_time: Optional[float] = None
    robots_allowed: Optional[bool] = None
    crawl_delay: Optional[float] = None
    
    # Robots.txt analysis results
    robots_analysis: Optional[RobotsAnalysisReport] = None
    
    # Error information
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    
    # Additional metadata
    domain: str = field(init=False)
    processed_by_thread: Optional[str] = None
    
    def __post_init__(self):
        """Extract domain from URL."""
        self.domain = urlparse(self.url).netloc


@dataclass
class BatchJobState:
    """State container for batch job persistence and resuming."""
    
    job_id: str
    urls: List[str] = field(default_factory=list)
    completed_urls: set = field(default_factory=set)
    failed_urls: set = field(default_factory=set)
    results: List[BatchResult] = field(default_factory=list)
    
    # Job metadata
    start_time: Optional[datetime] = None
    last_save_time: Optional[datetime] = None
    total_urls: int = 0
    processed_count: int = 0
    
    # Configuration
    max_workers: int = 5
    delay_per_domain: float = 1.0
    analyze_robots: bool = True
    
    @property
    def completion_percentage(self) -> float:
        """Calculate job completion percentage."""
        if self.total_urls == 0:
            return 0.0
        return (self.processed_count / self.total_urls) * 100
    
    @property
    def remaining_urls(self) -> List[str]:
        """Get list of URLs still to be processed."""
        return [url for url in self.urls if url not in self.completed_urls and url not in self.failed_urls]


class BatchProcessor:
    """
    Advanced batch processor for ethical web scraping with comprehensive features.
    
    This class provides:
    - Concurrent processing with configurable thread limits
    - Rate limiting respecting robots.txt crawl delays
    - Progress tracking with visual progress bars
    - Resume functionality for interrupted jobs
    - Export to CSV and JSON formats
    - Detailed summary reports and statistics
    - Integration with ScraperEtico and RobotsAnalyzer
    
    Attributes:
        scraper (ScraperEtico): Ethical web scraper instance
        analyzer (RobotsAnalyzer): Robots.txt analyzer instance
        logger (logging.Logger): Logger instance for detailed logging
        state_dir (Path): Directory for saving job state files
    """
    
    def __init__(
        self,
        scraper: Optional[ScraperEtico] = None,
        analyzer: Optional[RobotsAnalyzer] = None,
        state_dir: Union[str, Path] = "./batch_states",
        log_level: int = logging.INFO
    ):
        """
        Initialize the BatchProcessor.
        
        Args:
            scraper: ScraperEtico instance (creates default if None)
            analyzer: RobotsAnalyzer instance (creates default if None)
            state_dir: Directory to store job state files
            log_level: Logging level (default: logging.INFO)
        """
        # Initialize scraper and analyzer
        self.scraper = scraper or ScraperEtico()
        self.analyzer = analyzer or RobotsAnalyzer()
        
        # Setup state directory
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = self._setup_logger(log_level)
        
        # Thread safety
        self._lock = threading.Lock()
        self._domain_locks: Dict[str, threading.Lock] = {}
        self._domain_last_request: Dict[str, float] = {}
        
        self.logger.info(f"BatchProcessor initialized with state dir: {self.state_dir}")
    
    def _setup_logger(self, log_level: int) -> logging.Logger:
        """Setup logger with timestamp formatting."""
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
    
    def _get_domain_lock(self, domain: str) -> threading.Lock:
        """Get or create a lock for the specified domain."""
        with self._lock:
            if domain not in self._domain_locks:
                self._domain_locks[domain] = threading.Lock()
            return self._domain_locks[domain]
    
    def _apply_domain_rate_limit(self, domain: str, custom_delay: Optional[float] = None) -> None:
        """Apply rate limiting per domain with thread safety."""
        delay = custom_delay or self.scraper.default_delay
        
        with self._get_domain_lock(domain):
            if domain in self._domain_last_request:
                elapsed = time.time() - self._domain_last_request[domain]
                if elapsed < delay:
                    sleep_time = delay - elapsed
                    time.sleep(sleep_time)
            
            self._domain_last_request[domain] = time.time()
    
    def _process_single_url(
        self,
        url: str,
        analyze_robots: bool = True,
        custom_delay: Optional[float] = None
    ) -> BatchResult:
        """
        Process a single URL with full error handling.
        
        Args:
            url: URL to process
            analyze_robots: Whether to perform robots.txt analysis
            custom_delay: Custom delay for this URL
            
        Returns:
            BatchResult containing all processing results
        """
        result = BatchResult(url=url, success=False)
        result.processed_by_thread = threading.current_thread().name
        
        try:
            domain = urlparse(url).netloc
            
            # Apply domain-specific rate limiting
            effective_delay = custom_delay
            if effective_delay is None and analyze_robots:
                # Check for crawl delay from robots.txt
                crawl_delay = self.scraper.get_crawl_delay(url)
                if crawl_delay is not None:
                    effective_delay = crawl_delay
                    result.crawl_delay = crawl_delay
            
            self._apply_domain_rate_limit(domain, effective_delay)
            
            # Perform web scraping
            start_time = time.time()
            response = self.scraper.get(url, custom_delay=effective_delay)
            response_time = time.time() - start_time
            
            result.response_time = response_time
            
            if response is not None:
                result.success = True
                result.status_code = response.status_code
                result.response_size = len(response.content)
                result.robots_allowed = True
                
                self.logger.info(f"Successfully processed: {url} "
                               f"(status: {response.status_code}, "
                               f"size: {result.response_size} bytes, "
                               f"time: {response_time:.2f}s)")
            else:
                # Check if robots.txt disallowed the request
                robots_allowed = self.scraper.can_fetch(url)
                result.robots_allowed = robots_allowed
                
                if not robots_allowed:
                    result.error_type = "robots_disallowed"
                    result.error_message = "Access disallowed by robots.txt"
                else:
                    result.error_type = "request_failed"
                    result.error_message = "HTTP request failed"
                
                self.logger.warning(f"Failed to process: {url} - {result.error_message}")
            
            # Perform robots.txt analysis if requested
            if analyze_robots:
                try:
                    robots_report = self.analyzer.analyze_url(url)
                    if robots_report:
                        result.robots_analysis = robots_report
                        self.logger.debug(f"Robots.txt analysis completed for: {url}")
                    else:
                        self.logger.debug(f"No robots.txt found for: {url}")
                except Exception as e:
                    self.logger.warning(f"Robots.txt analysis failed for {url}: {e}")
            
        except Exception as e:
            result.error_type = type(e).__name__
            result.error_message = str(e)
            self.logger.error(f"Unexpected error processing {url}: {e}")
        
        return result
    
    def process_batch(
        self,
        urls: List[str],
        job_id: Optional[str] = None,
        max_workers: int = 5,
        analyze_robots: bool = True,
        custom_delay: Optional[float] = None,
        show_progress: bool = True,
        save_state_interval: int = 10
    ) -> BatchJobState:
        """
        Process a batch of URLs with concurrent execution.
        
        Args:
            urls: List of URLs to process
            job_id: Unique job identifier (auto-generated if None)
            max_workers: Maximum number of concurrent threads
            analyze_robots: Whether to perform robots.txt analysis
            custom_delay: Custom delay between requests
            show_progress: Whether to show progress bar
            save_state_interval: Save state every N processed URLs
            
        Returns:
            BatchJobState containing all results and metadata
        """
        # Generate job ID if not provided
        if job_id is None:
            job_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize job state
        job_state = BatchJobState(
            job_id=job_id,
            urls=list(urls),
            total_urls=len(urls),
            start_time=datetime.now(),
            max_workers=max_workers,
            delay_per_domain=custom_delay or self.scraper.default_delay,
            analyze_robots=analyze_robots
        )
        
        self.logger.info(f"Starting batch job '{job_id}' with {len(urls)} URLs, "
                        f"{max_workers} workers, analyze_robots={analyze_robots}")
        
        # Initialize progress bar
        if show_progress and TQDM_AVAILABLE:
            progress_bar = tqdm(total=len(urls), desc=f"Processing {job_id}", unit="URL")
        else:
            progress_bar = None
        
        try:
            # Process URLs concurrently
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all jobs
                future_to_url = {
                    executor.submit(
                        self._process_single_url,
                        url,
                        analyze_robots,
                        custom_delay
                    ): url for url in urls
                }
                
                # Process completed futures
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        result = future.result()
                        job_state.results.append(result)
                        
                        if result.success:
                            job_state.completed_urls.add(url)
                        else:
                            job_state.failed_urls.add(url)
                        
                        job_state.processed_count += 1
                        
                        # Update progress bar
                        if progress_bar:
                            progress_bar.update(1)
                            progress_bar.set_postfix({
                                'Success': len(job_state.completed_urls),
                                'Failed': len(job_state.failed_urls)
                            })
                        
                        # Save state periodically
                        if job_state.processed_count % save_state_interval == 0:
                            self.save_job_state(job_state)
                            
                    except Exception as e:
                        self.logger.error(f"Error processing future for {url}: {e}")
                        job_state.failed_urls.add(url)
                        job_state.processed_count += 1
                        
                        if progress_bar:
                            progress_bar.update(1)
        
        finally:
            if progress_bar:
                progress_bar.close()
        
        # Final state save
        job_state.last_save_time = datetime.now()
        self.save_job_state(job_state)
        
        # Log completion summary
        success_count = len(job_state.completed_urls)
        failure_count = len(job_state.failed_urls)
        total_time = (datetime.now() - job_state.start_time).total_seconds()
        
        self.logger.info(f"Batch job '{job_id}' completed: "
                        f"{success_count} successful, {failure_count} failed, "
                        f"total time: {total_time:.2f}s")
        
        return job_state
    
    def resume_batch_job(self, job_id: str, **kwargs) -> BatchJobState:
        """
        Resume an interrupted batch job.
        
        Args:
            job_id: Job identifier to resume
            **kwargs: Additional arguments to override saved configuration
            
        Returns:
            Updated BatchJobState with new results
        """
        # Load existing job state
        job_state = self.load_job_state(job_id)
        if job_state is None:
            raise ValueError(f"Job state not found for job_id: {job_id}")
        
        remaining_urls = job_state.remaining_urls
        if not remaining_urls:
            self.logger.info(f"Job '{job_id}' is already complete")
            return job_state
        
        self.logger.info(f"Resuming job '{job_id}' with {len(remaining_urls)} remaining URLs")
        
        # Override configuration if provided
        max_workers = kwargs.get('max_workers', job_state.max_workers)
        analyze_robots = kwargs.get('analyze_robots', job_state.analyze_robots)
        custom_delay = kwargs.get('custom_delay', job_state.delay_per_domain)
        show_progress = kwargs.get('show_progress', True)
        save_state_interval = kwargs.get('save_state_interval', 10)
        
        # Process remaining URLs
        remaining_job = self.process_batch(
            remaining_urls,
            job_id=f"{job_id}_resume_{datetime.now().strftime('%H%M%S')}",
            max_workers=max_workers,
            analyze_robots=analyze_robots,
            custom_delay=custom_delay,
            show_progress=show_progress,
            save_state_interval=save_state_interval
        )
        
        # Merge results
        job_state.results.extend(remaining_job.results)
        job_state.completed_urls.update(remaining_job.completed_urls)
        job_state.failed_urls.update(remaining_job.failed_urls)
        job_state.processed_count = len(job_state.results)
        job_state.last_save_time = datetime.now()
        
        # Save final state
        self.save_job_state(job_state)
        
        return job_state
    
    def save_job_state(self, job_state: BatchJobState) -> Path:
        """
        Save job state to disk for resuming.
        
        Args:
            job_state: Job state to save
            
        Returns:
            Path to saved state file
        """
        state_file = self.state_dir / f"{job_state.job_id}.pkl"
        
        try:
            with open(state_file, 'wb') as f:
                pickle.dump(job_state, f)
            
            self.logger.debug(f"Saved job state: {state_file}")
            return state_file
            
        except Exception as e:
            self.logger.error(f"Failed to save job state: {e}")
            raise
    
    def load_job_state(self, job_id: str) -> Optional[BatchJobState]:
        """
        Load job state from disk.
        
        Args:
            job_id: Job identifier to load
            
        Returns:
            Loaded job state or None if not found
        """
        state_file = self.state_dir / f"{job_id}.pkl"
        
        if not state_file.exists():
            self.logger.warning(f"Job state file not found: {state_file}")
            return None
        
        try:
            with open(state_file, 'rb') as f:
                job_state = pickle.load(f)
            
            self.logger.debug(f"Loaded job state: {state_file}")
            return job_state
            
        except Exception as e:
            self.logger.error(f"Failed to load job state: {e}")
            return None
    
    def list_job_states(self) -> List[str]:
        """
        List all available job states.
        
        Returns:
            List of job IDs
        """
        job_ids = []
        for state_file in self.state_dir.glob("*.pkl"):
            job_id = state_file.stem
            job_ids.append(job_id)
        
        return sorted(job_ids)
    
    def export_to_csv(
        self,
        job_state: BatchJobState,
        output_file: Union[str, Path],
        include_robots_analysis: bool = True
    ) -> Path:
        """
        Export batch results to CSV format.
        
        Args:
            job_state: Job state containing results to export
            output_file: Output CSV file path
            include_robots_analysis: Whether to include robots.txt analysis data
            
        Returns:
            Path to created CSV file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        fieldnames = [
            'url', 'domain', 'success', 'timestamp', 'status_code',
            'response_size', 'response_time', 'robots_allowed', 'crawl_delay',
            'error_type', 'error_message', 'processed_by_thread'
        ]
        
        if include_robots_analysis:
            fieldnames.extend([
                'robots_file_size', 'robots_user_agents', 'robots_sitemaps',
                'robots_total_rules', 'robots_errors', 'robots_valid'
            ])
        
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in job_state.results:
                    row = {
                        'url': result.url,
                        'domain': result.domain,
                        'success': result.success,
                        'timestamp': result.timestamp.isoformat(),
                        'status_code': result.status_code,
                        'response_size': result.response_size,
                        'response_time': result.response_time,
                        'robots_allowed': result.robots_allowed,
                        'crawl_delay': result.crawl_delay,
                        'error_type': result.error_type,
                        'error_message': result.error_message,
                        'processed_by_thread': result.processed_by_thread
                    }
                    
                    if include_robots_analysis and result.robots_analysis:
                        analysis = result.robots_analysis
                        row.update({
                            'robots_file_size': analysis.file_size,
                            'robots_user_agents': len(analysis.user_agents),
                            'robots_sitemaps': len(analysis.sitemaps),
                            'robots_total_rules': (
                                analysis.statistics.get('total_allow_rules', 0) +
                                analysis.statistics.get('total_disallow_rules', 0)
                            ),
                            'robots_errors': len(analysis.errors),
                            'robots_valid': analysis.is_valid
                        })
                    
                    writer.writerow(row)
            
            self.logger.info(f"Exported {len(job_state.results)} results to CSV: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {e}")
            raise
    
    def export_to_json(
        self,
        job_state: BatchJobState,
        output_file: Union[str, Path],
        include_robots_analysis: bool = True,
        pretty: bool = True
    ) -> Path:
        """
        Export batch results to JSON format.
        
        Args:
            job_state: Job state containing results to export
            output_file: Output JSON file path
            include_robots_analysis: Whether to include robots.txt analysis data
            pretty: Whether to format JSON with indentation
            
        Returns:
            Path to created JSON file
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        def serialize_result(result: BatchResult) -> Dict[str, Any]:
            """Convert BatchResult to serializable dictionary."""
            data = asdict(result)
            
            # Convert datetime to ISO string
            data['timestamp'] = result.timestamp.isoformat()
            
            # Handle robots analysis
            if not include_robots_analysis:
                data.pop('robots_analysis', None)
            elif result.robots_analysis:
                # Convert RobotsAnalysisReport to dict
                analysis_data = asdict(result.robots_analysis)
                # Convert any datetime fields in statistics
                if 'statistics' in analysis_data:
                    stats = analysis_data['statistics']
                    for key, value in stats.items():
                        if isinstance(value, datetime):
                            stats[key] = value.isoformat()
                data['robots_analysis'] = analysis_data
            
            return data
        
        export_data = {
            'job_metadata': {
                'job_id': job_state.job_id,
                'total_urls': job_state.total_urls,
                'processed_count': job_state.processed_count,
                'success_count': len(job_state.completed_urls),
                'failure_count': len(job_state.failed_urls),
                'completion_percentage': job_state.completion_percentage,
                'start_time': job_state.start_time.isoformat() if job_state.start_time else None,
                'last_save_time': job_state.last_save_time.isoformat() if job_state.last_save_time else None,
                'configuration': {
                    'max_workers': job_state.max_workers,
                    'delay_per_domain': job_state.delay_per_domain,
                    'analyze_robots': job_state.analyze_robots
                }
            },
            'results': [serialize_result(result) for result in job_state.results]
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                if pretty:
                    json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
                else:
                    json.dump(export_data, jsonfile, ensure_ascii=False)
            
            self.logger.info(f"Exported {len(job_state.results)} results to JSON: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {e}")
            raise
    
    def generate_summary_report(self, job_state: BatchJobState) -> Dict[str, Any]:
        """
        Generate comprehensive summary report and statistics.
        
        Args:
            job_state: Job state to analyze
            
        Returns:
            Dictionary containing detailed summary and statistics
        """
        results = job_state.results
        
        if not results:
            return {
                'job_id': job_state.job_id,
                'message': 'No results to analyze'
            }
        
        # Basic statistics
        total_results = len(results)
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        success_count = len(successful_results)
        failure_count = len(failed_results)
        success_rate = (success_count / total_results) * 100 if total_results > 0 else 0
        
        # Timing statistics
        response_times = [r.response_time for r in successful_results if r.response_time is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        # Size statistics  
        response_sizes = [r.response_size for r in successful_results if r.response_size is not None]
        total_data_size = sum(response_sizes) if response_sizes else 0
        avg_response_size = total_data_size / len(response_sizes) if response_sizes else 0
        
        # Domain analysis
        domain_counter = Counter(r.domain for r in results)
        domain_success_rates = {}
        for domain in domain_counter:
            domain_results = [r for r in results if r.domain == domain]
            domain_success = sum(1 for r in domain_results if r.success)
            domain_success_rates[domain] = (domain_success / len(domain_results)) * 100
        
        # Error analysis
        error_types = Counter(r.error_type for r in failed_results if r.error_type)
        
        # Status code analysis
        status_codes = Counter(r.status_code for r in successful_results if r.status_code)
        
        # Robots.txt analysis
        robots_analysis_summary = {}
        if job_state.analyze_robots:
            robots_results = [r for r in results if r.robots_analysis is not None]
            if robots_results:
                total_robots_analyzed = len(robots_results)
                robots_with_errors = sum(1 for r in robots_results if r.robots_analysis.errors)
                
                # Crawl delay analysis
                crawl_delays = [r.crawl_delay for r in results if r.crawl_delay is not None]
                
                # Sitemap analysis
                total_sitemaps = sum(len(r.robots_analysis.sitemaps) for r in robots_results)
                
                robots_analysis_summary = {
                    'total_analyzed': total_robots_analyzed,
                    'robots_with_errors': robots_with_errors,
                    'total_sitemaps_found': total_sitemaps,
                    'crawl_delays': {
                        'count': len(crawl_delays),
                        'min': min(crawl_delays) if crawl_delays else None,
                        'max': max(crawl_delays) if crawl_delays else None,
                        'average': sum(crawl_delays) / len(crawl_delays) if crawl_delays else None
                    }
                }
        
        # Thread performance analysis
        thread_performance = {}
        if any(r.processed_by_thread for r in results):
            thread_counter = Counter(r.processed_by_thread for r in results if r.processed_by_thread)
            for thread_name, count in thread_counter.items():
                thread_results = [r for r in results if r.processed_by_thread == thread_name]
                thread_success = sum(1 for r in thread_results if r.success)
                thread_performance[thread_name] = {
                    'total_processed': count,
                    'successful': thread_success,
                    'success_rate': (thread_success / count) * 100 if count > 0 else 0
                }
        
        # Job timing
        job_duration = None
        if job_state.start_time and job_state.last_save_time:
            duration = job_state.last_save_time - job_state.start_time
            job_duration = {
                'total_seconds': duration.total_seconds(),
                'human_readable': str(duration).split('.')[0]  # Remove microseconds
            }
        
        # Compile comprehensive report
        report = {
            'job_metadata': {
                'job_id': job_state.job_id,
                'start_time': job_state.start_time.isoformat() if job_state.start_time else None,
                'last_save_time': job_state.last_save_time.isoformat() if job_state.last_save_time else None,
                'duration': job_duration,
                'configuration': {
                    'max_workers': job_state.max_workers,
                    'delay_per_domain': job_state.delay_per_domain,
                    'analyze_robots': job_state.analyze_robots
                }
            },
            'overall_statistics': {
                'total_urls': job_state.total_urls,
                'processed_count': job_state.processed_count,
                'successful': success_count,
                'failed': failure_count,
                'success_rate_percent': round(success_rate, 2),
                'completion_percentage': round(job_state.completion_percentage, 2)
            },
            'performance_statistics': {
                'response_time': {
                    'average_seconds': round(avg_response_time, 3),
                    'min_seconds': round(min_response_time, 3),
                    'max_seconds': round(max_response_time, 3),
                    'total_samples': len(response_times)
                },
                'data_transfer': {
                    'total_bytes': total_data_size,
                    'total_mb': round(total_data_size / (1024 * 1024), 2),
                    'average_bytes_per_response': round(avg_response_size, 0),
                    'total_responses': len(response_sizes)
                }
            },
            'domain_analysis': {
                'total_domains': len(domain_counter),
                'most_common_domains': domain_counter.most_common(10),
                'domain_success_rates': {
                    domain: round(rate, 2) 
                    for domain, rate in sorted(domain_success_rates.items(), key=lambda x: x[1], reverse=True)[:10]
                }
            },
            'error_analysis': {
                'total_errors': failure_count,
                'error_types': dict(error_types.most_common(10)),
                'error_rate_percent': round((failure_count / total_results) * 100, 2) if total_results > 0 else 0
            },
            'http_status_analysis': {
                'status_code_distribution': dict(status_codes.most_common(10)),
                'unique_status_codes': len(status_codes)
            },
            'robots_analysis': robots_analysis_summary,
            'thread_performance': thread_performance
        }
        
        self.logger.info(f"Generated summary report for job '{job_state.job_id}': "
                        f"{success_count}/{total_results} successful ({success_rate:.1f}%)")
        
        return report
    
    def print_summary_report(self, job_state: BatchJobState) -> None:
        """
        Print a formatted summary report to console.
        
        Args:
            job_state: Job state to report on
        """
        report = self.generate_summary_report(job_state)
        
        print("\n" + "=" * 80)
        print(f"BATCH PROCESSING SUMMARY REPORT - JOB: {report['job_metadata']['job_id']}")
        print("=" * 80)
        
        # Job metadata
        meta = report['job_metadata']
        if meta['start_time']:
            print(f"Start Time: {meta['start_time']}")
        if meta['duration']:
            print(f"Duration: {meta['duration']['human_readable']}")
        
        config = meta['configuration']
        print(f"Configuration: {config['max_workers']} workers, "
              f"{config['delay_per_domain']}s delay, "
              f"robots analysis: {config['analyze_robots']}")
        
        # Overall statistics
        overall = report['overall_statistics']
        print(f"\nOVERALL RESULTS:")
        print(f"  Total URLs: {overall['total_urls']}")
        print(f"  Processed: {overall['processed_count']}")
        print(f"  Successful: {overall['successful']} ({overall['success_rate_percent']}%)")
        print(f"  Failed: {overall['failed']}")
        print(f"  Completion: {overall['completion_percentage']}%")
        
        # Performance
        perf = report['performance_statistics']
        print(f"\nPERFORMANCE:")
        if perf['response_time']['total_samples'] > 0:
            print(f"  Avg Response Time: {perf['response_time']['average_seconds']}s")
            print(f"  Min/Max Response Time: {perf['response_time']['min_seconds']}s / {perf['response_time']['max_seconds']}s")
        
        if perf['data_transfer']['total_responses'] > 0:
            print(f"  Total Data: {perf['data_transfer']['total_mb']} MB")
            print(f"  Avg Response Size: {perf['data_transfer']['average_bytes_per_response']} bytes")
        
        # Domain analysis
        domain = report['domain_analysis']
        print(f"\nDOMAIN ANALYSIS:")
        print(f"  Unique Domains: {domain['total_domains']}")
        if domain['most_common_domains']:
            print("  Most Common Domains:")
            for dom, count in domain['most_common_domains'][:5]:
                success_rate = domain['domain_success_rates'].get(dom, 0)
                print(f"    {dom}: {count} URLs ({success_rate:.1f}% success)")
        
        # Error analysis
        if report['error_analysis']['total_errors'] > 0:
            error = report['error_analysis']
            print(f"\nERROR ANALYSIS:")
            print(f"  Total Errors: {error['total_errors']} ({error['error_rate_percent']}%)")
            if error['error_types']:
                print("  Error Types:")
                for error_type, count in list(error['error_types'].items())[:5]:
                    print(f"    {error_type}: {count}")
        
        # Robots analysis
        if report['robots_analysis']:
            robots = report['robots_analysis']
            print(f"\nROBOTS.TXT ANALYSIS:")
            print(f"  Files Analyzed: {robots['total_analyzed']}")
            print(f"  Files with Errors: {robots['robots_with_errors']}")
            print(f"  Sitemaps Found: {robots['total_sitemaps_found']}")
            
            crawl_delays = robots['crawl_delays']
            if crawl_delays['count'] > 0:
                print(f"  Crawl Delays: {crawl_delays['count']} domains")
                print(f"    Average: {crawl_delays['average']:.1f}s")
                print(f"    Range: {crawl_delays['min']}s - {crawl_delays['max']}s")
        
        print("=" * 80)
    
    def cleanup_old_states(self, max_age_days: int = 30) -> int:
        """
        Clean up old job state files.
        
        Args:
            max_age_days: Maximum age of state files to keep
            
        Returns:
            Number of files cleaned up
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        cleaned_count = 0
        
        for state_file in self.state_dir.glob("*.pkl"):
            try:
                file_mtime = datetime.fromtimestamp(state_file.stat().st_mtime)
                if file_mtime < cutoff_date:
                    state_file.unlink()
                    cleaned_count += 1
                    self.logger.debug(f"Cleaned up old state file: {state_file}")
            except Exception as e:
                self.logger.warning(f"Error cleaning up state file {state_file}: {e}")
        
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old state files")
        
        return cleaned_count


# Convenience functions for quick usage

def quick_batch_process(
    urls: List[str],
    output_dir: str = "./batch_results",
    max_workers: int = 5,
    analyze_robots: bool = True,
    export_formats: List[str] = ['csv', 'json']
) -> BatchJobState:
    """
    Convenience function for quick batch processing with exports.
    
    Args:
        urls: List of URLs to process
        output_dir: Directory to save results
        max_workers: Number of concurrent workers
        analyze_robots: Whether to analyze robots.txt
        export_formats: List of export formats ('csv', 'json')
        
    Returns:
        Completed BatchJobState
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize processor
    processor = BatchProcessor()
    
    # Process batch
    job_state = processor.process_batch(
        urls=urls,
        max_workers=max_workers,
        analyze_robots=analyze_robots
    )
    
    # Export results
    base_filename = f"{job_state.job_id}"
    
    if 'csv' in export_formats:
        csv_file = output_path / f"{base_filename}.csv"
        processor.export_to_csv(job_state, csv_file)
    
    if 'json' in export_formats:
        json_file = output_path / f"{base_filename}.json"
        processor.export_to_json(job_state, json_file)
    
    # Print summary
    processor.print_summary_report(job_state)
    
    return job_state


if __name__ == "__main__":
    # Example usage
    test_urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/404",
        "https://example.com",
        "https://github.com"
    ]
    
    # Quick batch processing
    result = quick_batch_process(
        urls=test_urls,
        max_workers=3,
        analyze_robots=True,
        export_formats=['csv', 'json']
    )
    
    print(f"\nBatch processing completed. Job ID: {result.job_id}")