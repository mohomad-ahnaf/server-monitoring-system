"""
Base Monitor Class
Provides common functionality for all monitoring modules
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from database.db_connection import db
import config

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class BaseMonitor(ABC):
    """
    Abstract base class for all monitoring modules
    Provides common methods for data collection and storage
    """
    
    def __init__(self, name):
        """
        Initialize monitor
        
        Args:
            name (str): Monitor name
        """
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def collect(self):
        """
        Collect monitoring data
        Must be implemented by subclasses
        
        Returns:
            dict: Collected metrics
        """
        pass
    
    def store(self, data):
        """
        Store collected data in database
        
        Args:
            data (dict): Data to store
            
        Returns:
            bool: True if successful
        """
        try:
            session = db.get_session()
            # This will be implemented by specific monitors
            session.close()
            return True
        except Exception as e:
            self.logger.error(f"Error storing data: {e}")
            return False
    
    def run(self):
        """
        Main monitoring cycle: collect and store
        
        Returns:
            dict: Collected and stored data
        """
        try:
            self.logger.info(f"Starting {self.name} collection...")
            data = self.collect()
            
            if data:
                if self.store(data):
                    self.logger.debug(f"{self.name} data stored successfully")
                    return data
                else:
                    self.logger.error(f"Failed to store {self.name} data")
                    return None
            else:
                self.logger.warning(f"{self.name} returned no data")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in {self.name} monitor: {e}")
            return None
    
    @staticmethod
    def format_bytes(bytes_value):
        """
        Convert bytes to human readable format
        
        Args:
            bytes_value (int): Bytes to convert
            
        Returns:
            str: Formatted string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    @staticmethod
    def get_timestamp():
        """Get current timestamp"""
        return datetime.utcnow()
