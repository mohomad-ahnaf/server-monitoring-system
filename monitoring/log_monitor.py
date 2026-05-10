"""
Log Monitor Module
Monitors system log files and stores parsed logs in database
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List

from monitoring.base_monitor import BaseMonitor
from monitoring.log_parser import LogAnalyzer
from database.db_connection import db
from database.models import Log
import config

logger = logging.getLogger(__name__)


class LogMonitor(BaseMonitor):
    """
    Monitors system log files (/var/log/syslog, /var/log/auth.log, etc.)
    """
    
    def __init__(self, log_files: List[str] = None):
        """
        Initialize log monitor
        
        Args:
            log_files (list): List of log files to monitor
        """
        super().__init__('LogMonitor')
        self.log_files = log_files or config.LOG_FILES
        self.analyzer = LogAnalyzer()
        self.last_positions = {}  # Track file positions
        self.initialize_positions()
    
    def initialize_positions(self):
        """Initialize file positions from last read"""
        for log_file in self.log_files:
            if os.path.exists(log_file):
                try:
                    file_size = os.path.getsize(log_file)
                    self.last_positions[log_file] = file_size
                except Exception as e:
                    self.logger.warning(f"Could not initialize position for {log_file}: {e}")
                    self.last_positions[log_file] = 0
            else:
                self.logger.warning(f"Log file not found: {log_file}")
                self.last_positions[log_file] = 0
    
    def collect(self) -> Dict:
        """
        Collect log data from monitored files
        
        Returns:
            dict: Collected log entries
        """
        try:
            all_logs = []
            
            for log_file in self.log_files:
                if not os.path.exists(log_file):
                    self.logger.warning(f"Log file not accessible: {log_file}")
                    continue
                
                try:
                    logs = self._read_log_file(log_file)
                    all_logs.extend(logs)
                except Exception as e:
                    self.logger.error(f"Error reading {log_file}: {e}")
            
            self.logger.info(f"Collected {len(all_logs)} new log entries")
            
            return {
                'logs': all_logs,
                'count': len(all_logs),
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            self.logger.error(f"Error in log collection: {e}")
            return None
    
    def _read_log_file(self, log_file: str) -> List[Dict]:
        """
        Read new entries from a log file
        
        Args:
            log_file (str): Path to log file
            
        Returns:
            list: New log entries
        """
        logs = []
        
        try:
            current_size = os.path.getsize(log_file)
            last_position = self.last_positions.get(log_file, 0)
            
            # If file was rotated (size decreased), start from beginning
            if current_size < last_position:
                last_position = 0
            
            # Read new entries
            with open(log_file, 'r', errors='ignore') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                
                # Determine log type
                log_type = self._determine_log_type(log_file)
                
                # Analyze new lines
                for line in new_lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Analyze the line
                    analysis = self.analyzer.analyze_line(line, log_type)
                    
                    # Only store if parsed successfully or important
                    if analysis['is_important'] or analysis['parsed']:
                        analysis['log_file'] = log_file
                        analysis['log_type'] = log_type
                        logs.append(analysis)
                
                # Update position
                self.last_positions[log_file] = current_size
                
                self.logger.debug(
                    f"Read {len(new_lines)} lines from {log_file} "
                    f"({len(logs)} important entries)"
                )
            
        except PermissionError:
            self.logger.warning(f"Permission denied reading {log_file}")
        except Exception as e:
            self.logger.error(f"Error reading {log_file}: {e}")
        
        return logs
    
    @staticmethod
    def _determine_log_type(log_file: str) -> str:
        """
        Determine log type from file path
        
        Args:
            log_file (str): Path to log file
            
        Returns:
            str: Log type
        """
        log_file_lower = log_file.lower()
        
        if 'auth' in log_file_lower:
            return 'AUTH'
        elif 'syslog' in log_file_lower:
            return 'SYSLOG'
        elif 'dmesg' in log_file_lower:
            return 'DMESG'
        else:
            return 'SYSLOG'
    
    def store(self, data: Dict) -> bool:
        """
        Store logs in database
        
        Args:
            data (dict): Log data to store
            
        Returns:
            bool: True if successful
        """
        if not data or 'logs' not in data:
            return False
        
        try:
            session = db.get_session()
            
            for log_entry in data['logs']:
                try:
                    parsed = log_entry.get('parsed', {})
                    message = parsed.get('message', log_entry.get('raw_line', ''))
                    
                    # Summarize long messages
                    if len(message) > 1000:
                        message = message[:1000] + "..."
                    
                    log = Log(
                        log_type=log_entry.get('log_type', 'SYSLOG'),
                        log_source=log_entry.get('log_file', 'unknown'),
                        level=log_entry.get('level', 'INFO'),
                        message=message,
                        process_name=parsed.get('process'),
                        process_id=parsed.get('pid'),
                        user_name=log_entry.get('username'),
                        hostname=parsed.get('hostname'),
                        raw_line=log_entry.get('raw_line'),
                        is_parsed=log_entry.get('parsed') is not None,
                        is_important=log_entry.get('is_important', False),
                        created_at=datetime.utcnow()
                    )
                    
                    session.add(log)
                    
                except Exception as e:
                    self.logger.error(f"Error storing log entry: {e}")
                    continue
            
            session.commit()
            session.close()
            
            self.logger.info(f"Stored {len(data['logs'])} log entries in database")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing logs: {e}")
            if 'session' in locals():
                session.close()
            return False


class ContinuousLogMonitor:
    """
    Continuously monitors log files at specified intervals
    """
    
    def __init__(self, log_files: List[str] = None, interval: int = None):
        """
        Initialize continuous log monitor
        
        Args:
            log_files (list): Log files to monitor
            interval (int): Monitoring interval in seconds
        """
        self.monitor = LogMonitor(log_files)
        self.interval = interval or config.LOG_CHECK_INTERVAL
        self.running = False
    
    def run_once(self) -> bool:
        """
        Run monitor once
        
        Returns:
            bool: True if successful
        """
        try:
            data = self.monitor.collect()
            if data:
                return self.monitor.store(data)
            return False
        except Exception as e:
            logger.error(f"Error in continuous log monitor: {e}")
            return False


# Standalone monitoring function
def monitor_logs(log_files: List[str] = None) -> bool:
    """
    Standalone function to monitor logs once
    
    Args:
        log_files (list): Log files to monitor
        
    Returns:
        bool: True if successful
    """
    monitor = LogMonitor(log_files)
    data = monitor.collect()
    if data:
        return monitor.store(data)
    return False
