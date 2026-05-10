# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Response Format

All API responses are in JSON format:

```json
{
  "success": true,
  "data": {},
  "message": "Success message",
  "timestamp": "2024-01-15T10:30:45.123Z"
}
```

## Authentication

Currently, the API has no authentication. For production deployment, implement JWT or API keys.

---

## Endpoints

### Metrics

#### Get Latest Metrics
```
GET /api/metrics/latest
```

**Response:**
```json
{
  "success": true,
  "data": {
    "cpu_usage": 45.2,
    "memory_usage": 62.1,
    "disk_usage": 38.5,
    "uptime": 3600,
    "timestamp": "2024-01-15T10:30:45Z"
  }
}
```

#### Get Metrics History
```
GET /api/metrics/history?hours=24&limit=100
```

**Query Parameters:**
- `hours`: Hours of history (default: 24)
- `limit`: Maximum records (default: 100)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2024-01-15T10:30:45Z",
      "cpu_usage": 45.2,
      "memory_usage": 62.1,
      "disk_usage": 38.5
    }
  ]
}
```

---

### Alerts

#### Get All Alerts
```
GET /api/alerts?status=unresolved&limit=20&offset=0
```

**Query Parameters:**
- `status`: 'unresolved', 'resolved', or 'all' (default: all)
- `limit`: Records per page (default: 20)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 123,
      "metric_type": "cpu",
      "current_value": 87.5,
      "threshold": 85,
      "severity": "critical",
      "status": "unresolved",
      "message": "CPU usage exceeded critical threshold",
      "created_at": "2024-01-15T10:30:45Z",
      "resolved_at": null
    }
  ],
  "pagination": {
    "total": 42,
    "limit": 20,
    "offset": 0
  }
}
```

#### Resolve Alert
```
POST /api/alerts/{id}/resolve
```

**Body:**
```json
{
  "resolution_notes": "Issue fixed"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "status": "resolved",
    "resolved_at": "2024-01-15T10:35:20Z"
  }
}
```

#### Get Alert Statistics
```
GET /api/alerts/stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_alerts": 42,
    "unresolved_count": 5,
    "resolved_count": 37,
    "by_severity": {
      "critical": 2,
      "warning": 3
    }
  }
}
```

---

### Thresholds

#### Get Current Thresholds
```
GET /api/thresholds
```

**Response:**
```json
{
  "success": true,
  "data": {
    "cpu": {
      "warning": 80,
      "critical": 85
    },
    "memory": {
      "warning": 85,
      "critical": 90
    },
    "disk": {
      "warning": 90,
      "critical": 95
    }
  }
}
```

#### Update Thresholds
```
POST /api/thresholds
```

**Body:**
```json
{
  "cpu_warning": 75,
  "cpu_critical": 90,
  "memory_warning": 80,
  "memory_critical": 95,
  "disk_warning": 85,
  "disk_critical": 98
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "updated_thresholds": 6,
    "timestamp": "2024-01-15T10:35:20Z"
  }
}
```

---

### System

#### Get System Statistics
```
GET /api/stats
```

**Response:**
```json
{
  "success": true,
  "data": {
    "hostname": "server-01",
    "os": "Linux",
    "cpu_count": 8,
    "total_memory": "16GB",
    "current_metrics": {
      "cpu_usage": 45.2,
      "memory_usage": 62.1,
      "disk_usage": 38.5
    },
    "alerts": {
      "total": 42,
      "unresolved": 5
    },
    "uptime": "15 days, 3 hours"
  }
}
```

#### Health Check
```
GET /api/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "collector": "running",
    "timestamp": "2024-01-15T10:35:20Z"
  }
}
```

---

### Logs

#### Get Logs
```
GET /api/logs?source=syslog&level=error&limit=50&offset=0
```

**Query Parameters:**
- `source`: 'syslog' or 'auth' (default: all)
- `level`: Log level filter (default: all)
- `limit`: Records per page (default: 50)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 456,
      "source": "syslog",
      "level": "ERROR",
      "message": "Kernel out of memory",
      "timestamp": "2024-01-15T10:30:20Z",
      "is_important": true
    }
  ]
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid query parameter",
  "message": "limit must be a positive integer"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Resource not found",
  "message": "Alert with id 999 not found"
}
```

### 500 Server Error
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "Database connection failed"
}
```

---

## Rate Limiting

Currently no rate limiting. Recommended for production:
- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## Examples

### cURL Examples

**Get latest metrics:**
```bash
curl http://localhost:5000/api/metrics/latest
```

**Get unresolved alerts:**
```bash
curl http://localhost:5000/api/alerts?status=unresolved
```

**Resolve alert:**
```bash
curl -X POST http://localhost:5000/api/alerts/123/resolve \
  -H "Content-Type: application/json" \
  -d '{"resolution_notes": "Fixed"}'
```

**Update thresholds:**
```bash
curl -X POST http://localhost:5000/api/thresholds \
  -H "Content-Type: application/json" \
  -d '{"cpu_warning": 75, "cpu_critical": 90}'
```

### Python Examples

```python
import requests

# Get metrics
response = requests.get('http://localhost:5000/api/metrics/latest')
metrics = response.json()['data']
print(f"CPU: {metrics['cpu_usage']}%")

# Get alerts
response = requests.get('http://localhost:5000/api/alerts')
alerts = response.json()['data']
print(f"Total alerts: {len(alerts)}")

# Resolve alert
response = requests.post('http://localhost:5000/api/alerts/123/resolve',
  json={'resolution_notes': 'Issue fixed'})
```

---

## Changelog

### v1.0.0
- Initial API release
- Metrics endpoints
- Alerts management
- Thresholds configuration
- System stats
