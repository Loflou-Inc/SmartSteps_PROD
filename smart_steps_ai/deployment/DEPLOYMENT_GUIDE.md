# Smart Steps AI Deployment Guide

This guide provides detailed instructions for deploying and maintaining the Smart Steps AI Professional Persona module in various environments.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Deployment Options](#deployment-options)
3. [Docker Deployment](#docker-deployment)
4. [Standard Deployment](#standard-deployment)
5. [Configuration](#configuration)
6. [Monitoring](#monitoring)
7. [Maintenance](#maintenance)
8. [Backup and Recovery](#backup-and-recovery)
9. [Updates](#updates)
10. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware Requirements

- **CPU**: 4+ cores recommended (2 cores minimum)
- **RAM**: 8+ GB recommended (4 GB minimum)
- **Disk**: 20+ GB of free space recommended
- **Network**: Stable internet connection for API access

### Software Requirements

- **Operating System**: 
  - Linux: Ubuntu 20.04+, CentOS 8+, or Debian 11+
  - Windows: Windows 10/11 or Windows Server 2019+
  - macOS: macOS 11 (Big Sur) or newer
- **Dependencies**:
  - Python 3.9+ (Python 3.10 recommended)
  - Git
  - Docker & Docker Compose (for containerized deployment)

## Deployment Options

The Smart Steps AI module can be deployed in multiple ways depending on your environment and requirements:

1. **Docker Deployment**: Recommended for production. Provides isolated environment and easier maintenance.
2. **Standard Deployment**: Traditional installation on the host system.
3. **Development Setup**: For testing and development purposes.

## Docker Deployment

Docker deployment is the recommended method for production environments, providing isolated runtime environments and simplified management.

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

### Deployment Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/smart-steps-ai.git
   cd smart-steps-ai
   ```

2. **Configure environment variables**:
   Create a `.env` file in the root directory based on the example:
   ```bash
   cp deployment/config/production.env .env
   # Edit .env with appropriate values
   ```

3. **Configure monitoring**:
   ```bash
   cp deployment/config/monitoring.yaml config/monitoring.yaml
   # Edit config/monitoring.yaml if needed
   ```

4. **Start the services**:
   ```bash
   docker-compose -f deployment/docker-compose.yml up -d
   ```

5. **Verify the deployment**:
   ```bash
   # Check that containers are running
   docker-compose -f deployment/docker-compose.yml ps
   
   # Check API health endpoint
   curl http://localhost:9500/api/v1/admin/health
   ```

### Docker Deployment Architecture

The Docker deployment consists of the following services:

- **api**: The main Smart Steps AI API service
- **monitoring**: System monitoring service
- **nginx**: (Optional) Web server for TLS termination and request routing

## Standard Deployment

For environments where Docker isn't available or preferred, you can deploy directly on the host system.

### Prerequisites

- Python 3.9+
- virtualenv or conda (recommended)
- Git

### Deployment Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-org/smart-steps-ai.git
   cd smart-steps-ai
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # On Linux/macOS
   source venv/bin/activate
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e .
   ```

4. **Configure environment**:
   ```bash
   cp deployment/config/production.env .env
   # Edit .env with appropriate values
   ```

5. **Run the API server**:
   ```bash
   # Windows
   run_api_server.bat
   
   # Linux/macOS
   python run_api_server.py
   ```

6. **Start monitoring system** (optional):
   ```bash
   python deployment/monitoring_system.py start
   ```

7. **Verify the deployment**:
   ```bash
   curl http://localhost:9500/api/v1/admin/health
   ```

## Configuration

Smart Steps AI uses a flexible configuration system with multiple options to adapt to different environments.

### Environment Variables

The `.env` file contains the main configuration settings. Here are the critical settings:

```
# API Settings
API_SECRET_KEY=your-secure-key
ALLOWED_ORIGINS=https://your-app.example.com

# AI Provider Settings
DEFAULT_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key

# Security Settings
JWT_ALGORITHM=HS256
JWT_EXPIRY=86400
```

### Configuration Files

Additional configuration files are located in the `config/` directory:

- **app_config.yaml**: General application settings
- **monitoring.yaml**: Monitoring system configuration
- **personas/**: Persona definition files

### Environment-Specific Configs

The `deployment/config/` directory contains pre-configured environment files:

- **development.env**: Local development settings
- **testing.env**: Testing environment settings
- **production.env**: Production deployment settings

## Monitoring

The Smart Steps AI monitoring system provides comprehensive monitoring of system health, performance metrics, and automated alerts.

### Starting the Monitoring System

```bash
# Docker deployment
docker-compose -f deployment/docker-compose.yml up -d monitoring

# Standard deployment
python deployment/monitoring_system.py start
```

### Monitoring Features

- **System metrics**: CPU, memory, disk usage
- **API performance**: Response times, error rates
- **Alert system**: Email and SMS notifications
- **Maintenance automation**: Log rotation, database optimization

### Monitoring Dashboard

Access the monitoring dashboard at:
```
http://your-server:9500/api/v1/admin/metrics
```

## Maintenance

Regular maintenance tasks help ensure optimal performance and reliability.

### Automated Maintenance

The monitoring system automatically performs maintenance tasks based on the schedule defined in `monitoring.yaml`:

- **Log rotation**: Cleans up old log files
- **Database optimization**: VACUUM and ANALYZE operations
- **Cache clearing**: Periodic memory cache cleanup

### Manual Maintenance

You can manually trigger maintenance tasks:

```bash
# Docker deployment
docker-compose -f deployment/docker-compose.yml exec api python -m smart_steps_ai.utils.maintenance

# Standard deployment
python -m smart_steps_ai.utils.maintenance
```

## Backup and Recovery

Regular backups are essential for data safety and disaster recovery.

### Automated Backups

The system performs automated backups:

```bash
# Docker deployment
docker-compose -f deployment/docker-compose.yml exec api python deployment/auto_update.py check

# Standard deployment
python deployment/auto_update.py check
```

### Manual Backup

```bash
# Docker deployment
docker-compose -f deployment/docker-compose.yml exec api python -m smart_steps_ai.utils.maintenance backup

# Standard deployment
python -m smart_steps_ai.utils.maintenance backup
```

### Backup Contents

Each backup includes:
- Database snapshot
- Configuration files
- Logs (optional)

### Recovery Process

To restore from a backup:

```bash
# Docker deployment
docker-compose -f deployment/docker-compose.yml exec api python deployment/auto_update.py rollback --version 1.2.3

# Standard deployment
python deployment/auto_update.py rollback --version 1.2.3
```

## Updates

The Smart Steps AI system includes an automated update system to simplify maintenance.

### Checking for Updates

```bash
# Docker deployment
docker-compose -f deployment/docker-compose.yml exec api python deployment/auto_update.py check

# Standard deployment
python deployment/auto_update.py check
```

### Performing Updates

```bash
# Docker deployment
docker-compose -f deployment/docker-compose.yml exec api python deployment/auto_update.py update

# Standard deployment
python deployment/auto_update.py update
```

### Update Process

The update process includes:
1. Checking for new versions
2. Creating a backup
3. Updating application code
4. Migrating the database if needed
5. Restarting services

### Rolling Back

If an update causes issues, you can roll back:

```bash
# Docker deployment
docker-compose -f deployment/docker-compose.yml exec api python deployment/auto_update.py rollback

# Standard deployment
python deployment/auto_update.py rollback
```

## Troubleshooting

Common issues and their solutions:

### API Server Won't Start

**Check:**
- Database connectivity
- Environment variables
- Port availability
- Log files for detailed errors

### Authentication Issues

**Check:**
- API_SECRET_KEY consistency
- JWT token validity
- ALLOWED_ORIGINS setting

### Performance Problems

**Check:**
- System resource usage
- Database performance
- Monitoring metrics
- Cache configuration

### Monitoring System Issues

**Check:**
- Configuration file
- Log files
- Network connectivity
- Port availability

### For Additional Help

If you encounter issues not covered in this guide:

1. Check the logs:
   ```bash
   # Docker deployment
   docker-compose -f deployment/docker-compose.yml logs api
   
   # Standard deployment
   cat logs/smart_steps.log
   ```

2. Contact support:
   - Email: support@smartsteps.example.com
   - Issue tracker: https://github.com/your-org/smart-steps-ai/issues
