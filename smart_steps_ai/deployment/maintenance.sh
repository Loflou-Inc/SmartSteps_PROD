#!/bin/bash
# Smart Steps AI Maintenance Script
# This script performs regular maintenance tasks for the Smart Steps AI system
# Recommended to run daily via cron job

# Exit on error
set -e

# Configuration
LOG_FILE="/var/log/smart_steps_maintenance.log"
MAX_LOG_SIZE=10485760  # 10MB
APP_DIR="/opt/smart_steps_ai"  # Update with your installation directory
BACKUP_DIR="${APP_DIR}/backup"
MAX_BACKUPS=5  # Maximum number of backups to keep

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Rotate log file if it's too big
if [ -f "$LOG_FILE" ] && [ $(stat -c%s "$LOG_FILE") -gt $MAX_LOG_SIZE ]; then
    mv "$LOG_FILE" "${LOG_FILE}.$(date +%Y%m%d)"
    gzip "${LOG_FILE}.$(date +%Y%m%d)"
fi

# Log function
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

log "Starting Smart Steps AI maintenance"

# Check if we're running in Docker environment
if [ -f /.dockerenv ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
    IS_DOCKER=true
    log "Detected Docker environment"
else
    IS_DOCKER=false
    log "Running in standard environment"
fi

# Function to run maintenance tasks
run_maintenance() {
    log "Running maintenance tasks"
    
    if [ "$IS_DOCKER" = true ]; then
        docker exec smart_steps_api python -m smart_steps_ai.utils.maintenance
    else
        cd "$APP_DIR"
        source venv/bin/activate
        python -m smart_steps_ai.utils.maintenance
        deactivate
    fi
    
    log "Maintenance tasks completed"
}

# Function to create backup
create_backup() {
    log "Creating backup"
    
    BACKUP_NAME="smart_steps_backup_$(date +%Y%m%d_%H%M%S)"
    
    if [ "$IS_DOCKER" = true ]; then
        docker exec smart_steps_api python deployment/auto_update.py check
    else
        cd "$APP_DIR"
        source venv/bin/activate
        python deployment/auto_update.py check
        deactivate
    fi
    
    log "Backup created: $BACKUP_NAME"
    
    # Clean up old backups
    # Get list of backups sorted by date (oldest first)
    BACKUPS=$(ls -t "${BACKUP_DIR}/smart_steps_backup_"* 2>/dev/null || true)
    
    # Count number of backups
    BACKUP_COUNT=$(echo "$BACKUPS" | wc -l)
    
    # Remove oldest backups if we have too many
    if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
        BACKUPS_TO_DELETE=$(($BACKUP_COUNT - $MAX_BACKUPS))
        log "Removing $BACKUPS_TO_DELETE old backups"
        
        echo "$BACKUPS" | tail -n "$BACKUPS_TO_DELETE" | while read BACKUP; do
            log "Removing old backup: $BACKUP"
            rm -rf "$BACKUP"
        done
    fi
}

# Function to check system health
check_health() {
    log "Checking system health"
    
    # Check disk space
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')
    if [ "$DISK_USAGE" -gt 90 ]; then
        log "WARNING: Disk usage is high: ${DISK_USAGE}%"
    else
        log "Disk usage: ${DISK_USAGE}%"
    fi
    
    # Check service status
    if [ "$IS_DOCKER" = true ]; then
        API_STATUS=$(docker inspect --format='{{.State.Status}}' smart_steps_api)
        MONITORING_STATUS=$(docker inspect --format='{{.State.Status}}' smart_steps_monitoring 2>/dev/null || echo "not running")
        
        log "API service status: $API_STATUS"
        log "Monitoring service status: $MONITORING_STATUS"
    else
        # Check services using systemd if available
        if command -v systemctl >/dev/null 2>&1; then
            API_STATUS=$(systemctl is-active smart_steps_api.service 2>/dev/null || echo "not running")
            MONITORING_STATUS=$(systemctl is-active smart_steps_monitoring.service 2>/dev/null || echo "not running")
            
            log "API service status: $API_STATUS"
            log "Monitoring service status: $MONITORING_STATUS"
        else
            # Simple process check
            if pgrep -f "smart_steps_ai.api.main" >/dev/null; then
                log "API service is running"
            else
                log "WARNING: API service is not running"
            fi
            
            if pgrep -f "monitoring_system.py" >/dev/null; then
                log "Monitoring service is running"
            else
                log "WARNING: Monitoring service is not running"
            fi
        fi
    fi
    
    # Check API health endpoint
    if command -v curl >/dev/null 2>&1; then
        API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:9500/api/v1/admin/health 2>/dev/null || echo "failed")
        
        if [ "$API_HEALTH" = "200" ]; then
            log "API health check: OK"
        else
            log "WARNING: API health check failed: $API_HEALTH"
        fi
    else
        log "curl not available, skipping API health check"
    fi
}

# Function to prune Docker resources (Docker only)
prune_docker() {
    if [ "$IS_DOCKER" = true ]; then
        log "Pruning Docker resources"
        
        # Remove unused containers
        docker container prune -f
        
        # Remove unused images
        docker image prune -f
        
        # Remove unused volumes (careful with this one)
        # docker volume prune -f
        
        log "Docker pruning completed"
    fi
}

# Run all maintenance tasks
run_maintenance
create_backup
check_health

# Run Docker-specific tasks
if [ "$IS_DOCKER" = true ]; then
    prune_docker
fi

log "Maintenance completed successfully"
