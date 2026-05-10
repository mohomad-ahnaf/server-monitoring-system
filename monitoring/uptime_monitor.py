"""
Uptime Monitor Module
Monitors system uptime and boot time
"""

import psutil
import logging
import platform
from datetime import datetime, timedelta
from monitoring.base_monitor import BaseMonitor

logger = logging.getLogger(__name__)


class UptimeMonitor(BaseMonitor):
    """
    Monitors system uptime and boot information
    """
    
    def __init__(self):
        """Initialize uptime monitor"""
        super().__init__('Uptime')
    
    def collect(self):
        """
        Collect uptime data
        
        Returns:
            dict: Uptime metrics
        """
        try:
            # Get boot time
            boot_time_timestamp = psutil.boot_time()
            boot_time = datetime.fromtimestamp(boot_time_timestamp)
            
            # Get uptime in seconds
            uptime_seconds = int(datetime.now().timestamp() - boot_time_timestamp)
            
            # Calculate uptime components
            uptime_timedelta = timedelta(seconds=uptime_seconds)
            days = uptime_timedelta.days
            hours = uptime_timedelta.seconds // 3600
            minutes = (uptime_timedelta.seconds % 3600) // 60
            
            # Get system info
            hostname = platform.node()
            os_type = platform.system()
            os_release = platform.release()
            kernel_version = platform.version()
            
            data = {
                'boot_time': boot_time,
                'boot_time_timestamp': boot_time_timestamp,
                'uptime_seconds': uptime_seconds,
                'uptime_days': days,
                'uptime_hours': hours,
                'uptime_minutes': minutes,
                'uptime_formatted': f"{days}d {hours}h {minutes}m",
                'hostname': hostname,
                'os_type': os_type,
                'os_release': os_release,
                'kernel_version': kernel_version,
                'timestamp': datetime.utcnow()
            }
            
            self.logger.info(
                f"System Uptime: {data['uptime_formatted']} | "
                f"Boot Time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting uptime data: {e}")
            return None
