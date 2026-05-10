"""
Disk Monitor Module
Monitors disk usage and I/O statistics
"""

import psutil
import logging
from datetime import datetime
from monitoring.base_monitor import BaseMonitor
from database.db_connection import db
from database.models import SystemMetric

logger = logging.getLogger(__name__)


class DiskMonitor(BaseMonitor):
    """
    Monitors disk usage and I/O statistics
    """
    
    def __init__(self):
        """Initialize disk monitor"""
        super().__init__('Disk')
    
    def collect(self):
        """
        Collect disk usage data
        
        Returns:
            dict: Disk metrics
        """
        try:
            # Get root partition disk usage
            root_disk = psutil.disk_usage('/')
            
            # Get disk I/O counters
            disk_io = psutil.disk_io_counters()
            
            # Get all partitions
            partitions = psutil.disk_partitions()
            
            partition_data = []
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partition_data.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent,
                    })
                except PermissionError:
                    # Skip partitions we don't have permission to access
                    pass
            
            # Convert bytes to GB
            total_gb = root_disk.total / (1024 ** 3)
            used_gb = root_disk.used / (1024 ** 3)
            free_gb = root_disk.free / (1024 ** 3)
            
            data = {
                'disk_percent': root_disk.percent,
                'disk_total': root_disk.total,
                'disk_used': root_disk.used,
                'disk_free': root_disk.free,
                'disk_total_gb': total_gb,
                'disk_used_gb': used_gb,
                'disk_free_gb': free_gb,
                'io_read_count': disk_io.read_count,
                'io_write_count': disk_io.write_count,
                'io_read_bytes': disk_io.read_bytes,
                'io_write_bytes': disk_io.write_bytes,
                'partitions': partition_data,
                'timestamp': datetime.utcnow()
            }
            
            self.logger.info(
                f"Disk Usage (Root): {root_disk.percent:.1f}% "
                f"({self.format_bytes(root_disk.used)} / "
                f"{self.format_bytes(root_disk.total)})"
            )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting disk data: {e}")
            return None
    
    def store(self, data):
        """
        Store disk data in database
        
        Args:
            data (dict): Disk metrics
            
        Returns:
            bool: True if successful
        """
        try:
            session = db.get_session()
            
            metric = SystemMetric(
                cpu_usage=0,
                cpu_cores=0,
                memory_usage=0,
                memory_total_mb=0,
                memory_used_mb=0,
                memory_available_mb=0,
                disk_usage=data['disk_percent'],
                disk_total_gb=data['disk_total_gb'],
                disk_used_gb=data['disk_used_gb'],
                disk_free_gb=data['disk_free_gb'],
                uptime_seconds=0,
                timestamp=data['timestamp']
            )
            
            session.add(metric)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing disk data: {e}")
            if 'session' in locals():
                session.close()
            return False
