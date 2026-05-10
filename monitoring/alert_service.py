"""
Alert Service Module
Generates alerts based on system metrics
"""

import logging
from datetime import datetime, timedelta
from database.db_connection import db
from database.models import SystemMetric, Alert
from monitoring.alert_manager import AlertManager
import config

logger = logging.getLogger(__name__)


class AlertService:
    """
    Service that generates and manages system alerts
    """
    
    def __init__(self):
        """Initialize alert service"""
        self.alert_manager = AlertManager()
        self.logger = logging.getLogger(__name__)
        self.alert_cooldown = {}  # Track alert generation to avoid duplicates
        self.cooldown_period = 300  # 5 minutes
    
    def check_metrics_and_generate_alerts(self, metric) -> list:
        """
        Check metrics and generate alerts if thresholds exceeded
        
        Args:
            metric: SystemMetric object
            
        Returns:
            list: Generated alerts
        """
        alerts_generated = []
        
        try:
            # Check CPU usage
            cpu_alert = self.check_cpu_usage(metric)
            if cpu_alert:
                alerts_generated.append(cpu_alert)
            
            # Check memory usage
            memory_alert = self.check_memory_usage(metric)
            if memory_alert:
                alerts_generated.append(memory_alert)
            
            # Check disk usage
            disk_alert = self.check_disk_usage(metric)
            if disk_alert:
                alerts_generated.append(disk_alert)
            
            # Check swap usage
            swap_alert = self.check_swap_usage(metric)
            if swap_alert:
                alerts_generated.append(swap_alert)
            
            return alerts_generated
            
        except Exception as e:
            self.logger.error(f"Error checking metrics: {e}")
            return []
    
    def check_cpu_usage(self, metric) -> bool:
        """Check CPU usage and generate alert if needed"""
        return self._check_metric(
            metric_name='CPU_USAGE',
            value=metric.cpu_usage,
            alert_type='CPU',
            message_template='CPU usage is {:.1f}% (threshold: {:.1f}%)'
        )
    
    def check_memory_usage(self, metric) -> bool:
        """Check memory usage and generate alert if needed"""
        return self._check_metric(
            metric_name='MEMORY_USAGE',
            value=metric.memory_usage,
            alert_type='MEMORY',
            message_template='Memory usage is {:.1f}% (threshold: {:.1f}%)'
        )
    
    def check_disk_usage(self, metric) -> bool:
        """Check disk usage and generate alert if needed"""
        return self._check_metric(
            metric_name='DISK_USAGE',
            value=metric.disk_usage,
            alert_type='DISK',
            message_template='Disk usage is {:.1f}% (threshold: {:.1f}%)'
        )
    
    def check_swap_usage(self, metric) -> bool:
        """Check swap usage and generate alert if needed"""
        if metric.swap_usage is None:
            return False
        
        return self._check_metric(
            metric_name='SWAP_USAGE',
            value=metric.swap_usage,
            alert_type='DISK',
            message_template='Swap usage is {:.1f}% (threshold: {:.1f}%)'
        )
    
    def _check_metric(self, metric_name: str, value: float, alert_type: str,
                     message_template: str) -> bool:
        """
        Check a single metric and generate alert if needed
        
        Args:
            metric_name (str): Name of the metric
            value (float): Current value
            alert_type (str): Alert type
            message_template (str): Message template
            
        Returns:
            bool: True if alert was generated
        """
        try:
            # Check if metric exceeds threshold
            alert_info = self.alert_manager.check_metric(metric_name, value)
            
            if not alert_info:
                # Resolve any active alerts if value is now normal
                self._resolve_alerts_if_normal(alert_type, value)
                return False
            
            # Check cooldown to avoid duplicate alerts
            cooldown_key = f"{alert_type}_{alert_info['severity']}"
            
            if self._is_in_cooldown(cooldown_key):
                self.logger.debug(f"Alert for {cooldown_key} is in cooldown")
                return False
            
            # Generate the alert message
            threshold = alert_info['threshold']
            message = message_template.format(value, threshold)
            
            # Create the alert
            if self.alert_manager.create_alert(
                alert_type=alert_type,
                message=message,
                severity=alert_info['severity'],
                metric_name=metric_name,
                current_value=value,
                threshold_value=threshold
            ):
                self._set_cooldown(cooldown_key)
                self.logger.warning(f"Alert generated: {alert_type} - {message}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking metric {metric_name}: {e}")
            return False
    
    def _is_in_cooldown(self, key: str) -> bool:
        """Check if alert is in cooldown period"""
        if key not in self.alert_cooldown:
            return False
        
        last_time = self.alert_cooldown[key]
        if datetime.now().timestamp() - last_time < self.cooldown_period:
            return True
        
        # Cooldown expired
        del self.alert_cooldown[key]
        return False
    
    def _set_cooldown(self, key: str):
        """Set cooldown for an alert"""
        self.alert_cooldown[key] = datetime.now().timestamp()
    
    def _resolve_alerts_if_normal(self, alert_type: str, current_value: float):
        """Resolve alerts if metric is back to normal"""
        try:
            session = db.get_session()
            
            # Get unresolved alerts for this type
            alerts = session.query(Alert).filter(
                Alert.alert_type == alert_type,
                Alert.is_resolved == False
            ).all()
            
            for alert in alerts:
                # Check if value is now within normal range
                threshold = self.alert_manager.get_threshold(
                    f"{alert_type}_USAGE"
                )
                
                if threshold and current_value < threshold.get('warning', 100):
                    # Value is now normal, resolve the alert
                    alert.is_resolved = True
                    alert.resolved_at = datetime.utcnow()
                    self.logger.info(f"Resolved alert: {alert_type}")
            
            session.commit()
            session.close()
            
        except Exception as e:
            self.logger.error(f"Error resolving alerts: {e}")
            if 'session' in locals():
                session.close()
    
    def process_batch_metrics(self, metrics: list):
        """
        Process multiple metrics and generate alerts
        
        Args:
            metrics (list): List of SystemMetric objects
        """
        total_alerts = 0
        
        for metric in metrics:
            alerts = self.check_metrics_and_generate_alerts(metric)
            total_alerts += len(alerts)
        
        if total_alerts > 0:
            self.logger.info(f"Generated {total_alerts} alerts")
    
    def cleanup_old_alerts(self):
        """Cleanup old alerts"""
        try:
            days = config.ALERT_RETENTION_DAYS
            deleted = self.alert_manager.cleanup_old_alerts(days)
            if deleted > 0:
                self.logger.info(f"Cleaned up {deleted} old alerts")
        except Exception as e:
            self.logger.error(f"Error cleaning up alerts: {e}")
    
    def get_alert_statistics(self, hours: int = 24) -> dict:
        """
        Get alert statistics
        
        Args:
            hours (int): Number of hours to analyze
            
        Returns:
            dict: Alert statistics
        """
        try:
            session = db.get_session()
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            total_alerts = session.query(Alert).filter(
                Alert.created_at >= cutoff_time
            ).count()
            
            critical_alerts = session.query(Alert).filter(
                Alert.created_at >= cutoff_time,
                Alert.severity == 'CRITICAL'
            ).count()
            
            warning_alerts = session.query(Alert).filter(
                Alert.created_at >= cutoff_time,
                Alert.severity == 'WARNING'
            ).count()
            
            resolved_alerts = session.query(Alert).filter(
                Alert.created_at >= cutoff_time,
                Alert.is_resolved == True
            ).count()
            
            unresolved_alerts = session.query(Alert).filter(
                Alert.is_resolved == False
            ).count()
            
            session.close()
            
            return {
                'total': total_alerts,
                'critical': critical_alerts,
                'warning': warning_alerts,
                'resolved': resolved_alerts,
                'unresolved': unresolved_alerts,
                'period_hours': hours
            }
            
        except Exception as e:
            self.logger.error(f"Error getting alert statistics: {e}")
            return {}


# Global alert service instance
alert_service = AlertService()


def process_alerts(metric):
    """
    Process alerts for a metric
    
    Args:
        metric: SystemMetric object
    """
    alert_service.check_metrics_and_generate_alerts(metric)
