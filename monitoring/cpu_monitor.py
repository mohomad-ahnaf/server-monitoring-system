"""
CPU Monitor Module
Monitors CPU usage and core information
"""

import psutil
import logging
from datetime import datetime
from monitoring.base_monitor import BaseMonitor
from database.db_connection import db
from database.models import SystemMetric
import config

logger = logging.getLogger(__name__)


class CPUMonitor(BaseMonitor):
    """
    Monitors CPU usage percentage and core information
    """
    
    def __init__(self):
        """Initialize CPU monitor"""
        super().__init__('CPU')
        self.interval = config.MONITORING_INTERVAL
    
    def collect(self):
        """
        Collect CPU usage data
        
        Returns:
            dict: CPU metrics
        """
        try:
            # Get CPU percentages
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get per-core CPU percentages
            cpu_per_core = psutil.cpu_percent(interval=1, percpu=True)
            
            # Get CPU count
            cpu_count_physical = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # Get load average
            load_avg = psutil.getloadavg()
            
            # Get CPU times
            cpu_times = psutil.cpu_times()
            
            data = {
                'cpu_percent': cpu_percent,
                'cpu_per_core': cpu_per_core,
                'cpu_count_physical': cpu_count_physical,
                'cpu_count_logical': cpu_count_logical,
                'load_avg_1m': load_avg[0],
                'load_avg_5m': load_avg[1],
                'load_avg_15m': load_avg[2],
                'cpu_times': {
                    'user': cpu_times.user,
                    'system': cpu_times.system,
                    'idle': cpu_times.idle,
                    'nice': getattr(cpu_times, 'nice', 0),
                    'iowait': getattr(cpu_times, 'iowait', 0),
                },
                'timestamp': datetime.utcnow()
            }
            
            self.logger.info(
                f"CPU Usage: {cpu_percent}% | Load Avg: {load_avg[0]:.2f}, "
                f"{load_avg[1]:.2f}, {load_avg[2]:.2f}"
            )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting CPU data: {e}")
            return None
    
    def store(self, data):
        """
        Store CPU data in database
        
        Args:
            data (dict): CPU metrics
            
        Returns:
            bool: True if successful
        """
        try:
            session = db.get_session()
            
            metric = SystemMetric(
                cpu_usage=data['cpu_percent'],
                cpu_cores=data['cpu_count_logical'],
                load_average_1m=data['load_avg_1m'],
                load_average_5m=data['load_avg_5m'],
                load_average_15m=data['load_avg_15m'],
                # These will be set by other monitors
                memory_usage=0,
                memory_total_mb=0,
                memory_used_mb=0,
                memory_available_mb=0,
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
            self.logger.error(f"Error storing CPU data: {e}")
            if 'session' in locals():
                session.close()
            return False
