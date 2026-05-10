"""
Log Parser Module
Parses and analyzes system log entries
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class LogParser:
    """
    Parses system log entries and extracts relevant information
    """
    
    # Pattern for syslog format
    SYSLOG_PATTERN = re.compile(
        r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+'
        r'(?P<hostname>\S+)\s+'
        r'(?P<process>\w+)(?:\[(?P<pid>\d+)\])?:\s+'
        r'(?P<message>.*)'
    )
    
    # Pattern for auth.log format
    AUTH_PATTERN = re.compile(
        r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+'
        r'(?P<hostname>\S+)\s+'
        r'(?P<process>\S+)(?:\[(?P<pid>\d+)\])?:\s+'
        r'(?P<message>.*)'
    )
    
    # Error and warning keywords
    ERROR_KEYWORDS = [
        'ERROR', 'FATAL', 'CRITICAL', 'CRIT', 'FAILED', 'FAIL',
        'EXCEPTION', 'PANIC', 'EMERGENCY', 'EMERG', 'ALERT'
    ]
    
    WARNING_KEYWORDS = [
        'WARNING', 'WARN', 'NOTICE', 'INFO', 'Deprecated'
    ]
    
    # Common patterns to look for
    FAILURE_PATTERNS = {
        'failed_login': re.compile(r'(Failed password|authentication failure|invalid user)', re.IGNORECASE),
        'connection_refused': re.compile(r'(Connection refused|connection timeout)', re.IGNORECASE),
        'permission_denied': re.compile(r'(Permission denied|access denied)', re.IGNORECASE),
        'service_failed': re.compile(r'(service failed|service stopped|service crashed)', re.IGNORECASE),
        'out_of_memory': re.compile(r'(Out of memory|OOM)', re.IGNORECASE),
        'disk_full': re.compile(r'(No space left|disk full)', re.IGNORECASE),
        'segmentation_fault': re.compile(r'(Segmentation fault|SIGSEGV)', re.IGNORECASE),
    }
    
    @classmethod
    def parse_syslog_line(cls, line: str) -> Optional[Dict]:
        """
        Parse a syslog formatted line
        
        Args:
            line (str): Log line to parse
            
        Returns:
            dict: Parsed log data or None if parsing failed
        """
        try:
            match = cls.SYSLOG_PATTERN.match(line)
            if not match:
                return None
            
            groups = match.groupdict()
            
            return {
                'timestamp': groups.get('timestamp'),
                'hostname': groups.get('hostname'),
                'process': groups.get('process'),
                'pid': groups.get('pid'),
                'message': groups.get('message'),
                'raw_line': line
            }
        except Exception as e:
            logger.error(f"Error parsing syslog line: {e}")
            return None
    
    @classmethod
    def parse_auth_line(cls, line: str) -> Optional[Dict]:
        """
        Parse an auth.log formatted line
        
        Args:
            line (str): Log line to parse
            
        Returns:
            dict: Parsed log data or None if parsing failed
        """
        try:
            match = cls.AUTH_PATTERN.match(line)
            if not match:
                return None
            
            groups = match.groupdict()
            
            return {
                'timestamp': groups.get('timestamp'),
                'hostname': groups.get('hostname'),
                'process': groups.get('process'),
                'pid': groups.get('pid'),
                'message': groups.get('message'),
                'raw_line': line
            }
        except Exception as e:
            logger.error(f"Error parsing auth log line: {e}")
            return None
    
    @classmethod
    def determine_level(cls, line: str) -> str:
        """
        Determine log level (ERROR, WARNING, INFO)
        
        Args:
            line (str): Log message
            
        Returns:
            str: Log level
        """
        line_upper = line.upper()
        
        for keyword in cls.ERROR_KEYWORDS:
            if keyword in line_upper:
                return 'ERROR'
        
        for keyword in cls.WARNING_KEYWORDS:
            if keyword in line_upper:
                return 'WARNING'
        
        return 'INFO'
    
    @classmethod
    def check_failure_patterns(cls, message: str) -> Optional[str]:
        """
        Check if message matches any failure patterns
        
        Args:
            message (str): Log message to check
            
        Returns:
            str: Pattern name if matched, None otherwise
        """
        for pattern_name, pattern in cls.FAILURE_PATTERNS.items():
            if pattern.search(message):
                return pattern_name
        
        return None
    
    @classmethod
    def is_important(cls, parsed_log: Dict) -> bool:
        """
        Determine if a log entry is important
        
        Args:
            parsed_log (dict): Parsed log entry
            
        Returns:
            bool: True if important
        """
        message = parsed_log.get('message', '')
        
        # Check for error/warning keywords
        level = cls.determine_level(message)
        if level in ['ERROR', 'WARNING']:
            return True
        
        # Check for failure patterns
        if cls.check_failure_patterns(message):
            return True
        
        # Check for specific critical keywords
        critical_keywords = [
            'failed password', 'authentication failure',
            'unauthorized', 'denied',
            'crash', 'segmentation fault'
        ]
        
        for keyword in critical_keywords:
            if keyword.lower() in message.lower():
                return True
        
        return False
    
    @classmethod
    def extract_username(cls, message: str) -> Optional[str]:
        """
        Extract username from log message
        
        Args:
            message (str): Log message
            
        Returns:
            str: Username if found, None otherwise
        """
        # Try to find "user=" pattern
        user_match = re.search(r'user[=\s]+(\S+)', message, re.IGNORECASE)
        if user_match:
            return user_match.group(1).strip('":\'')
        
        # Try to find "for user" pattern
        for_match = re.search(r'for\s+(\w+)\s+', message, re.IGNORECASE)
        if for_match:
            return for_match.group(1)
        
        return None
    
    @classmethod
    def summarize_line(cls, line: str, max_length: int = 500) -> str:
        """
        Summarize a log line to a maximum length
        
        Args:
            line (str): Log line
            max_length (int): Maximum length
            
        Returns:
            str: Summarized line
        """
        if len(line) <= max_length:
            return line
        
        return line[:max_length] + "..."


class LogAnalyzer:
    """
    Analyzes and categorizes log entries
    """
    
    def __init__(self):
        """Initialize log analyzer"""
        self.parser = LogParser()
    
    def analyze_line(self, line: str, log_type: str = 'SYSLOG') -> Dict:
        """
        Analyze a single log line
        
        Args:
            line (str): Log line
            log_type (str): Type of log (SYSLOG, AUTH, DMESG)
            
        Returns:
            dict: Analysis results
        """
        result = {
            'raw_line': line,
            'log_type': log_type,
            'parsed': None,
            'level': 'INFO',
            'is_important': False,
            'failure_pattern': None,
            'username': None
        }
        
        # Parse the line
        if log_type == 'SYSLOG':
            parsed = self.parser.parse_syslog_line(line)
        elif log_type == 'AUTH':
            parsed = self.parser.parse_auth_line(line)
        else:
            # Try both parsers
            parsed = self.parser.parse_syslog_line(line)
            if not parsed:
                parsed = self.parser.parse_auth_line(line)
        
        result['parsed'] = parsed
        
        if not parsed:
            return result
        
        message = parsed.get('message', '')
        
        # Determine level
        result['level'] = self.parser.determine_level(message)
        
        # Check for failure patterns
        result['failure_pattern'] = self.parser.check_failure_patterns(message)
        
        # Determine importance
        result['is_important'] = self.parser.is_important(parsed)
        
        # Extract username
        result['username'] = self.parser.extract_username(message)
        
        return result
    
    def batch_analyze(self, lines: List[str], log_type: str = 'SYSLOG') -> List[Dict]:
        """
        Analyze multiple log lines
        
        Args:
            lines (list): List of log lines
            log_type (str): Type of log
            
        Returns:
            list: List of analysis results
        """
        return [self.analyze_line(line, log_type) for line in lines]
