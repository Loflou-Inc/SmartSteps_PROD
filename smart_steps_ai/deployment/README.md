# Smart Steps AI Deployment

This directory contains all the components needed to deploy and maintain the Smart Steps AI Professional Persona module in various environments.

## Directory Structure

- **Dockerfile**: Container definition for the API service
- **Dockerfile.monitoring**: Container definition for the monitoring service
- **docker-compose.yml**: Docker Compose configuration for orchestrating services
- **auto_update.py**: Script for managing application updates and rollbacks
- **maintenance.sh**: Shell script for scheduled maintenance tasks
- **DEPLOYMENT_GUIDE.md**: Comprehensive deployment documentation
- **config/**: Environment-specific configuration files
  - **production.env**: Production environment settings
  - **development.env**: Development environment settings
  - **testing.env**: Testing environment settings
  - **monitoring.yaml**: Monitoring system configuration
- **nginx/**: Nginx configuration for web server and reverse proxy
  - **smartsteps.conf**: Nginx server configuration

## Deployment Options

The Smart Steps AI module supports three deployment scenarios:

1. **Docker Deployment** (Recommended for Production)
   - Uses Docker and Docker Compose to run services in containers
   - Provides isolation, scalability, and easier maintenance
   - Includes monitoring, automatic updates, and health checks

2. **Standard Deployment**
   - Traditional installation directly on the server
   - Suitable for environments where containers aren't available
   - Includes same functionality as Docker deployment

3. **Development Setup**
   - Lightweight configuration for development environments
   - Uses mock providers by default to avoid API costs
   - Includes additional debugging tools

## Quick Start

For detailed instructions, see the [Deployment Guide](DEPLOYMENT_GUIDE.md).

### Docker Deployment

```bash
# Copy and configure environment file
cp config/production.env ../.env
# Edit .env with your settings

# Start services
docker-compose -f docker-compose.yml up -d

# Verify deployment
curl http://localhost:9500/api/v1/admin/health
```

### Standard Deployment

```bash
# Navigate to project root
cd ..

# Copy and configure environment file
cp deployment/config/production.env .env
# Edit .env with your settings

# Install dependencies
pip install -e .

# Start API server
python run_api_server.py

# Start monitoring (optional)
python deployment/monitoring_system.py start
```

## Maintenance

The deployment includes several tools for system maintenance:

- **Automated monitoring**: Real-time monitoring of system health and performance
- **Scheduled maintenance**: Automated tasks for log rotation, database optimization, etc.
- **Update management**: Safe application updates with automatic rollback capability
- **Backup system**: Regular backups with retention policies

For scheduled maintenance, set up a cron job to run the maintenance script:

```bash
# Run daily at 2:00 AM
0 2 * * * /opt/smart_steps_ai/deployment/maintenance.sh
```

## Release Management

The `release_manager.py` script provides tools for managing releases:

```bash
# Create a new release (incrementing version number)
python release_manager.py create-release --minor

# Generate release notes
python release_manager.py generate-notes

# Build a package
python release_manager.py build-package

# Full release process
python release_manager.py full-release --patch
```

## Support

For assistance with deployment issues:

- Consult the [Deployment Guide](DEPLOYMENT_GUIDE.md)
- Check logs in the `logs/` directory
- Contact support at support@smartsteps.example.com