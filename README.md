# Server Monitoring & Log Analysis System

A professional Linux-based infrastructure monitoring and log analysis system built with Python, Flask, PostgreSQL, and Docker. This system monitors server health, collects logs, stores metrics in a SQL database, and provides a real-time web dashboard.

## 🎯 Features

### System Monitoring
- **CPU Usage Tracking** - Real-time CPU utilization monitoring
- **Memory Usage** - RAM and swap memory monitoring
- **Disk Usage** - Partition and filesystem monitoring
- **Process Monitoring** - Top processes by CPU and memory
- **Uptime Tracking** - System uptime and boot time
- **Network Monitoring** - Network interface statistics (optional)

### Log Analysis
- Automatic log file parsing from `/var/log/`
- Detection of:
  - Failed login attempts
  - Critical errors
  - Warning messages
  - Service failures
- Persistent log storage in database

### Alert System
- Automatic alerts when thresholds are exceeded:
  - CPU usage > 80%
  - Memory usage > 85%
  - Disk usage > 90%
- Alert severity levels (Critical, Warning, Info)
- Historical alert tracking

### Web Dashboard
- Real-time system metrics display
- Historical data visualization with charts
- Alert status and recent alerts
- Recent log entries
- System statistics cards
- Responsive design for mobile/desktop

### Automation
- Bash scripts for service management
- Database backup automation
- Cron job integration
- Easy startup and shutdown

### Containerization
- Docker support for easy deployment
- Docker Compose for multi-container orchestration
- PostgreSQL database container
- Flask application container

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| OS | Linux (Ubuntu/Debian) |
| Backend | Python 3.9+ |
| Web Framework | Flask 2.3 |
| Database | PostgreSQL 14+ |
| ORM | SQLAlchemy |
| Frontend | HTML5/CSS3, Chart.js |
| Containerization | Docker & Docker Compose |
| System Monitoring | psutil |
| Scripting | Bash |

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended for easy setup)
- OR:
  - Linux (Ubuntu 20.04+ or Debian 11+)
  - Python 3.9+
  - PostgreSQL 12+
  - pip (Python package manager)

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/server-monitoring-system.git
cd server-monitoring-system

# Copy environment file
cp .env.example .env

# Start the system
docker-compose up -d

# View logs
docker-compose logs -f
```

The dashboard will be available at `http://localhost:5000`

### Option 2: Manual Setup (Linux)

```bash
# Clone the repository
git clone https://github.com/yourusername/server-monitoring-system.git
cd server-monitoring-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Set up database
psql -U postgres -f database/schema.sql

# Initialize database
python database/db_connection.py

# Start monitoring service
python monitoring/collector.py &

# Start Flask dashboard
python dashboard/app.py
```

The dashboard will be available at `http://localhost:5000`

## 📁 Project Structure

```
server-monitoring-system/
├── monitoring/               # System monitoring modules
│   ├── cpu_monitor.py
│   ├── memory_monitor.py
│   ├── disk_monitor.py
│   ├── process_monitor.py
│   ├── uptime_monitor.py
│   ├── base_monitor.py
│   └── collector.py          # Main collector script
│
├── database/                 # Database-related files
│   ├── schema.sql           # Database schema
│   ├── db_connection.py      # Database connection
│   └── models.py            # SQLAlchemy models
│
├── dashboard/               # Flask web application
│   ├── app.py              # Main Flask app
│   ├── templates/          # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── alerts.html
│   │   ├── logs.html
│   │   └── settings.html
│   └── static/             # CSS and JavaScript
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── dashboard.js
│
├── scripts/                # Bash automation scripts
│   ├── start_monitoring.sh
│   ├── stop_monitoring.sh
│   ├── backup.sh
│   └── setup.sh
│
├── docker/                 # Docker configuration
│   ├── Dockerfile          # Flask app container
│   └── docker-compose.yml  # Multi-container setup
│
├── tests/                  # Unit tests
│   └── test_monitors.py
│
├── config.py              # Configuration file
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## 🗄️ Database Schema

### system_metrics
Stores system performance metrics:
- CPU usage percentage
- Memory usage percentage
- Disk usage percentage
- System uptime
- Timestamp

### alerts
Stores generated alerts:
- Alert type (CPU, Memory, Disk)
- Message
- Severity level (Critical, Warning, Info)
- Timestamp

### logs
Stores parsed system logs:
- Log type (Syslog, Auth, etc.)
- Message content
- Timestamp

## 📊 Dashboard Views

### Dashboard (Home)
- System overview cards
- Real-time CPU, Memory, Disk usage gauges
- Historical charts (24-hour view)
- Current system status
- Quick stats

### Alerts
- List of recent alerts
- Severity indicators
- Timestamp information
- Alert filtering options

### Logs
- Parsed system logs
- Log type filtering
- Search functionality
- Export option

### Settings
- Configure alert thresholds
- Update monitoring intervals
- Database connection settings
- System preferences

## ⚙️ Configuration

Edit the `.env` file to configure:

```env
# Database
DB_HOST=localhost
DB_USER=monitoring_user
DB_PASSWORD=your_password
DB_NAME=monitoring_db

# Thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90

# Intervals
MONITORING_INTERVAL=60
```

## 📝 Usage Examples

### Running the Collector
```bash
python monitoring/collector.py
```

### Running the Dashboard
```bash
python dashboard/app.py
```

### Automated Backup
```bash
bash scripts/backup.sh
```

### Start Everything
```bash
bash scripts/start_monitoring.sh
```

## 🐛 Troubleshooting

### Database connection errors
- Verify PostgreSQL is running
- Check credentials in `.env` file
- Ensure database exists: `createdb monitoring_db`

### Permission denied for log files
- Run with appropriate permissions (may need `sudo`)
- Or copy logs to readable location

### Docker issues
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## 📚 Learning Goals

This project demonstrates:
- ✅ Linux administration and log analysis
- ✅ Python scripting and modules
- ✅ SQL database design and operations
- ✅ System monitoring and metrics collection
- ✅ Web development with Flask
- ✅ Docker containerization
- ✅ DevOps and SRE best practices
- ✅ Bash scripting and automation
- ✅ Real-time data visualization

## 🎓 Suitable For

- SRE (Site Reliability Engineering) internships
- DevOps internships
- Application Management roles
- Infrastructure Engineering positions
- System Administration roles

## 📈 Future Enhancements

- [ ] Email alert notifications
- [ ] SMS alerts
- [ ] Multi-server monitoring
- [ ] Custom metric plugins
- [ ] Grafana integration
- [ ] Prometheus metrics export
- [ ] Slack/Teams notifications
- [ ] Advanced log analytics with ML
- [ ] Performance trending reports
- [ ] API authentication and RBAC

## 📄 License

MIT License - See LICENSE file for details

## 👤 Author

Your Name - Created for SRE/DevOps Portfolio

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the logs in `logs/` directory
3. Open an issue on GitHub
4. Refer to inline code comments and documentation

---

**Status:** ✅ In Development
**Last Updated:** 2024
**Version:** 1.0.0-dev

Happy Monitoring! 🚀
