"""
Configuration file for Server Monitoring System
Loads environment variables and provides configuration constants
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ====================
# Database Configuration
# ====================
DB_TYPE = os.getenv('DB_TYPE', 'postgresql')  # postgresql or mysql
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'monitoring_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password123')
DB_NAME = os.getenv('DB_NAME', 'monitoring_db')

# SQLAlchemy Database URL
if DB_TYPE == 'postgresql':
    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
elif DB_TYPE == 'mysql':
    DATABASE_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
else:
    DATABASE_URL = 'sqlite:///monitoring.db'

# ====================
# Flask Configuration
# ====================
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', '5000'))

# ====================
# Monitoring Configuration
# ====================
MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', '60'))  # seconds
CPU_THRESHOLD = float(os.getenv('CPU_THRESHOLD', '80'))  # percentage
MEMORY_THRESHOLD = float(os.getenv('MEMORY_THRESHOLD', '85'))  # percentage
DISK_THRESHOLD = float(os.getenv('DISK_THRESHOLD', '90'))  # percentage

# ====================
# Log Monitoring Configuration
# ====================
LOG_FILES = [
    '/var/log/syslog',
    '/var/log/auth.log',
    '/var/log/dmesg',
]
LOG_CHECK_INTERVAL = int(os.getenv('LOG_CHECK_INTERVAL', '30'))  # seconds
LOG_ERROR_PATTERNS = ['ERROR', 'CRITICAL', 'FATAL', 'Failed password']
LOG_WARNING_PATTERNS = ['WARNING', 'WARN', 'Connection refused']

# ====================
# Alert Configuration
# ====================
ALERT_RETENTION_DAYS = int(os.getenv('ALERT_RETENTION_DAYS', '30'))
METRICS_RETENTION_DAYS = int(os.getenv('METRICS_RETENTION_DAYS', '90'))
ENABLE_EMAIL_ALERTS = os.getenv('ENABLE_EMAIL_ALERTS', 'False').lower() == 'true'
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
ALERT_EMAIL = os.getenv('ALERT_EMAIL', '')

# ====================
# Paths and Directories
# ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(BASE_DIR, 'data')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# Create directories if they don't exist
for directory in [LOG_DIR, DATA_DIR, BACKUP_DIR]:
    os.makedirs(directory, exist_ok=True)

# ====================
# Logging Configuration
# ====================
LOG_FILE = os.path.join(LOG_DIR, 'system.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
