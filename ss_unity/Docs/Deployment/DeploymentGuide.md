# Smart Steps AI Professional Persona Module - Deployment Guide

This guide provides comprehensive instructions for deploying the Smart Steps AI Professional Persona module in various environments.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Deployment Options](#deployment-options)
3. [Linux Deployment](#linux-deployment)
4. [Windows Deployment](#windows-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Cloud Deployment](#cloud-deployment)
7. [Unity Integration](#unity-integration)
8. [Post-Deployment Configuration](#post-deployment-configuration)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)
10. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 10 GB
- **Operating System**: Ubuntu 20.04+, Windows Server 2019+, or Docker-compatible environment
- **Python**: Version 3.8 or higher
- **Network**: Outbound internet access (for API providers)

### Recommended Requirements

- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 20+ GB SSD
- **Operating System**: Ubuntu 22.04, Windows Server 2022, or Docker
- **Python**: Version 3.9 or higher
- **Network**: Static IP with firewall configuration

## Deployment Options

The Smart Steps AI module can be deployed using one of the following methods:

1. **Native Installation**: Direct installation on Linux or Windows servers
2. **Docker Deployment**: Containerized deployment using Docker and Docker Compose
3. **Cloud Deployment**: Deployment on AWS, Azure, or Google Cloud Platform
4. **Hybrid Deployment**: Combined local installation with cloud services

Choose the deployment method that best fits your infrastructure requirements and expertise.

## Linux Deployment

### Prerequisites

Ensure you have the following prerequisites installed:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

### Installation Steps

1. **Download the installation script**:

```bash
wget https://example.com/smartsteps/install_server.sh
chmod +x install_server.sh
```

2. **Run the installation script with root privileges**:

```bash
sudo ./install_server.sh
```

3. **Verify the installation**:

```bash
systemctl status smartsteps.service
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8543/api/health
```

### Configuration

The Linux installation script creates the following file structure:

- Configuration: `/etc/smartsteps/`
- Logs: `/var/log/smartsteps/`
- Data: `/var/lib/smartsteps/`
- Application: `/opt/smartsteps/`

Edit the configuration files in `/etc/smartsteps/` to customize the deployment.

## Windows Deployment

### Prerequisites

Ensure you have the following prerequisites installed:

- Python 3.8 or higher
- Git (optional)
- Windows PowerShell 5.1 or higher

### Installation Steps

1. **Download the installation script** from the provided link or repository.

2. **Open PowerShell as Administrator** and navigate to the script directory.

3. **Run the installation script**:

```powershell
.\install_server.ps1
```

4. **Verify the installation**:

```powershell
Get-Service -Name SmartStepsAI
Invoke-WebRequest -Uri http://localhost:8543/api/health -Headers @{Authorization = "Bearer YOUR_API_KEY"}
```

### Configuration

The Windows installation script creates the following file structure:

- Configuration: `C:\ProgramData\SmartSteps\Config\`
- Logs: `C:\ProgramData\SmartSteps\Logs\`
- Data: `C:\ProgramData\SmartSteps\`
- Application: `C:\Program Files\SmartSteps\`

Edit the configuration files in `C:\ProgramData\SmartSteps\Config\` to customize the deployment.

## Docker Deployment

### Prerequisites

- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher
- Git (for repository cloning)

### Installation Steps

1. **Clone the repository**:

```bash
git clone https://github.com/example/smartsteps-ai.git
cd smartsteps-ai
```

2. **Deploy with Docker Compose**:

```bash
cd scripts/docker
docker-compose up -d
```

3. **Verify the deployment**:

```bash
docker ps
docker logs smartsteps-api
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8543/api/health
```

### Configuration

The Docker deployment uses volume mounts for persistence:

- Configuration: `smartsteps-config` volume (mapped to `/etc/smartsteps/` in the container)
- Data: `smartsteps-data` volume (mapped to `/app/data/` in the container)
- Logs: `smartsteps-logs` volume (mapped to `/app/logs/` in the container)

To customize the configuration:

```bash
# Get the API key from logs
docker logs smartsteps-api | grep "Your API key is"

# Edit configuration files
docker exec -it smartsteps-api sh -c "vi /etc/smartsteps/config.yaml"
```

## Cloud Deployment

### AWS Deployment

#### Using EC2

1. Launch an EC2 instance with Ubuntu 22.04 or Amazon Linux 2.
2. Follow the Linux deployment instructions.

#### Using ECS/Fargate

1. Create an ECR repository for the Docker image.
2. Build and push the Docker image to ECR.
3. Create an ECS task definition and service.
4. Configure appropriate IAM roles and security groups.

### Azure Deployment

#### Using Azure VMs

1. Create an Azure VM with Ubuntu 22.04.
2. Follow the Linux deployment instructions.

#### Using Azure Container Instances

1. Create an Azure Container Registry.
2. Build and push the Docker image to ACR.
3. Deploy the container using Azure Container Instances.
4. Configure appropriate networking and storage.

### Google Cloud Platform

#### Using Compute Engine

1. Create a GCP VM instance with Ubuntu 22.04.
2. Follow the Linux deployment instructions.

#### Using Google Kubernetes Engine

1. Create a GKE cluster.
2. Apply the Kubernetes deployment manifests.
3. Configure ingress and persistent volumes.

## Unity Integration

### Installing the Unity Package

1. **Download the installation script**:
   Download `install_unity_package.ps1` from the repository.

2. **Run the installation script**:

```powershell
.\install_unity_package.ps1
```

3. Follow the interactive prompts to specify:
   - Unity project location
   - API endpoint
   - API key

4. **Import the package in Unity**:
   - Open your Unity project
   - The package will be automatically detected
   - If not, go to Window > Package Manager > + > Add package from disk
   - Select the `package.json` file from the installed location

### Configuring the Unity Integration

After installation, you can configure the Unity integration through:

1. **Inspector Settings**:
   - Select the SmartStepsAI GameObject in your scene
   - Adjust settings in the Inspector panel

2. **Configuration File**:
   - Edit `SmartStepsAIConfig.json` in the Resources folder

3. **Runtime Configuration**:
   - Use the `SmartStepsAIManager.Configure()` method in your scripts

## Post-Deployment Configuration

### Security Configuration

After deploying the Smart Steps AI module, review and adjust the security settings:

1. **API Authentication**:
   - Generate a new API key if needed
   - Configure allowed origins for CORS
   - Set up rate limiting

2. **User Authentication**:
   - Configure multi-factor authentication
   - Set password policies
   - Define user roles and permissions

3. **Data Protection**:
   - Configure encryption settings
   - Set up backup procedures
   - Define data retention policies

### Performance Tuning

Adjust the performance settings based on your hardware capabilities:

1. **Worker Configuration**:
   - Set appropriate number of workers (typically match CPU cores)
   - Configure worker timeout values

2. **Memory Management**:
   - Adjust cache settings for optimal memory usage
   - Configure garbage collection thresholds

3. **Database Optimization**:
   - Enable connection pooling
   - Set appropriate timeout values
   - Configure index optimization

## Monitoring and Maintenance

### Monitoring Setup

1. **System Monitoring**:
   - CPU, memory, and disk usage
   - Network traffic and latency
   - Service availability

2. **Application Monitoring**:
   - API response times
   - Error rates and types
   - Service health checks

3. **Log Management**:
   - Centralized log collection
   - Log rotation and archiving
   - Log analysis and alerting

### Maintenance Procedures

1. **Backup and Recovery**:
   - Regular database backups
   - Configuration file backups
   - Test restoration procedures periodically
   - Document backup and restoration processes

2. **Updates and Upgrades**:
   - Regular security updates
   - Scheduled version upgrades
   - Rollback procedures
   - Change management process

3. **Health Checks**:
   - Daily service status verification
   - Weekly performance review
   - Monthly security assessment
   - Quarterly disaster recovery testing

## Troubleshooting

### Common Issues

#### API Connection Issues

**Symptoms**: Unable to connect to the API, connection timeout, connection refused

**Solutions**:
- Verify the service is running (`systemctl status smartsteps.service` or `Get-Service SmartStepsAI`)
- Check network connectivity and firewall rules
- Verify the API endpoint configuration
- Check server logs for errors

#### Authentication Failures

**Symptoms**: 401 Unauthorized, 403 Forbidden responses

**Solutions**:
- Verify the API key is correct
- Check API key prefixes (should start with `sk_ss_`)
- Ensure the API key has not expired
- Verify user permissions for the requested operation

#### Performance Issues

**Symptoms**: Slow API responses, high CPU/memory usage

**Solutions**:
- Check system resources (CPU, memory, disk)
- Adjust worker count and thread settings
- Enable caching if not already enabled
- Optimize database queries and indexes
- Check for memory leaks in logs

#### Unity Integration Issues

**Symptoms**: Unity cannot connect to the API, error messages in Unity console

**Solutions**:
- Verify API endpoint configuration in Unity
- Check API key in Unity settings
- Ensure network connectivity from Unity to the API server
- Check for SSL/TLS certificate issues
- Verify Unity package version compatibility

### Logging and Diagnostics

#### Log Locations

- **Linux**: `/var/log/smartsteps/`
- **Windows**: `C:\ProgramData\SmartSteps\Logs\`
- **Docker**: Container logs (`docker logs smartsteps-api`)
- **Unity**: Unity Editor console and Player.log

#### Diagnostic Commands

```bash
# Check service status (Linux)
systemctl status smartsteps.service

# Check service status (Windows PowerShell)
Get-Service SmartStepsAI

# View service logs (Linux)
journalctl -u smartsteps.service -f

# Test API health endpoint
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:8543/api/health

# Database verification
python -m smart_steps_ai.tools.verify_db --config /etc/smartsteps/config.yaml

# Memory management diagnostics
python -m smart_steps_ai.tools.memory_check --config /etc/smartsteps/config.yaml
```

### Getting Help

If you encounter issues that cannot be resolved using this guide:

1. **Community Support**:
   - Post questions on the Smart Steps GitHub repository
   - Join the Smart Steps Discord community for real-time assistance
   - Search the knowledge base at [support.smartsteps.example.com](https://support.smartsteps.example.com)

2. **Professional Support**:
   - Submit a support ticket at [help.smartsteps.example.com](https://help.smartsteps.example.com)
   - Contact your account representative
   - For critical issues, use the emergency support hotline

## Appendix

### Configuration Reference

#### Main Configuration (config.yaml)

| Section | Parameter | Description | Default |
|---------|-----------|-------------|---------|
| app | name | Application name | SmartSteps AI |
| app | environment | Deployment environment | production |
| app | debug | Enable debug mode | false |
| paths | data | Data directory path | /var/lib/smartsteps |
| paths | logs | Log directory path | /var/log/smartsteps |
| paths | personas | Personas directory path | /var/lib/smartsteps/personas |
| server | host | Bind address | 0.0.0.0 |
| server | port | API port | 8543 |
| server | workers | Number of worker processes | 4 |
| security | api_key_prefix | API key prefix | sk_ss_ |
| security | enable_mfa | Enable multi-factor auth | true |

#### Security Configuration (security.yaml)

Refer to the [Security Configuration Guide](../Security/SecurityConfiguration.md) for detailed information.

### Network Requirements

| Component | Direction | Port | Protocol | Purpose |
|-----------|-----------|------|----------|---------|
| API Server | Inbound | 8543 | TCP | API access |
| API Server | Outbound | 443 | TCP | External API providers |
| Database | Inbound | 27017 | TCP | MongoDB (if used) |
| Cache | Inbound | 6379 | TCP | Redis (if used) |
| Monitoring | Inbound | 9090 | TCP | Prometheus (if used) |
| Logs | Outbound | 514 | TCP/UDP | Syslog (if used) |

### Required Permissions

#### Linux

```bash
# File permissions
/opt/smartsteps/ - 750 (smartsteps:smartsteps)
/var/log/smartsteps/ - 750 (smartsteps:smartsteps)
/var/lib/smartsteps/ - 750 (smartsteps:smartsteps)
/etc/smartsteps/ - 750 (smartsteps:smartsteps)
/etc/smartsteps/secrets.yaml - 600 (smartsteps:smartsteps)
```

#### Windows

```powershell
# Service permissions
SmartStepsAI service - LocalSystem account
C:\Program Files\SmartSteps\ - Administrators, SYSTEM (Full Control)
C:\ProgramData\SmartSteps\ - Administrators, SYSTEM (Full Control)
C:\ProgramData\SmartSteps\Config\secrets.yaml - Administrators, SYSTEM (Read)
```

### Deployment Checklist

Use this checklist to verify your deployment:

- [ ] Server meets minimum system requirements
- [ ] Python 3.8+ installed
- [ ] Installation script executed successfully
- [ ] Service running and enabled on startup
- [ ] API accessible on configured port
- [ ] API key generated and secured
- [ ] Configuration files properly set up
- [ ] Security settings reviewed and configured
- [ ] Logging configured and verified
- [ ] Backup procedures established
- [ ] Monitoring set up
- [ ] Documentation accessible to administrators
- [ ] Unity integration tested (if applicable)

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-05-11 | Deployment Team | Initial creation |

**Review Schedule**: This document should be reviewed and updated at least quarterly or when significant deployment changes occur.