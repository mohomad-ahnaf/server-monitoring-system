"""
Flask Dashboard Application
Main web application for monitoring system
"""

import os
import json
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from sqlalchemy import desc, and_

import config
from database.db_connection import db
from database.models import (
    SystemMetric, Alert, Log, AlertThreshold, TopProcess
)

# Configure logging
logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['JSON_SORT_KEYS'] = False


# ====================
# Helper Functions
# ====================

def get_latest_metric():
    """Get the latest system metric"""
    try:
        session_db = db.get_session()
        metric = session_db.query(SystemMetric).order_by(
            desc(SystemMetric.timestamp)
        ).first()
        session_db.close()
        return metric
    except Exception as e:
        logger.error(f"Error fetching latest metric: {e}")
        return None


def get_metric_history(hours=24):
    """Get metric history for the last N hours"""
    try:
        session_db = db.get_session()
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics = session_db.query(SystemMetric).filter(
            SystemMetric.timestamp >= cutoff_time
        ).order_by(SystemMetric.timestamp.asc()).all()
        
        session_db.close()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metric history: {e}")
        return []


def get_recent_alerts(limit=10, unresolved_only=False):
    """Get recent alerts"""
    try:
        session_db = db.get_session()
        query = session_db.query(Alert)
        
        if unresolved_only:
            query = query.filter(Alert.is_resolved == False)
        
        alerts = query.order_by(desc(Alert.created_at)).limit(limit).all()
        session_db.close()
        return alerts
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        return []


def get_recent_logs(limit=20, important_only=False):
    """Get recent logs"""
    try:
        session_db = db.get_session()
        query = session_db.query(Log)
        
        if important_only:
            query = query.filter(Log.is_important == True)
        
        logs = query.order_by(desc(Log.created_at)).limit(limit).all()
        session_db.close()
        return logs
    except Exception as e:
        logger.error(f"Error fetching logs: {e}")
        return []


def get_top_processes(limit=5):
    """Get top processes by resource usage"""
    try:
        session_db = db.get_session()
        
        # Get latest top processes
        latest_time = session_db.query(
            TopProcess.recorded_at
        ).order_by(desc(TopProcess.recorded_at)).first()
        
        if not latest_time:
            session_db.close()
            return {'cpu': [], 'memory': []}
        
        latest_time = latest_time[0]
        
        processes = session_db.query(TopProcess).filter(
            TopProcess.recorded_at == latest_time
        ).all()
        
        session_db.close()
        
        # Sort by CPU and memory
        top_cpu = sorted(processes, key=lambda x: x.cpu_usage or 0, reverse=True)[:limit]
        top_memory = sorted(processes, key=lambda x: x.memory_usage or 0, reverse=True)[:limit]
        
        return {
            'cpu': top_cpu,
            'memory': top_memory
        }
    except Exception as e:
        logger.error(f"Error fetching top processes: {e}")
        return {'cpu': [], 'memory': []}


# ====================
# Routes
# ====================

@app.route('/')
def index():
    """Dashboard home page"""
    try:
        metric = get_latest_metric()
        alerts = get_recent_alerts(limit=5)
        logs = get_recent_logs(limit=5)
        top_procs = get_top_processes()
        
        # Calculate uptime string
        uptime_str = "N/A"
        if metric and metric.uptime_seconds:
            days = metric.uptime_seconds // 86400
            hours = (metric.uptime_seconds % 86400) // 3600
            minutes = (metric.uptime_seconds % 3600) // 60
            uptime_str = f"{days}d {hours}h {minutes}m"
        
        return render_template(
            'index.html',
            metric=metric,
            alerts=alerts,
            logs=logs,
            top_procs=top_procs,
            uptime=uptime_str
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/api/metrics/latest')
def api_latest_metric():
    """API: Get latest metric"""
    metric = get_latest_metric()
    if metric:
        return jsonify(metric.to_dict())
    return jsonify({'error': 'No metrics available'}), 404


@app.route('/api/metrics/history')
def api_metric_history():
    """API: Get metric history"""
    hours = request.args.get('hours', 24, type=int)
    metrics = get_metric_history(hours)
    
    data = [m.to_dict() for m in metrics]
    return jsonify(data)


@app.route('/api/metrics/chart')
def api_metric_chart():
    """API: Get metrics formatted for charts"""
    hours = request.args.get('hours', 24, type=int)
    metrics = get_metric_history(hours)
    
    timestamps = []
    cpu_data = []
    memory_data = []
    disk_data = []
    
    for metric in metrics:
        timestamps.append(metric.timestamp.strftime('%H:%M:%S'))
        cpu_data.append(round(metric.cpu_usage, 1))
        memory_data.append(round(metric.memory_usage, 1))
        disk_data.append(round(metric.disk_usage, 1))
    
    return jsonify({
        'timestamps': timestamps,
        'cpu': cpu_data,
        'memory': memory_data,
        'disk': disk_data
    })


@app.route('/alerts')
def alerts():
    """Alerts page"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        session_db = db.get_session()
        total = session_db.query(Alert).count()
        
        alerts_list = session_db.query(Alert).order_by(
            desc(Alert.created_at)
        ).offset(offset).limit(per_page).all()
        
        session_db.close()
        
        total_pages = (total + per_page - 1) // per_page
        
        return render_template(
            'alerts.html',
            alerts=alerts_list,
            page=page,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error rendering alerts page: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/logs')
def logs():
    """Logs page"""
    try:
        page = request.args.get('page', 1, type=int)
        log_type = request.args.get('type', 'all')
        per_page = 50
        offset = (page - 1) * per_page
        
        session_db = db.get_session()
        query = session_db.query(Log)
        
        if log_type != 'all':
            query = query.filter(Log.log_type == log_type)
        
        total = query.count()
        
        logs_list = query.order_by(
            desc(Log.created_at)
        ).offset(offset).limit(per_page).all()
        
        session_db.close()
        
        total_pages = (total + per_page - 1) // per_page
        
        return render_template(
            'logs.html',
            logs=logs_list,
            page=page,
            total_pages=total_pages,
            log_type=log_type
        )
    except Exception as e:
        logger.error(f"Error rendering logs page: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/settings')
def settings():
    """Settings page"""
    try:
        session_db = db.get_session()
        thresholds = session_db.query(AlertThreshold).all()
        session_db.close()
        
        return render_template('settings.html', thresholds=thresholds)
    except Exception as e:
        logger.error(f"Error rendering settings page: {e}")
        return render_template('error.html', error=str(e)), 500


@app.route('/api/thresholds', methods=['GET', 'POST'])
def api_thresholds():
    """API: Get/update alert thresholds"""
    try:
        session_db = db.get_session()
        
        if request.method == 'GET':
            thresholds = session_db.query(AlertThreshold).all()
            data = [t.to_dict() for t in thresholds]
            session_db.close()
            return jsonify(data)
        
        elif request.method == 'POST':
            data = request.get_json()
            threshold_id = data.get('id')
            
            threshold = session_db.query(AlertThreshold).filter(
                AlertThreshold.id == threshold_id
            ).first()
            
            if threshold:
                threshold.warning_threshold = data.get('warning_threshold')
                threshold.critical_threshold = data.get('critical_threshold')
                threshold.enabled = data.get('enabled', True)
                threshold.updated_at = datetime.utcnow()
                
                session_db.commit()
                session_db.close()
                
                return jsonify({'status': 'success'})
            
            session_db.close()
            return jsonify({'error': 'Threshold not found'}), 404
    
    except Exception as e:
        logger.error(f"Error in thresholds API: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts/resolve/<int:alert_id>', methods=['POST'])
def api_resolve_alert(alert_id):
    """API: Resolve an alert"""
    try:
        session_db = db.get_session()
        alert = session_db.query(Alert).filter(Alert.id == alert_id).first()
        
        if alert:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()
            session_db.commit()
            session_db.close()
            
            return jsonify({'status': 'success'})
        
        session_db.close()
        return jsonify({'error': 'Alert not found'}), 404
    
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def api_stats():
    """API: Get system statistics"""
    try:
        metric = get_latest_metric()
        
        if not metric:
            return jsonify({'error': 'No metrics available'}), 404
        
        session_db = db.get_session()
        
        unresolved_alerts = session_db.query(Alert).filter(
            Alert.is_resolved == False
        ).count()
        
        total_logs = session_db.query(Log).count()
        error_logs = session_db.query(Log).filter(
            Log.level == 'ERROR'
        ).count()
        
        session_db.close()
        
        return jsonify({
            'cpu_usage': round(metric.cpu_usage, 1),
            'memory_usage': round(metric.memory_usage, 1),
            'disk_usage': round(metric.disk_usage, 1),
            'uptime_seconds': metric.uptime_seconds,
            'unresolved_alerts': unresolved_alerts,
            'total_logs': total_logs,
            'error_logs': error_logs,
            'timestamp': metric.timestamp.isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': str(e)}), 500


# ====================
# Error Handlers
# ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html', error='Internal server error'), 500


# ====================
# Context Processors
# ====================

@app.context_processor
def inject_config():
    """Inject config values to templates"""
    return {
        'app_name': 'System Monitoring Dashboard',
        'version': '1.0.0',
        'current_year': datetime.now().year
    }


# ====================
# Main
# ====================

if __name__ == '__main__':
    logger.info("Starting Flask Dashboard")
    logger.info(f"Database: {config.DB_TYPE}")
    logger.info(f"Host: {config.HOST}:{config.PORT}")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.FLASK_DEBUG
    )
