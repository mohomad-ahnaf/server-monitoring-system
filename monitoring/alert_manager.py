"""
Alert Manager Module
Manages alert thresholds and alert logic
"""

import logging
from datetime import datetime, timedelta
from database.db_connection import db
from database.models import Alert, AlertThreshold
import config

logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manages system alerts and thresholds
    """
    
    # Default thresholds
    DEFAULT_THRESHOLDS = {
        'CPU_USAGE': {'warning': 70.0, 'critical': 85.0},
        'MEMORY_USAGE': {'warning': 80.0, 'critical': 90.0},
        'DISK_USAGE': {'warning': 80.0, 'critical': 95.0},
        'SWAP_USAGE': {'warning': 50.0, 'critical': 80.0},
    }
    
    def __init__(self):
        """Initialize alert manager"""
        self.logger = logging.getLogger(__name__)
        self._load_thresholds()
    
    def _load_thresholds(self):
        """Load thresholds from database"""
        try:
            session = db.get_session()
            thresholds = session.query(AlertThreshold).all()
            
            self.thresholds = {}
            for threshold in thresholds:
                self.thresholds[threshold.metric_name] = {
                    'warning': threshold.warning_threshold,
                    'critical': threshold.critical_threshold,
                    'enabled': threshold.enabled,
                    'id': threshold.id
                }
            
            session.close()
            self.logger.info(f"Loaded {len(self.thresholds)} alert thresholds")
            
        except Exception as e:
            self.logger.error(f"Error loading thresholds: {e}")
            self.thresholds = {}
    
    def get_threshold(self, metric_name: str) -> dict:
        """
        Get threshold for a metric
        
        Args:
            metric_name (str): Name of the metric
            
        Returns:
            dict: Threshold values
        """
        return self.thresholds.get(
            metric_name,
            self.DEFAULT_THRESHOLDS.get(metric_name, {})
        )
    
    def check_metric(self, metric_name: str, value: float, current_metric=None) -> dict:
        """
        Check if metric exceeds thresholds
        
        Args:
            metric_name (str): Name of the metric
            value (float): Current value
            current_metric: Current metric object
            
        Returns:
            dict: Alert info or None if no alert
        """
        threshold = self.get_threshold(metric_name)
        
        if not threshold:
            return None
        
        if not threshold.get('enabled', True):
            return None
        
        warning = threshold.get('warning', 0)
        critical = threshold.get('critical', 0)
        
        alert_info = None
        
        if value >= critical:
            alert_info = {
                'severity': 'CRITICAL',
                'level': 'critical',
                'current_value': value,
                'threshold': critical
            }
        elif value >= warning:
            alert_info = {
                'severity': 'WARNING',
                'level': 'warning',
                'current_value': value,
                'threshold': warning
            }
        
        return alert_info
    
    def create_alert(self, alert_type: str, message: str, severity: str,
                    metric_name: str = None, current_value: float = None,
                    threshold_value: float = None) -> bool:
        """
        Create a new alert
        
        Args:
            alert_type (str): Type of alert (CPU, MEMORY, DISK, LOG)
            message (str): Alert message
            severity (str): Severity level (CRITICAL, WARNING, INFO)
            metric_name (str): Name of the metric
            current_value (float): Current value
            threshold_value (float): Threshold value
            
        Returns:
            bool: True if successful
        """
        try:
            session = db.get_session()
            
            alert = Alert(
                alert_type=alert_type,
                metric_name=metric_name,
                current_value=current_value,
                threshold_value=threshold_value,
                message=message,
                severity=severity,
                is_resolved=False,
                created_at=datetime.utcnow()
            )
            
            session.add(alert)
            session.commit()
            session.close()
            
            self.logger.info(f"Alert created: {alert_type} - {message}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            if 'session' in locals():
                session.close()
            return False
    
    def resolve_alert(self, alert_id: int) -> bool:
        """
        Mark an alert as resolved
        
        Args:
            alert_id (int): Alert ID
            
        Returns:
            bool: True if successful
        """
        try:
            session = db.get_session()
            alert = session.query(Alert).filter(Alert.id == alert_id).first()
            
            if alert:
                alert.is_resolved = True
                alert.resolved_at = datetime.utcnow()
                session.commit()
                session.close()
                
                self.logger.info(f"Alert {alert_id} resolved")
                return True
            
            session.close()
            return False
            
        except Exception as e:
            self.logger.error(f"Error resolving alert: {e}")
            if 'session' in locals():
                session.close()
            return False
    
    def get_unresolved_alerts(self, limit: int = 100) -> list:
        """
        Get unresolved alerts
        
        Args:
            limit (int): Maximum number of alerts to return
            
        Returns:
            list: List of alerts
        """
        try:
            session = db.get_session()
            alerts = session.query(Alert).filter(
                Alert.is_resolved == False
            ).order_by(Alert.created_at.desc()).limit(limit).all()
            session.close()
            return alerts
        except Exception as e:
            self.logger.error(f"Error getting alerts: {e}")
            return []
    
    def get_recent_alerts(self, hours: int = 24, limit: int = 100) -> list:
        """
        Get recent alerts
        
        Args:
            hours (int): Number of hours to look back
            limit (int): Maximum number of alerts
            
        Returns:
            list: List of alerts
        """
        try:
            session = db.get_session()
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            alerts = session.query(Alert).filter(
                Alert.created_at >= cutoff_time
            ).order_by(Alert.created_at.desc()).limit(limit).all()
            
            session.close()
            return alerts
        except Exception as e:
            self.logger.error(f"Error getting recent alerts: {e}")
            return []
    
    def cleanup_old_alerts(self, days: int = 30) -> int:
        """
        Delete old resolved alerts
        
        Args:
            days (int): Number of days to keep
            
        Returns:
            int: Number of deleted alerts
        """
        try:
            session = db.get_session()
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            deleted = session.query(Alert).filter(
                Alert.is_resolved == True,
                Alert.resolved_at < cutoff_time
            ).delete()
            
            session.commit()
            session.close()
            
            if deleted > 0:
                self.logger.info(f"Cleaned up {deleted} old alerts")
            
            return deleted
            
        except Exception as e:
            self.logger.error(f"Error cleaning up alerts: {e}")
            if 'session' in locals():
                session.close()
            return 0
    
    def update_threshold(self, metric_name: str, warning: float, critical: float) -> bool:
        """
        Update alert threshold
        
        Args:
            metric_name (str): Metric name
            warning (float): Warning threshold
            critical (float): Critical threshold
            
        Returns:
            bool: True if successful
        """
        try:
            session = db.get_session()
            threshold = session.query(AlertThreshold).filter(
                AlertThreshold.metric_name == metric_name
            ).first()
            
            if threshold:
                threshold.warning_threshold = warning
                threshold.critical_threshold = critical
                threshold.updated_at = datetime.utcnow()
                session.commit()
                session.close()
                
                # Reload thresholds
                self._load_thresholds()
                
                self.logger.info(f"Updated threshold for {metric_name}")
                return True
            
            session.close()
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating threshold: {e}")
            if 'session' in locals():
                session.close()
            return False
