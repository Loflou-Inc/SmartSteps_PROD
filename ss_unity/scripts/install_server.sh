#!/bin/bash
# Smart Steps AI Professional Persona Module - Server Installation Script
# This script installs the Smart Steps server components on a Linux system

set -e  # Exit on any error

# ASCII Art Banner
echo "
 _____                      _      _____  _
/  ___|                    | |    /  ___|| |
\ \`--.  _ __ ___    __ _  | |_   \ \`--. | |_   ___  _ __   ___
 \`--. \| '_ \` _ \  / _\` | | __|   \`--. \| __| / _ \| '_ \ / __|
/\__/ /| | | | | || (_| | | |_   /\__/ /| |_ |  __/| |_) |\__ \\
\____/ |_| |_| |_| \__,_|  \__|  \____/  \__| \___|| .__/ |___/
                                                   | |
                                                   |_|
     AI Professional Persona Module - Server Installation
"

# Configuration Variables
INSTALL_DIR="/opt/smartsteps"
LOG_DIR="/var/log/smartsteps"
CONFIG_DIR="/etc/smartsteps"
DATA_DIR="/var/lib/smartsteps"
SERVICE_USER="smartsteps"
SERVICE_GROUP="smartsteps"
PYTHON_VERSION="3.8"

# Helper Functions
print_section() {
    echo "------------------------------------------------------"
    echo "  $1"
    echo "------------------------------------------------------"
}

check_prerequisites() {
    print_section "Checking Prerequisites"
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        echo "Error: This script must be run as root"
        exit 1
    fi
    
    # Check for required commands
    for cmd in python3 pip3 virtualenv systemctl; do
        if ! command -v $cmd &> /dev/null; then
            echo "Error: Required command '$cmd' not found"
            echo "Please install the necessary dependencies and try again"
            exit 1
        fi
    done
    
    # Check Python version
    PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if (( $(echo "$PY_VERSION < $PYTHON_VERSION" | bc -l) )); then
        echo "Error: Python version $PYTHON_VERSION or higher is required (found $PY_VERSION)"
        exit 1
    fi
    
    echo "✓ All prerequisites satisfied"
}

create_user_and_directories() {
    print_section "Creating User and Directories"
    
    # Create user and group if they don't exist
    if ! getent group $SERVICE_GROUP &> /dev/null; then
        groupadd --system $SERVICE_GROUP
        echo "✓ Created group $SERVICE_GROUP"
    fi
    
    if ! getent passwd $SERVICE_USER &> /dev/null; then
        useradd --system --gid $SERVICE_GROUP --shell /bin/false --home-dir $INSTALL_DIR $SERVICE_USER
        echo "✓ Created user $SERVICE_USER"
    fi
    
    # Create directories
    mkdir -p $INSTALL_DIR
    mkdir -p $LOG_DIR
    mkdir -p $CONFIG_DIR
    mkdir -p $DATA_DIR
    mkdir -p $DATA_DIR/sessions
    mkdir -p $DATA_DIR/personas
    mkdir -p $DATA_DIR/memory
    
    # Set permissions
    chown -R $SERVICE_USER:$SERVICE_GROUP $INSTALL_DIR
    chown -R $SERVICE_USER:$SERVICE_GROUP $LOG_DIR
    chown -R $SERVICE_USER:$SERVICE_GROUP $CONFIG_DIR
    chown -R $SERVICE_USER:$SERVICE_GROUP $DATA_DIR
    
    chmod 750 $INSTALL_DIR
    chmod 750 $LOG_DIR
    chmod 750 $CONFIG_DIR
    chmod 750 $DATA_DIR
    
    echo "✓ Created directories with appropriate permissions"
}

install_python_environment() {
    print_section "Setting up Python Environment"
    
    # Create virtual environment
    virtualenv -p python3 $INSTALL_DIR/venv
    
    # Activate virtual environment and install dependencies
    source $INSTALL_DIR/venv/bin/activate
    
    # Install dependencies
    pip install --no-cache-dir --upgrade pip
    pip install --no-cache-dir wheel
    
    # Clone or copy application files
    if [ -d "./smart_steps_ai" ]; then
        cp -r ./smart_steps_ai $INSTALL_DIR/
        echo "✓ Copied application files from local directory"
    else
        git clone https://github.com/example/smart-steps-ai.git $INSTALL_DIR/smart_steps_ai
        echo "✓ Cloned application files from repository"
    fi
    
    # Install application
    cd $INSTALL_DIR/smart_steps_ai
    pip install --no-cache-dir -e .
    pip install --no-cache-dir -r requirements.txt
    
    # Copy sample configurations
    if [ -d "./config" ]; then
        cp -r ./config/* $CONFIG_DIR/
        echo "✓ Copied sample configuration files"
    fi
    
    echo "✓ Python environment setup complete"
}

configure_application() {
    print_section "Configuring Application"
    
    # Create main configuration file if it doesn't exist
    if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
        cat > $CONFIG_DIR/config.yaml << EOF
# Smart Steps AI Professional Persona Module Configuration
app:
  name: SmartSteps AI
  environment: production
  debug: false

paths:
  data: $DATA_DIR
  logs: $LOG_DIR
  personas: $DATA_DIR/personas
  sessions: $DATA_DIR/sessions
  memory: $DATA_DIR/memory

server:
  host: 0.0.0.0
  port: 8543
  workers: 4
  timeout: 60

security:
  api_key_prefix: "sk_ss_"
  allowed_origins: ["https://localhost:3000"]
  enable_mfa: true
  session_expiry_minutes: 30
EOF
        echo "✓ Created default configuration file"
    fi
    
    # Set correct permissions
    chown $SERVICE_USER:$SERVICE_GROUP $CONFIG_DIR/config.yaml
    chmod 640 $CONFIG_DIR/config.yaml
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32)
    cat > $CONFIG_DIR/secrets.yaml << EOF
# IMPORTANT: This file contains sensitive information
# Keep this file secure and restrict access
secrets:
  api_key: "$SECRET_KEY"
  jwt_secret: "$(openssl rand -hex 32)"
  encryption_key: "$(openssl rand -hex 32)"
EOF
    
    # Set restricted permissions for secrets
    chown $SERVICE_USER:$SERVICE_GROUP $CONFIG_DIR/secrets.yaml
    chmod 600 $CONFIG_DIR/secrets.yaml
    
    # Create security configuration
    if [ ! -f "$CONFIG_DIR/security.yaml" ]; then
        cp $INSTALL_DIR/smart_steps_ai/config/templates/security.yaml $CONFIG_DIR/security.yaml
        echo "✓ Created security configuration"
    fi
    
    echo "✓ Application configuration complete"
    echo "API Key: $SECRET_KEY"
}

setup_systemd_service() {
    print_section "Setting up Systemd Service"
    
    # Create systemd service file
    cat > /etc/systemd/system/smartsteps.service << EOF
[Unit]
Description=Smart Steps AI Professional Persona Service
After=network.target

[Service]
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$INSTALL_DIR/smart_steps_ai
ExecStart=$INSTALL_DIR/venv/bin/python -m smart_steps_ai.server
Environment=PYTHONPATH=$INSTALL_DIR
Environment=SMARTSTEPS_CONFIG_DIR=$CONFIG_DIR
Environment=SMARTSTEPS_ENV=production
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable smartsteps.service
    
    echo "✓ Systemd service installed and enabled"
}

setup_database() {
    print_section "Setting up Database"
    
    # Activate virtual environment
    source $INSTALL_DIR/venv/bin/activate
    
    # Initialize database
    PYTHONPATH=$INSTALL_DIR python -m smart_steps_ai.db.init --config $CONFIG_DIR/config.yaml
    
    echo "✓ Database initialized"
}

final_setup() {
    print_section "Performing Final Setup"
    
    # Create default personas
    source $INSTALL_DIR/venv/bin/activate
    PYTHONPATH=$INSTALL_DIR python -m smart_steps_ai.tools.create_default_personas --config $CONFIG_DIR/config.yaml
    
    # Set correct permissions on all files
    find $INSTALL_DIR -type d -exec chmod 750 {} \;
    find $INSTALL_DIR -type f -exec chmod 640 {} \;
    find $INSTALL_DIR/venv/bin -type f -exec chmod 750 {} \;
    
    echo "✓ Created default personas"
    echo "✓ Set file permissions"
}

start_service() {
    print_section "Starting Service"
    
    systemctl start smartsteps.service
    systemctl status smartsteps.service --no-pager
    
    echo "✓ Service started successfully"
}

installation_summary() {
    print_section "Installation Summary"
    
    echo "Smart Steps AI Professional Persona Module has been installed successfully!"
    echo ""
    echo "Installation Directory: $INSTALL_DIR"
    echo "Configuration Directory: $CONFIG_DIR"
    echo "Log Directory: $LOG_DIR"
    echo "Data Directory: $DATA_DIR"
    echo ""
    echo "API Endpoint: http://$(hostname -I | awk '{print $1}'):8543/api"
    echo "API Key: $SECRET_KEY"
    echo ""
    echo "To verify the installation, run: curl -H 'Authorization: Bearer $SECRET_KEY' http://localhost:8543/api/health"
    echo ""
    echo "Management commands:"
    echo "  - Start service: systemctl start smartsteps.service"
    echo "  - Stop service: systemctl stop smartsteps.service"
    echo "  - Check status: systemctl status smartsteps.service"
    echo "  - View logs: journalctl -u smartsteps.service"
    echo ""
    echo "For more information, refer to the documentation in $INSTALL_DIR/smart_steps_ai/docs"
}

# Main Installation Process
main() {
    print_section "Starting Installation"
    
    check_prerequisites
    create_user_and_directories
    install_python_environment
    configure_application
    setup_systemd_service
    setup_database
    final_setup
    start_service
    installation_summary
    
    print_section "Installation Complete"
}

# Execute Main Process
main
