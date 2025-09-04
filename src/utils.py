"""
Utility functions for ScraperEtico - Ethical Web Scraping utilities

This module provides essential utility functions for:
- URL validation and parsing
- Colored terminal logging output
- Domain extraction and URL manipulation
- Safe URL joining operations
- Data formatting and export helpers
"""

import re
import json
import csv
from typing import Optional, Dict, Any, List, Union, Tuple
from urllib.parse import urlparse, urljoin, urlunparse, quote, unquote
from pathlib import Path
import logging


# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'      # Allowed actions
    RED = '\033[91m'        # Blocked/error actions
    YELLOW = '\033[93m'     # Warnings
    BLUE = '\033[94m'       # Info
    CYAN = '\033[96m'       # Headers/titles
    WHITE = '\033[97m'      # Default text
    BOLD = '\033[1m'        # Bold text
    RESET = '\033[0m'       # Reset to default


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate if a URL is properly formatted and accessible.
    
    Args:
        url: The URL string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if URL is valid, False otherwise
        - error_message: Description of validation error, None if valid
        
    Examples:
        >>> validate_url("https://example.com")
        (True, None)
        >>> validate_url("invalid-url")
        (False, "Invalid URL scheme")
    """
    if not isinstance(url, str):
        return False, "URL must be a string"
    
    if not url.strip():
        return False, "URL cannot be empty"
    
    try:
        parsed = urlparse(url.strip())
        
        # Check for required components
        if not parsed.scheme:
            return False, "Invalid URL scheme"
        
        if not parsed.netloc:
            return False, "Invalid URL domain"
        
        # Check for valid schemes
        valid_schemes = {'http', 'https', 'ftp', 'ftps'}
        if parsed.scheme.lower() not in valid_schemes:
            return False, f"Unsupported URL scheme: {parsed.scheme}"
        
        # Basic domain validation
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        
        # Extract domain without port
        domain = parsed.netloc.split(':')[0]
        if not domain_pattern.match(domain):
            # Allow localhost and IP addresses
            if domain not in ('localhost', '127.0.0.1') and not _is_valid_ip(domain):
                return False, "Invalid domain format"
        
        return True, None
        
    except Exception as e:
        return False, f"URL parsing error: {str(e)}"


def _is_valid_ip(ip: str) -> bool:
    """
    Check if string is a valid IP address.
    
    Args:
        ip: IP address string to validate
        
    Returns:
        True if valid IP address, False otherwise
    """
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if not part.isdigit():
                return False
            num = int(part)
            if num < 0 or num > 255:
                return False
        
        return True
    except:
        return False


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: The URL to extract domain from
        
    Returns:
        Domain string or None if invalid URL
        
    Examples:
        >>> extract_domain("https://example.com/path")
        'example.com'
        >>> extract_domain("https://subdomain.example.com:8080/path")
        'subdomain.example.com'
    """
    try:
        parsed = urlparse(url.strip())
        if parsed.netloc:
            # Remove port if present
            return parsed.netloc.split(':')[0]
        return None
    except:
        return None


def extract_base_domain(url: str) -> Optional[str]:
    """
    Extract base domain (without subdomains) from URL.
    
    Args:
        url: The URL to extract base domain from
        
    Returns:
        Base domain string or None if invalid URL
        
    Examples:
        >>> extract_base_domain("https://www.subdomain.example.com")
        'example.com'
        >>> extract_base_domain("https://api.github.com")
        'github.com'
    """
    domain = extract_domain(url)
    if not domain:
        return None
    
    try:
        parts = domain.split('.')
        if len(parts) >= 2:
            # Return last two parts for base domain
            return '.'.join(parts[-2:])
        return domain
    except:
        return None


def safe_urljoin(base: str, url: str) -> Optional[str]:
    """
    Safely join a base URL with a relative URL.
    
    Args:
        base: Base URL
        url: URL to join (can be relative or absolute)
        
    Returns:
        Joined URL or None if joining failed
        
    Examples:
        >>> safe_urljoin("https://example.com/", "/path")
        'https://example.com/path'
        >>> safe_urljoin("https://example.com/dir/", "../other")
        'https://example.com/other'
    """
    try:
        if not base or not url:
            return None
        
        # If url is already absolute, return it
        if urlparse(url).netloc:
            return url
        
        joined = urljoin(base.strip(), url.strip())
        
        # Validate the result
        is_valid, _ = validate_url(joined)
        return joined if is_valid else None
        
    except Exception:
        return None


def normalize_url(url: str) -> Optional[str]:
    """
    Normalize URL by removing fragments, sorting query parameters, etc.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL or None if invalid
        
    Examples:
        >>> normalize_url("https://example.com/path?b=2&a=1#fragment")
        'https://example.com/path?a=1&b=2'
    """
    try:
        parsed = urlparse(url.strip())
        
        # Remove fragment
        normalized = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        
        # Sort query parameters if present
        if parsed.query:
            from urllib.parse import parse_qs, urlencode
            query_dict = parse_qs(parsed.query, keep_blank_values=True)
            # Sort and rebuild query string
            sorted_query = urlencode(sorted(query_dict.items()), doseq=True)
            normalized = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path,
                parsed.params,
                sorted_query,
                ''
            ))
        
        return normalized
        
    except Exception:
        return None


def format_log_message(message: str, level: str = "info", color: bool = True) -> str:
    """
    Format log messages with optional colors for terminal output.
    
    Args:
        message: The message to format
        level: Log level ('success'/'allowed', 'error'/'blocked', 'warning', 'info')
        color: Whether to include color codes
        
    Returns:
        Formatted message string
        
    Examples:
        >>> format_log_message("Access allowed", "success")
        '✅ Access allowed'
        >>> format_log_message("Access blocked", "error")
        '❌ Access blocked'
    """
    level = level.lower()
    
    # Map levels to symbols and colors
    level_map = {
        'success': ('✅', Colors.GREEN),
        'allowed': ('✅', Colors.GREEN),
        'error': ('❌', Colors.RED),
        'blocked': ('❌', Colors.RED),
        'warning': ('⚠️ ', Colors.YELLOW),
        'info': ('ℹ️ ', Colors.BLUE),
        'debug': ('🔍', Colors.CYAN)
    }
    
    symbol, color_code = level_map.get(level, ('•', Colors.WHITE))
    
    if color:
        return f"{color_code}{symbol} {message}{Colors.RESET}"
    else:
        return f"{symbol} {message}"


def log_url_status(url: str, allowed: bool, reason: str = "", color: bool = True) -> str:
    """
    Format URL access status for logging.
    
    Args:
        url: The URL being accessed
        allowed: Whether access is allowed
        reason: Optional reason for the status
        color: Whether to include color codes
        
    Returns:
        Formatted status message
        
    Examples:
        >>> log_url_status("https://example.com", True, "robots.txt allows")
        '✅ https://example.com - robots.txt allows'
        >>> log_url_status("https://example.com/admin", False, "blocked by robots.txt")
        '❌ https://example.com/admin - blocked by robots.txt'
    """
    level = "allowed" if allowed else "blocked"
    base_message = url
    
    if reason:
        base_message += f" - {reason}"
    
    return format_log_message(base_message, level, color)


def format_request_summary(
    url: str, 
    status_code: int, 
    response_size: int, 
    duration: float,
    color: bool = True
) -> str:
    """
    Format HTTP request summary for logging.
    
    Args:
        url: The requested URL
        status_code: HTTP status code
        response_size: Response size in bytes
        duration: Request duration in seconds
        color: Whether to include color codes
        
    Returns:
        Formatted request summary
        
    Examples:
        >>> format_request_summary("https://example.com", 200, 1024, 0.5)
        '✅ 200 | 1.0KB | 0.50s | https://example.com'
    """
    # Determine status level based on status code
    if 200 <= status_code < 300:
        level = "success"
    elif 400 <= status_code < 500:
        level = "warning"
    else:
        level = "error"
    
    # Format response size
    size_str = format_bytes(response_size)
    
    # Format duration
    duration_str = f"{duration:.2f}s"
    
    message = f"{status_code} | {size_str} | {duration_str} | {url}"
    
    return format_log_message(message, level, color)


def format_bytes(bytes_count: int) -> str:
    """
    Format byte count into human-readable string.
    
    Args:
        bytes_count: Number of bytes
        
    Returns:
        Formatted byte string
        
    Examples:
        >>> format_bytes(1024)
        '1.0KB'
        >>> format_bytes(1048576)
        '1.0MB'
    """
    if bytes_count == 0:
        return "0B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(bytes_count)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f}{units[unit_index]}"


def export_to_json(
    data: List[Dict[str, Any]], 
    filepath: Union[str, Path],
    indent: int = 2,
    ensure_ascii: bool = False
) -> bool:
    """
    Export data to JSON file.
    
    Args:
        data: List of dictionaries to export
        filepath: Path to output JSON file
        indent: JSON indentation (default: 2)
        ensure_ascii: Whether to ensure ASCII encoding
        
    Returns:
        True if export successful, False otherwise
        
    Examples:
        >>> data = [{"url": "https://example.com", "status": 200}]
        >>> export_to_json(data, "results.json")
        True
    """
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, default=str)
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to export JSON to {filepath}: {e}")
        return False


def export_to_csv(
    data: List[Dict[str, Any]], 
    filepath: Union[str, Path],
    fieldnames: Optional[List[str]] = None
) -> bool:
    """
    Export data to CSV file.
    
    Args:
        data: List of dictionaries to export
        filepath: Path to output CSV file
        fieldnames: CSV column names (auto-detected if None)
        
    Returns:
        True if export successful, False otherwise
        
    Examples:
        >>> data = [{"url": "https://example.com", "status": 200}]
        >>> export_to_csv(data, "results.csv")
        True
    """
    try:
        if not data:
            return False
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Auto-detect fieldnames if not provided
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to export CSV to {filepath}: {e}")
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for filesystem
        
    Examples:
        >>> sanitize_filename("https://example.com/path?query=1")
        'https_example.com_path_query_1'
    """
    # Replace invalid characters with underscores
    invalid_chars = r'<>:"/\\|?*'
    sanitized = filename
    
    for char in invalid_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Replace multiple underscores with single
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip('_.')
    
    # Ensure filename isn't too long
    max_length = 255
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('_.')
    
    return sanitized or 'unnamed_file'


def parse_robots_delay(robots_content: str, user_agent: str = "*") -> Optional[float]:
    """
    Parse crawl delay from robots.txt content.
    
    Args:
        robots_content: Raw robots.txt content
        user_agent: User agent to check for (default: "*")
        
    Returns:
        Crawl delay in seconds or None if not found
        
    Examples:
        >>> content = "User-agent: *\\nCrawl-delay: 1"
        >>> parse_robots_delay(content)
        1.0
    """
    try:
        lines = robots_content.split('\n')
        current_user_agent = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.lower().startswith('user-agent:'):
                current_user_agent = line.split(':', 1)[1].strip()
            
            elif line.lower().startswith('crawl-delay:'):
                # Check if this applies to our user agent
                if (current_user_agent == user_agent or 
                    current_user_agent == '*' or 
                    user_agent == '*'):
                    
                    delay_str = line.split(':', 1)[1].strip()
                    try:
                        return float(delay_str)
                    except ValueError:
                        continue
        
        return None
        
    except Exception:
        return None


def get_file_extension_from_url(url: str) -> Optional[str]:
    """
    Extract file extension from URL.
    
    Args:
        url: URL to extract extension from
        
    Returns:
        File extension (with dot) or None if not found
        
    Examples:
        >>> get_file_extension_from_url("https://example.com/file.pdf")
        '.pdf'
        >>> get_file_extension_from_url("https://example.com/page")
        None
    """
    try:
        parsed = urlparse(url)
        path = parsed.path
        
        if '.' in path:
            # Get the last part after the final slash
            filename = path.split('/')[-1]
            if '.' in filename:
                return '.' + filename.split('.')[-1].lower()
        
        return None
        
    except Exception:
        return None


def is_static_resource(url: str) -> bool:
    """
    Check if URL points to a static resource (CSS, JS, images, etc.).
    
    Args:
        url: URL to check
        
    Returns:
        True if URL appears to be a static resource
        
    Examples:
        >>> is_static_resource("https://example.com/style.css")
        True
        >>> is_static_resource("https://example.com/page.html")
        False
    """
    static_extensions = {
        '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
        '.woff', '.woff2', '.ttf', '.eot', '.mp4', '.mp3', '.pdf', '.zip',
        '.webp', '.bmp', '.tiff', '.avi', '.mov', '.wmv', '.flv'
    }
    
    extension = get_file_extension_from_url(url)
    return extension in static_extensions if extension else False


def create_logger_with_colors(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Create a logger with colored output formatting.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger with colored formatting
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler with colored formatting
    handler = logging.StreamHandler()
    
    class ColoredFormatter(logging.Formatter):
        """Custom formatter with color support."""
        
        COLORS = {
            'DEBUG': Colors.CYAN,
            'INFO': Colors.BLUE,
            'WARNING': Colors.YELLOW,
            'ERROR': Colors.RED,
            'CRITICAL': Colors.RED + Colors.BOLD
        }
        
        def format(self, record):
            # Color the level name
            level_color = self.COLORS.get(record.levelname, Colors.WHITE)
            record.levelname = f"{level_color}{record.levelname}{Colors.RESET}"
            
            # Format timestamp
            record.asctime = self.formatTime(record, self.datefmt)
            
            return super().format(record)
    
    formatter = ColoredFormatter(
        f'{Colors.CYAN}%(asctime)s{Colors.RESET} - '
        f'{Colors.WHITE}%(name)s{Colors.RESET} - '
        f'%(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger