"""
Process Monitor Module
Monitors running processes and top processes by resource usage
"""

import psutil
import logging
from datetime import datetime
from monitoring.base_monitor import BaseMonitor
from database.db_connection import db
from database.models import TopProcess

logger = logging.getLogger(__name__)


class ProcessMonitor(BaseMonitor):
    """
    Monitors running processes and tracks top processes by CPU and memory
    """
    
    def __init__(self, top_count=10):
        """
        Initialize process monitor
        
        Args:
            top_count (int): Number of top processes to track
        """
        super().__init__('Process')
        self.top_count = top_count
    
    def collect(self):
        """
        Collect process data
        
        Returns:
            dict: Process metrics
        """
        try:
            # Get all processes
            process_list = []
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent'])
                    if pinfo['cpu_percent'] is not None and pinfo['memory_percent'] is not None:
                        process_list.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Get top processes by CPU
            top_by_cpu = sorted(
                process_list,
                key=lambda x: x['cpu_percent'],
                reverse=True
            )[:self.top_count]
            
            # Get top processes by memory
            top_by_memory = sorted(
                process_list,
                key=lambda x: x['memory_percent'],
                reverse=True
            )[:self.top_count]
            
            # Get process count
            running_count = len(psutil.pids())
            
            data = {
                'total_processes': running_count,
                'top_by_cpu': top_by_cpu,
                'top_by_memory': top_by_memory,
                'all_processes': process_list,
                'timestamp': datetime.utcnow()
            }
            
            self.logger.info(
                f"Total Processes: {running_count} | "
                f"Top CPU: {top_by_cpu[0]['name']} ({top_by_cpu[0]['cpu_percent']:.1f}%) | "
                f"Top Memory: {top_by_memory[0]['name']} ({top_by_memory[0]['memory_percent']:.1f}%)"
            )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error collecting process data: {e}")
            return None
    
    def store(self, data):
        """
        Store top processes in database
        
        Args:
            data (dict): Process metrics
            
        Returns:
            bool: True if successful
        """
        try:
            session = db.get_session()
            
            # Store top processes by CPU
            for proc in data['top_by_cpu'][:self.top_count]:
                try:
                    proc_info = psutil.Process(proc['pid'])
                    
                    # Get memory in MB
                    memory_info = proc_info.memory_info()
                    memory_mb = memory_info.rss / (1024 * 1024)
                    
                    top_proc = TopProcess(
                        pid=proc['pid'],
                        process_name=proc['name'],
                        cpu_usage=proc['cpu_percent'],
                        memory_usage=proc['memory_percent'],
                        memory_mb=int(memory_mb),
                        status=proc_info.status(),
                        user=proc_info.username() if hasattr(proc_info, 'username') else None,
                        create_time=datetime.fromtimestamp(proc_info.create_time()),
                        recorded_at=data['timestamp']
                    )
                    session.add(top_proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing process data: {e}")
            if 'session' in locals():
                session.close()
            return False
