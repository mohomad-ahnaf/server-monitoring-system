# Docker Configuration for Server Monitoring System

## Quick Start

```bash
# Copy the repository
git clone https://github.com/yourusername/server-monitoring-system.git
cd server-monitoring-system

# Copy environment template
cp .env.example .env

# Start services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## Services

### PostgreSQL Database (`postgres`)
- **Image**: postgres:14-alpine
- **Port**: 5432
- **Volume**: postgres_data (persists database between restarts)
- **Health Check**: Automatic

### Flask Application (`app`)
- **Port**: 5000
- **Volumes**:
  - `./logs` - Application logs
  - `./data` - Data storage
  - `./backups` - Database backups
- **Depends On**: postgres (waits for database)
- **Health Check**: HTTP /api/stats

### PgAdmin (Optional Debug)
- **Port**: 5050
- **Profile**: debug
- **Usage**: `docker-compose --profile debug up`

## Environment Variables

Key environment variables in `.env`:

```bash
# Database
DB_USER=monitoring_user
DB_PASSWORD=password123
DB_NAME=monitoring_db

# Flask
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key

# Monitoring
MONITORING_INTERVAL=60
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90
```

## Common Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f app        # Flask app
docker-compose logs -f postgres   # Database

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache

# Run command in container
docker-compose exec app bash
docker-compose exec postgres psql -U monitoring_user -d monitoring_db

# Scale services (not applicable for this setup)
docker-compose up -d --scale app=2
```

## Troubleshooting

### Database connection issues
```bash
# Check database status
docker-compose ps

# Check database logs
docker-compose logs postgres

# Connect to database
docker-compose exec postgres psql -U monitoring_user -d monitoring_db
```

### Flask app not starting
```bash
# Check app logs
docker-compose logs -f app

# Restart app
docker-compose restart app
```

### Reset everything
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

For production use:

1. Change `FLASK_ENV` to `production`
2. Update `SECRET_KEY` to a secure value
3. Use strong database passwords
4. Configure reverse proxy (nginx/Apache)
5. Use SSL/TLS certificates
6. Set up proper monitoring and backups
7. Use environment-specific `.env` files

## Monitoring Container Health

```bash
# Check container status
docker-compose ps

# View detailed container info
docker inspect <container_id>

# Monitor container stats
docker stats
```

## Backup and Restore

### Backup database
```bash
docker-compose exec postgres pg_dump -U monitoring_user monitoring_db > backup.sql
```

### Restore database
```bash
docker-compose exec -T postgres psql -U monitoring_user monitoring_db < backup.sql
```

## Docker Network

Services communicate over the `monitoring-network`:
- App connects to: `postgres:5432`
- External access: `localhost:5000` (app), `localhost:5432` (postgres)

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Python Docker Hub](https://hub.docker.com/_/python)
