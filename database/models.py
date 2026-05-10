"""
SQLAlchemy ORM Models for the Monitoring System
Defines database models for system metrics, alerts, logs, etc.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, BigInteger, Text
from sqlalchemy.sql import func
from database.db_connection import Base


class SystemMetric(Base):
    """
    Stores system resource metrics (CPU, memory, disk, etc.)
    """
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True, index=True)
    cpu_usage = Column(Float, nullable=False)
    cpu_cores = Column(Integer, nullable=False)
    memory_usage = Column(Float, nullable=False)
    memory_total_mb = Column(BigInteger, nullable=False)
    memory_used_mb = Column(BigInteger, nullable=False)
    memory_available_mb = Column(BigInteger, nullable=False)
    swap_usage = Column(Float)
    disk_usage = Column(Float, nullable=False)
    disk_total_gb = Column(Float, nullable=False)
    disk_used_gb = Column(Float, nullable=False)
    disk_free_gb = Column(Float, nullable=False)
    uptime_seconds = Column(BigInteger, nullable=False)
    load_average_1m = Column(Float)
    load_average_5m = Column(Float)
    load_average_15m = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return (f"<SystemMetric(cpu={self.cpu_usage}%, mem={self.memory_usage}%, "
                f"disk={self.disk_usage}%, timestamp={self.timestamp})>")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'cpu_usage': self.cpu_usage,
            'cpu_cores': self.cpu_cores,
            'memory_usage': self.memory_usage,
            'memory_total_mb': self.memory_total_mb,
            'memory_used_mb': self.memory_used_mb,
            'memory_available_mb': self.memory_available_mb,
            'swap_usage': self.swap_usage,
            'disk_usage': self.disk_usage,
            'disk_total_gb': self.disk_total_gb,
            'disk_used_gb': self.disk_used_gb,
            'disk_free_gb': self.disk_free_gb,
            'uptime_seconds': self.uptime_seconds,
            'load_average_1m': self.load_average_1m,
            'load_average_5m': self.load_average_5m,
            'load_average_15m': self.load_average_15m,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


class Alert(Base):
    """
    Stores system alerts (when thresholds are exceeded)
    """
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # CPU, MEMORY, DISK, LOG
    metric_name = Column(String(100))
    current_value = Column(Float)
    threshold_value = Column(Float)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False, index=True)  # CRITICAL, WARNING, INFO
    is_resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return (f"<Alert(type={self.alert_type}, severity={self.severity}, "
                f"message={self.message[:50]}...)>")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'metric_name': self.metric_name,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'message': self.message,
            'severity': self.severity,
            'is_resolved': self.is_resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Log(Base):
    """
    Stores parsed system logs
    """
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True, index=True)
    log_type = Column(String(50), nullable=False, index=True)  # SYSLOG, AUTH, DMESG
    log_source = Column(String(255), nullable=False)  # File path
    level = Column(String(20), index=True)  # ERROR, WARNING, INFO
    message = Column(Text, nullable=False)
    process_name = Column(String(255))
    process_id = Column(Integer)
    user_name = Column(String(100))
    hostname = Column(String(255))
    raw_line = Column(Text)
    is_parsed = Column(Boolean, default=True)
    is_important = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return (f"<Log(type={self.log_type}, level={self.level}, "
                f"message={self.message[:50]}...)>")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'log_type': self.log_type,
            'log_source': self.log_source,
            'level': self.level,
            'message': self.message,
            'process_name': self.process_name,
            'process_id': self.process_id,
            'user_name': self.user_name,
            'hostname': self.hostname,
            'raw_line': self.raw_line,
            'is_parsed': self.is_parsed,
            'is_important': self.is_important,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class AlertThreshold(Base):
    """
    Stores configurable alert thresholds
    """
    __tablename__ = 'alert_thresholds'
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, unique=True)
    warning_threshold = Column(Float, nullable=False)
    critical_threshold = Column(Float, nullable=False)
    enabled = Column(Boolean, default=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return (f"<AlertThreshold(metric={self.metric_name}, "
                f"warning={self.warning_threshold}, critical={self.critical_threshold})>")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'warning_threshold': self.warning_threshold,
            'critical_threshold': self.critical_threshold,
            'enabled': self.enabled,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class SystemInfo(Base):
    """
    Stores static system information
    """
    __tablename__ = 'system_info'
    
    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(255), nullable=False)
    os_type = Column(String(100))
    os_version = Column(String(100))
    kernel_version = Column(String(100))
    total_cpu_cores = Column(Integer)
    boot_time = Column(DateTime)
    last_checked = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemInfo(hostname={self.hostname}, os={self.os_type})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'hostname': self.hostname,
            'os_type': self.os_type,
            'os_version': self.os_version,
            'kernel_version': self.kernel_version,
            'total_cpu_cores': self.total_cpu_cores,
            'boot_time': self.boot_time.isoformat() if self.boot_time else None,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
        }


class TopProcess(Base):
    """
    Stores top processes by CPU and memory usage
    """
    __tablename__ = 'top_processes'
    
    id = Column(Integer, primary_key=True, index=True)
    pid = Column(Integer, nullable=False)
    process_name = Column(String(255), nullable=False)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    memory_mb = Column(BigInteger)
    status = Column(String(20))
    user = Column(String(100))
    create_time = Column(DateTime)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return (f"<TopProcess(pid={self.pid}, name={self.process_name}, "
                f"cpu={self.cpu_usage}%, mem={self.memory_usage}%)>")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'pid': self.pid,
            'process_name': self.process_name,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'memory_mb': self.memory_mb,
            'status': self.status,
            'user': self.user,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None,
        }
