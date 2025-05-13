# Smart Steps AI Professional Persona Module - Administrator Guide

## Introduction

This guide provides comprehensive instructions for administrators responsible for managing and maintaining the Smart Steps AI Professional Persona module. It covers installation, configuration, user management, monitoring, and troubleshooting.

## Table of Contents

1. [System Overview](#system-overview)
2. [Installation and Setup](#installation-and-setup)
3. [Configuration Management](#configuration-management)
4. [User Administration](#user-administration)
5. [Security Management](#security-management)
6. [Performance Tuning](#performance-tuning)
7. [Backup and Recovery](#backup-and-recovery)
8. [Monitoring and Alerts](#monitoring-and-alerts)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance Tasks](#maintenance-tasks)

## System Overview

### Architecture

The Smart Steps AI Professional Persona module consists of the following components:

1. **API Server**: Provides RESTful API endpoints for all functionality
2. **Persona Manager**: Handles AI persona definitions and behaviors
3. **Session Manager**: Manages therapy/facilitation sessions
4. **Memory System**: Stores and retrieves contextual information
5. **Analysis Engine**: Generates insights and reports
6. **Database Layer**: Persists data (file-based or MongoDB)
7. **Unity Integration**: Client-side components for Unity applications

### Data Flow

```
Unity Client <--> API Server <--> Core Components <--> Storage
                                      ^
                                      |
                            External AI Providers
```

### Key Files and Directories

- **Configuration**: `/etc/smartsteps/` (Linux) or `C:\ProgramData\SmartSteps\Config\` (Windows)
- **Logs**: `/var/log/smartsteps/` (Linux) or `C:\ProgramData\SmartSteps\Logs\` (Windows)
- **Data**: `/var/lib/smartsteps/` (Linux) or `C:\ProgramData\SmartSteps\` (Windows)
- **Application**: `/opt/smartsteps/` (Linux) or `C:\Program Files\SmartSteps\` (Windows)

## Installation and Setup

For detailed installation instructions, refer to the [Deployment Guide](DeploymentGuide.md).

### Quick Reference: Linux Installation

```bash
# Install prerequisites
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git

# Download and run installer
wget https://example.com/smartsteps/install_server.sh
chmod +x install_server.sh
sudo ./install_server.sh

# Verify installation
systemctl status smartsteps.service
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8543/api/health
```

### Quick Reference: Windows Installation

```powershell
# Run PowerShell as Administrator
cd C:\Path\To\Installer
.\install_server.ps1

# Verify installation
Get-Service -Name SmartStepsAI
```

### Post-Installation Verification

After installation, verify the system using the following checks:

1. **Service Status**: Ensure the service is running and enabled on startup
2. **API Access**: Test the API health endpoint
3. **Log Files**: Check for any error messages in the logs
4. **Data Directory**: Verify data directories are properly created
5. **Default Personas**: Confirm default personas are available

## Configuration Management

### Configuration Files

The system uses YAML configuration files stored in the configuration directory:

- **config.yaml**: Main configuration file
- **security.yaml**: Security settings
- **secrets.yaml**: API keys and sensitive information
- **personas/*.json**: Persona definition files

### Updating Configuration

To modify configuration:

1. Edit the appropriate configuration file
2. Save the changes
3. Restart the service to apply changes:
   - **Linux**: `sudo systemctl restart smartsteps.service`
   - **Windows**: `Restart-Service SmartStepsAI`

### Configuration Validation

Always validate your configuration changes before applying them:

```bash
# Linux
sudo -u smartsteps python -m smart_steps_ai.tools.validate_config --config /etc/smartsteps/config.yaml

# Windows
python -m smart_steps_ai.tools.validate_config --config C:\ProgramData\SmartSteps\Config\config.yaml
```

### Environment Variables

The following environment variables can override configuration settings:

| Variable | Description | Example |
|----------|-------------|---------|
| SMARTSTEPS_ENV | Deployment environment | production |
| SMARTSTEPS_CONFIG_DIR | Configuration directory | /etc/smartsteps |
| SMARTSTEPS_LOG_LEVEL | Logging level | INFO |
| SMARTSTEPS_API_PORT | API server port | 8543 |
| SMARTSTEPS_WORKERS | Number of worker processes | 4 |

## User Administration

### User Management

Administrators can manage users through the API or CLI:

```bash
# Create a new user
python -m smart_steps_ai.cli user create --username john.doe --role therapist --email john.doe@example.com

# List all users
python -m smart_steps_ai.cli user list

# Update user role
python -m smart_steps_ai.cli user update --username john.doe --role supervisor

# Delete a user
python -m smart_steps_ai.cli user delete --username john.doe
```

### Role Management

The system has the following predefined roles:

| Role | Description | Permissions |
|------|-------------|-------------|
| admin | System administrator | Full system access |
| supervisor | Supervises therapists | Session review, reporting, user management |
| therapist | Conducts therapy sessions | Session management, client management, basic reporting |
| facilitator | Guides client interactions | Session participation, limited client data access |
| researcher | Analyzes anonymized data | Read-only access to anonymized data |

### Custom Roles

To create custom roles with specific permissions:

```bash
# Create a custom role
python -m smart_steps_ai.cli role create --name senior_therapist --inherit therapist --add-permissions "report:advanced,client:delete"

# List all roles
python -m smart_steps_ai.cli role list

# View role details
python -m smart_steps_ai.cli role view --name senior_therapist
```

## Security Management

### API Key Management

API keys are used for authenticating API requests:

```bash
# Generate a new API key
python -m smart_steps_ai.cli apikey generate --name "Unity Client" --expiry 365

# List all API keys
python -m smart_steps_ai.cli apikey list

# Revoke an API key
python -m smart_steps_ai.cli apikey revoke --id sk_ss_abc123
```

### Multi-Factor Authentication

Configure MFA settings in the security.yaml file:

```yaml
security:
  authentication:
    mfa:
      enabled: true
      required_for_roles: ["admin", "supervisor"]
      methods:
        - type: "totp"
          enabled: true
        - type: "email"
          enabled: true
```

### Audit Logging

All security-related actions are logged in the security audit log:

```bash
# View security audit log
# Linux
sudo cat /var/log/smartsteps/security.log

# Windows
Get-Content -Path "C:\ProgramData\SmartSteps\Logs\security.log"
```

### Security Scanning

Run regular security scans to identify potential vulnerabilities:

```bash
# Run security scan
python -m smart_steps_ai.tools.security_scan --config /etc/smartsteps/config.yaml
```

## Performance Tuning

### Worker Configuration

Adjust the number of worker processes based on your hardware:

```yaml
server:
  workers: 4  # Set to number of CPU cores
  worker_timeout_seconds: 60
  worker_connections: 1000
```

### Caching Configuration

Configure caching to improve performance:

```yaml
performance:
  cache:
    enabled: true
    memory_cache_size_mb: 256
    disk_cache_enabled: true
    disk_cache_path: "/var/lib/smartsteps/cache"
    ttl_seconds: 3600
```

### Database Optimization

For file-based storage, configure optimization parameters:

```yaml
storage:
  type: "file"
  optimization:
    auto_vacuum: true
    index_optimization: true
    compact_on_startup: true
```

For MongoDB storage, configure connection pooling:

```yaml
storage:
  type: "mongodb"
  connection:
    host: "localhost"
    port: 27017
    database: "smartsteps"
    max_pool_size: 100
    min_pool_size: 10
    max_idle_time_ms: 10000
```

### Memory Management

Configure memory usage limits:

```yaml
performance:
  memory:
    max_memory_percent: 80
    vector_compression: true
    batch_processing: true
    garbage_collection_interval: 300
```

## Backup and Recovery

### Automated Backups

Configure automated backups in the configuration:

```yaml
backup:
  enabled: true
  schedule: "0 2 * * *"  # Daily at 2 AM (cron format)
  retention_days: 30
  destination: "/backup/smartsteps"
  compression: true
  include_config: true
  include_logs: false
```

### Manual Backups

Perform manual backups using the CLI tool:

```bash
# Create a full backup
python -m smart_steps_ai.cli backup create --output /path/to/backup

# Backup only data
python -m smart_steps_ai.cli backup create --data-only --output /path/to/backup

# Backup only configuration
python -m smart_steps_ai.cli backup create --config-only --output /path/to/backup
```

### Restore Procedure

To restore from a backup:

```bash
# Stop the service
sudo systemctl stop smartsteps.service  # Linux
Stop-Service SmartStepsAI  # Windows

# Restore from backup
python -m smart_steps_ai.cli backup restore --source /path/to/backup

# Start the service
sudo systemctl start smartsteps.service  # Linux
Start-Service SmartStepsAI  # Windows

# Verify restoration
python -m smart_steps_ai.cli verify --all
```

### Data Recovery

For emergency data recovery:

1. **Stop the service**: Prevent further data changes
2. **Create a backup of current state**: Even if corrupted
3. **Identify the issue**: Check logs and error messages
4. **Apply appropriate recovery method**:
   - Restore from backup
   - Run database repair tools
   - Manual data correction

```bash
# Repair database
python -m smart_steps_ai.tools.repair_db --config /etc/smartsteps/config.yaml

# Verify data integrity
python -m smart_steps_ai.tools.verify_data --config /etc/smartsteps/config.yaml
```

## Monitoring and Alerts

### System Monitoring

Monitor system resource usage:

```bash
# View current resource usage
python -m smart_steps_ai.cli monitor resources

# Monitor API performance
python -m smart_steps_ai.cli monitor api

# Monitor database metrics
python -m smart_steps_ai.cli monitor database
```

### Log Monitoring

Configure log monitoring in the main configuration:

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "/var/log/smartsteps/app.log"
  max_size_mb: 100
  backup_count: 10
  format: "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
  separate_error_log: true
  error_log: "/var/log/smartsteps/error.log"
```

Common log locations:

- **Application log**: `/var/log/smartsteps/app.log`
- **Error log**: `/var/log/smartsteps/error.log`
- **API access log**: `/var/log/smartsteps/api.log`
- **Security audit log**: `/var/log/smartsteps/security.log`

### Alert Configuration

Configure alerts for critical system events:

```yaml
alerts:
  enabled: true
  channels:
    email:
      enabled: true
      recipients: ["admin@example.com"]
      smtp_server: "smtp.example.com"
      smtp_port: 587
      smtp_user: "alerts@example.com"
      smtp_password: "password"
    webhook:
      enabled: false
      url: "https://example.com/webhook"
    sms:
      enabled: false
      provider: "twilio"
      recipients: ["+1234567890"]
  rules:
    - name: "high_cpu"
      condition: "cpu_percent > 90"
      duration_seconds: 300
      cooldown_minutes: 60
      message: "High CPU usage detected: {value}%"
      severity: "warning"
    - name: "error_spike"
      condition: "error_rate > 10"
      duration_seconds: 60
      cooldown_minutes: 15
      message: "Error rate spike detected: {value} errors/minute"
      severity: "critical"
```

### Monitoring Dashboard

Access the monitoring dashboard at `http://your-server:8543/admin/dashboard` with administrative credentials.

## Troubleshooting

### Common Issues and Solutions

#### Service Won't Start

**Symptoms**: Service fails to start, exits immediately

**Solutions**:
- Check log files for errors: `/var/log/smartsteps/error.log`
- Verify configuration files are valid
- Check permissions on data directories
- Verify Python version and dependencies
- Check for port conflicts

```bash
# Validate configuration
python -m smart_steps_ai.tools.validate_config --config /etc/smartsteps/config.yaml

# Check port availability
netstat -tuln | grep 8543
```

#### Database Connection Issues

**Symptoms**: Service starts but API returns 500 errors, database connection errors in logs

**Solutions**:
- Verify database service is running
- Check database connection settings
- Ensure database credentials are correct
- Check network connectivity to database server

```bash
# Test database connection
python -m smart_steps_ai.tools.test_db_connection

# Repair database
python -m smart_steps_ai.tools.repair_db --config /etc/smartsteps/config.yaml
```

#### Memory Issues

**Symptoms**: Service becomes unresponsive, high memory usage, "Out of memory" errors

**Solutions**:
- Adjust worker count to match available system memory
- Enable memory optimization features
- Implement caching with appropriate TTL values
- Configure batch processing for large operations

```bash
# Check memory usage
python -m smart_steps_ai.cli monitor resources

# Optimize memory settings
python -m smart_steps_ai.tools.optimize_memory --apply
```

#### API Performance Issues

**Symptoms**: Slow API responses, timeout errors

**Solutions**:
- Increase worker count for CPU-bound operations
- Optimize database queries and indexes
- Enable and configure caching
- Adjust timeout settings
- Scale horizontally if needed

```bash
# Benchmark API performance
python -m smart_steps_ai.tools.benchmark_api

# Generate performance optimization recommendations
python -m smart_steps_ai.tools.optimize_performance --recommend
```

### Diagnostic Tools

The system provides several diagnostic tools:

```bash
# System health check
python -m smart_steps_ai.cli health

# API endpoint testing
python -m smart_steps_ai.tools.test_endpoints

# Log analysis
python -m smart_steps_ai.tools.analyze_logs --last-hours 24

# Performance profiling
python -m smart_steps_ai.tools.profile_api --duration 60
```

### Logging Levels

Adjust logging levels for detailed troubleshooting:

```yaml
logging:
  level: "DEBUG"  # Temporarily set to DEBUG for troubleshooting
  
  # Component-specific logging levels
  component_levels:
    api: "DEBUG"
    database: "INFO"
    persona_manager: "INFO"
    session_manager: "DEBUG"
```

## Maintenance Tasks

### Routine Maintenance

Perform these maintenance tasks regularly:

#### Daily Tasks

- Check service status
- Review error logs
- Verify backup completion
- Monitor system resource usage

#### Weekly Tasks

- Review security audit logs
- Check disk space usage
- Analyze performance metrics
- Verify data integrity

#### Monthly Tasks

- Apply security updates
- Rotate API keys (if needed)
- Review and optimize configuration
- Test backup restoration
- Clean up old log files

### Database Maintenance

```bash
# Perform database maintenance
python -m smart_steps_ai.cli db maintenance

# Optimize database
python -m smart_steps_ai.cli db optimize

# Clean up old sessions
python -m smart_steps_ai.cli db cleanup --older-than 90d
```

### Upgrade Procedures

To upgrade the Smart Steps AI module:

1. **Backup the current system**
   ```bash
   python -m smart_steps_ai.cli backup create --output /path/to/backup
   ```

2. **Stop the service**
   ```bash
   # Linux
   sudo systemctl stop smartsteps.service
   
   # Windows
   Stop-Service SmartStepsAI
   ```

3. **Download and install the new version**
   ```bash
   # Linux
   sudo ./install_server.sh --upgrade
   
   # Windows
   .\install_server.ps1 -Upgrade
   ```

4. **Start the service**
   ```bash
   # Linux
   sudo systemctl start smartsteps.service
   
   # Windows
   Start-Service SmartStepsAI
   ```

5. **Verify the upgrade**
   ```bash
   python -m smart_steps_ai.cli version
   python -m smart_steps_ai.cli verify --all
   ```

### Version Management

Track the installed version and available updates:

```bash
# Check current version
python -m smart_steps_ai.cli version

# Check for updates
python -m smart_steps_ai.cli check-updates

# View changelog
python -m smart_steps_ai.cli changelog
```

## Advanced Configuration

### Scaling Configuration

For high-traffic deployments, consider these scaling options:

```yaml
scaling:
  auto_scaling: true
  min_workers: 4
  max_workers: 16
  worker_scaling_trigger: "cpu_percent > 75"
  scale_down_delay_minutes: 10
  horizontal_scaling_enabled: false  # Requires load balancer setup
```

### Custom Persona Development

Create custom AI personas for specialized roles:

```bash
# Create a new persona template
python -m smart_steps_ai.cli persona create-template --name "addiction_counselor" --output ./my_persona.json

# Import a custom persona
python -m smart_steps_ai.cli persona import --file ./my_persona.json

# Test a persona
python -m smart_steps_ai.cli persona test --name "addiction_counselor" --interactive
```

### Integration Configuration

Configure integration with external systems:

```yaml
integrations:
  ehr_systems:
    enabled: true
    type: "fhir"
    endpoint: "https://ehr.example.com/fhir"
    auth_method: "oauth2"
    client_id: "smartsteps_client"
    scopes: ["patient.read", "observation.write"]
  
  calendar:
    enabled: true
    type: "google"
    credentials_file: "/etc/smartsteps/google_calendar_credentials.json"
    calendar_id: "primary"
```

## Appendix

### Command Line Reference

Complete list of CLI commands:

| Command | Description | Example |
|---------|-------------|---------|
| `backup create` | Create a system backup | `python -m smart_steps_ai.cli backup create` |
| `backup restore` | Restore from backup | `python -m smart_steps_ai.cli backup restore --source backup.zip` |
| `db maintenance` | Perform database maintenance | `python -m smart_steps_ai.cli db maintenance` |
| `health` | Check system health | `python -m smart_steps_ai.cli health` |
| `monitor resources` | Monitor system resources | `python -m smart_steps_ai.cli monitor resources` |
| `user create` | Create a new user | `python -m smart_steps_ai.cli user create` |
| `persona import` | Import a persona | `python -m smart_steps_ai.cli persona import --file persona.json` |
| `version` | Show version information | `python -m smart_steps_ai.cli version` |

### Configuration Reference

For detailed configuration options, refer to:
- [Configuration Schema](../Reference/ConfigurationSchema.md)
- [Security Configuration Guide](../Security/SecurityConfiguration.md)
- [Scaling Guide](../Deployment/ScalingGuide.md)

### Resource Requirements

| Deployment Size | Users | Sessions/day | CPU | RAM | Storage |
|-----------------|-------|--------------|-----|-----|---------|
| Small | <10 | <50 | 2 cores | 4 GB | 20 GB |
| Medium | 10-50 | 50-200 | 4 cores | 8 GB | 50 GB |
| Large | 50-200 | 200-1000 | 8+ cores | 16+ GB | 100+ GB |
| Enterprise | 200+ | 1000+ | 16+ cores | 32+ GB | 500+ GB |

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-05-11 | Admin Team | Initial creation |

**Review Schedule**: This document should be reviewed and updated at least quarterly or when significant system changes occur.