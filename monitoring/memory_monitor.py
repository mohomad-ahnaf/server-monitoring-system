"""
Memory Monitor Module
Monitors memory and swap usage
"""

import psutil
import logging
from datetime import datetime
from monitoring.base_monitor import BaseMonitor
from database.db_connection import db
from database.models import SystemMetric

logger = logging.getLogger(__name__)


class MemoryMonitor(BaseMonitor):
    """
    Monitors RAM and swap memory usage
    """
    
    def __init__(self):
        """Initialize memory monitor"""
        super().__init__('Memory')
    
    def collect(self):
        """
        Collect memory usage data
        
        Returns:
            dict: Memory metrics
        """
        try:
            # Get virtual memory (RAM)
            vmem = psutil.virtual_memory()
            
            # Get swap memory
            swap = psutil.swap_memory()
            
            data = {
                'memory_percent': vmem.percent,
                'memory_total': vmem.total,
                'memory_used': vmem.used,
                'memory_available': vmem.available,
                'memory_free': vmem.free,
                'memory_buffers': vmem.buffers,
                'memory_cached': vmem.cached,
                'swap_percent': swap.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'timestamp': datetime.utcnow()
            }
            
            # Convert bytes to MB
            memory_used_mb = data['memory_used'] / (1024 * 1024)
            memory_total_mb = data['memory_total'] / (1024 * 1024)
            memory_available_mb = data['memory_available'] / (1024 * 1024)
            
            self.logger.info(
                f"Memory Usage: {data['memory_percent']:.1f}% "
                f"({self.format_bytes(data['memory_used'])} / "
                f"{self.format_bytes(data['memory_total'])}) | "
                f"Swap: {swap.percent:.1f}%"
            )
            
            data['memory_used_mb'] = memory_used_mb
            data['memory_total_mb'] = memory_total_mb
            data['memory_available_mb'] = memory_available_mb
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting memory data: {e}")
            return None
    
    def store(self, data):
        """
        Store memory data in database
        
        Args:
            data (dict): Memory metrics
            
        Returns:
            bool: True if successful
        """
        try:
            session = db.get_session()
            
            metric = SystemMetric(
                cpu_usage=0,
                cpu_cores=0,
                memory_usage=data['memory_percent'],
                memory_total_mb=int(data['memory_total_mb']),
                memory_used_mb=int(data['memory_used_mb']),
                memory_available_mb=int(data['memory_available_mb']),
                swap_usage=data['swap_percent'],
                # These will be set by other monitors
                disk_usage=0,
                disk_total_gb=0,
                disk_used_gb=0,
                disk_free_gb=0,
                uptime_seconds=0,
                timestamp=data['timestamp']
            )
            
            session.add(metric)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing memory data: {e}")
            if 'session' in locals():
                session.close()
            return False
