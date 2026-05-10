"""
Main Collector Module
Orchestrates all monitoring modules and collects metrics periodically
"""

import time
import logging
import signal
import sys
from datetime import datetime
from threading import Thread, Event

import config
from database.db_connection import db
from database.models import SystemMetric, SystemInfo
from monitoring.cpu_monitor import CPUMonitor
from monitoring.memory_monitor import MemoryMonitor
from monitoring.disk_monitor import DiskMonitor
from monitoring.process_monitor import ProcessMonitor
from monitoring.uptime_monitor import UptimeMonitor

# Configure logging
logging.basicConfig(
    level=config.LOG_LEVEL,
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Main metrics collector that orchestrates all monitoring modules
    """
    
    def __init__(self):
        """Initialize the metrics collector"""
        self.running = False
        self.stop_event = Event()
        self.monitors = {
            'cpu': CPUMonitor(),
            'memory': MemoryMonitor(),
            'disk': DiskMonitor(),
            'process': ProcessMonitor(),
            'uptime': UptimeMonitor(),
        }
        self.collection_interval = config.MONITORING_INTERVAL
        self.logger = logging.getLogger(__name__)
    
    def initialize(self):
        """Initialize database and test connectivity"""
        self.logger.info("="*60)
        self.logger.info("Initializing Metrics Collector")
        self.logger.info("="*60)
        
        # Test database connection
        self.logger.info("Testing database connection...")
        if not db.test_connection():
            self.logger.error("Failed to connect to database")
            return False
        
        self.logger.info("✓ Database connected successfully")
        
        # Initialize database schema
        self.logger.info("Initializing database schema...")
        if not db.init_db():
            self.logger.warning("Schema initialization returned warnings (may already exist)")
        
        self.logger.info("✓ Database schema ready")
        
        return True
    
    def collect_all_metrics(self):
        """
        Collect metrics from all monitoring modules
        
        Returns:
            dict: All collected metrics
        """
        timestamp = datetime.utcnow()
        all_data = {
            'timestamp': timestamp,
            'metrics': {}
        }
        
        try:
            # Collect from all monitors
            for monitor_name, monitor in self.monitors.items():
                self.logger.debug(f"Collecting {monitor_name} metrics...")
                data = monitor.collect()
                if data:
                    all_data['metrics'][monitor_name] = data
                else:
                    self.logger.warning(f"Failed to collect {monitor_name} metrics")
            
            # Store combined metrics in database
            self._store_combined_metrics(all_data)
            
            return all_data
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return None
    
    def _store_combined_metrics(self, all_data):
        """
        Store all collected metrics in a single database record
        
        Args:
            all_data (dict): All collected metrics
        """
        try:
            session = db.get_session()
            
            cpu_data = all_data['metrics'].get('cpu', {})
            memory_data = all_data['metrics'].get('memory', {})
            disk_data = all_data['metrics'].get('disk', {})
            uptime_data = all_data['metrics'].get('uptime', {})
            
            metric = SystemMetric(
                # CPU metrics
                cpu_usage=cpu_data.get('cpu_percent', 0),
                cpu_cores=cpu_data.get('cpu_count_logical', 0),
                load_average_1m=cpu_data.get('load_avg_1m', 0),
                load_average_5m=cpu_data.get('load_avg_5m', 0),
                load_average_15m=cpu_data.get('load_avg_15m', 0),
                
                # Memory metrics
                memory_usage=memory_data.get('memory_percent', 0),
                memory_total_mb=int(memory_data.get('memory_total_mb', 0)),
                memory_used_mb=int(memory_data.get('memory_used_mb', 0)),
                memory_available_mb=int(memory_data.get('memory_available_mb', 0)),
                swap_usage=memory_data.get('swap_percent', 0),
                
                # Disk metrics
                disk_usage=disk_data.get('disk_percent', 0),
                disk_total_gb=disk_data.get('disk_total_gb', 0),
                disk_used_gb=disk_data.get('disk_used_gb', 0),
                disk_free_gb=disk_data.get('disk_free_gb', 0),
                
                # Uptime metrics
                uptime_seconds=uptime_data.get('uptime_seconds', 0),
                
                timestamp=all_data['timestamp']
            )
            
            session.add(metric)
            session.commit()
            session.close()
            
            self.logger.debug("Combined metrics stored successfully")
            
        except Exception as e:
            self.logger.error(f"Error storing combined metrics: {e}")
            if 'session' in locals():
                session.close()
    
    def print_metrics(self, all_data):
        """
        Print collected metrics to console
        
        Args:
            all_data (dict): All collected metrics
        """
        if not all_data or 'metrics' not in all_data:
            return
        
        metrics = all_data['metrics']
        timestamp = all_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        print("\n" + "="*70)
        print(f"SYSTEM METRICS - {timestamp}")
        print("="*70)
        
        # CPU metrics
        if 'cpu' in metrics:
            cpu = metrics['cpu']
            print(f"\n📊 CPU USAGE:")
            print(f"   ├─ Overall: {cpu.get('cpu_percent', 0):.1f}%")
            print(f"   ├─ Cores: {cpu.get('cpu_count_logical', 0)}")
            print(f"   └─ Load Avg (1m/5m/15m): "
                  f"{cpu.get('load_avg_1m', 0):.2f} / "
                  f"{cpu.get('load_avg_5m', 0):.2f} / "
                  f"{cpu.get('load_avg_15m', 0):.2f}")
        
        # Memory metrics
        if 'memory' in metrics:
            mem = metrics['memory']
            print(f"\n💾 MEMORY USAGE:")
            print(f"   ├─ RAM: {mem.get('memory_percent', 0):.1f}% "
                  f"({mem.get('memory_used_mb', 0):.0f}MB / "
                  f"{mem.get('memory_total_mb', 0):.0f}MB)")
            print(f"   └─ Swap: {mem.get('swap_percent', 0):.1f}%")
        
        # Disk metrics
        if 'disk' in metrics:
            disk = metrics['disk']
            print(f"\n💿 DISK USAGE:")
            print(f"   ├─ Root: {disk.get('disk_percent', 0):.1f}% "
                  f"({disk.get('disk_used_gb', 0):.1f}GB / "
                  f"{disk.get('disk_total_gb', 0):.1f}GB)")
            if 'partitions' in disk:
                for part in disk['partitions'][:3]:
                    print(f"   ├─ {part['device']}: {part['percent']:.1f}% "
                          f"({part['fstype']})")
        
        # Uptime
        if 'uptime' in metrics:
            uptime = metrics['uptime']
            print(f"\n⏱️  UPTIME:")
            print(f"   ├─ Boot Time: {uptime.get('uptime_formatted', 'N/A')}")
            print(f"   └─ System: {uptime.get('hostname', 'N/A')} "
                  f"({uptime.get('os_type', 'N/A')})")
        
        # Top processes
        if 'process' in metrics:
            proc = metrics['process']
            print(f"\n⚙️  TOP PROCESSES:")
            print(f"   Total: {proc.get('total_processes', 0)}")
            if proc.get('top_by_cpu'):
                top_cpu = proc['top_by_cpu'][0]
                print(f"   ├─ CPU: {top_cpu['name']} ({top_cpu['cpu_percent']:.1f}%)")
            if proc.get('top_by_memory'):
                top_mem = proc['top_by_memory'][0]
                print(f"   └─ Memory: {top_mem['name']} ({top_mem['memory_percent']:.1f}%)")
        
        print("\n" + "="*70 + "\n")
    
    def collection_loop(self):
        """Main collection loop"""
        self.logger.info(f"Starting metrics collection every {self.collection_interval} seconds")
        self.running = True
        collection_count = 0
        
        while self.running and not self.stop_event.is_set():
            try:
                collection_count += 1
                self.logger.info(f"\n[Collection #{collection_count}] Starting data collection...")
                
                # Collect all metrics
                metrics = self.collect_all_metrics()
                
                if metrics:
                    # Print to console
                    self.print_metrics(metrics)
                    self.logger.info("✓ Metrics collected and stored successfully")
                else:
                    self.logger.error("✗ Failed to collect metrics")
                
                # Wait for next collection
                self.logger.debug(f"Waiting {self.collection_interval} seconds until next collection...")
                self.stop_event.wait(self.collection_interval)
                
            except KeyboardInterrupt:
                self.logger.info("Received interrupt signal, shutting down...")
                self.stop()
                break
            except Exception as e:
                self.logger.error(f"Error in collection loop: {e}")
                self.stop_event.wait(5)  # Wait 5 seconds before retry
    
    def start(self):
        """Start the metrics collector"""
        if not self.initialize():
            self.logger.error("Failed to initialize collector")
            return False
        
        # Start collection in background thread
        collection_thread = Thread(target=self.collection_loop, daemon=False)
        collection_thread.start()
        
        self.logger.info("Metrics collector started")
        return True
    
    def stop(self):
        """Stop the metrics collector"""
        self.logger.info("Stopping metrics collector...")
        self.running = False
        self.stop_event.set()
        self.logger.info("✓ Collector stopped")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"\nReceived signal {signum}, shutting down...")
    if hasattr(signal_handler, 'collector'):
        signal_handler.collector.stop()
    sys.exit(0)


def main():
    """Main entry point"""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start collector
    collector = MetricsCollector()
    signal_handler.collector = collector
    
    if collector.start():
        # Keep the main thread running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            collector.stop()
    else:
        logger.error("Failed to start collector")
        sys.exit(1)


if __name__ == '__main__':
    main()
