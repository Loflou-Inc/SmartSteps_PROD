#!/bin/bash
# Smart Steps AI Professional Persona Module - Docker Entrypoint Script
set -e

# Function to generate a random API key if none exists
generate_api_key() {
    if [ ! -f "$SMARTSTEPS_CONFIG_DIR/secrets.yaml" ]; then
        echo "Generating API key and secrets..."
        
        # Generate random keys
        API_KEY=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
        JWT_SECRET=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
        ENCRYPTION_KEY=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
        
        # Create secrets file
        cat > "$SMARTSTEPS_CONFIG_DIR/secrets.yaml" << EOF
# IMPORTANT: This file contains sensitive information
# Keep this file secure and restrict access
secrets:
  api_key: "$API_KEY"
  jwt_secret: "$JWT_SECRET"
  encryption_key: "$ENCRYPTION_KEY"
EOF
        echo "API key and secrets generated successfully."
        echo "Your API key is: $API_KEY"
        echo "Store this securely for API access."
        echo ""
    else
        echo "Using existing API key from secrets file."
    fi
}

# Function to create default configuration if none exists
create_default_config() {
    if [ ! -f "$SMARTSTEPS_CONFIG_DIR/config.yaml" ]; then
        echo "Creating default configuration..."
        
        # Create config file
        cat > "$SMARTSTEPS_CONFIG_DIR/config.yaml" << EOF
# Smart Steps AI Professional Persona Module Configuration
app:
  name: SmartSteps AI
  environment: production
  debug: false

paths:
  data: /app/data
  logs: /app/logs
  personas: /app/data/personas
  sessions: /app/data/sessions
  memory: /app/data/memory

server:
  host: 0.0.0.0
  port: 8543
  workers: 4
  timeout: 60

security:
  api_key_prefix: "sk_ss_"
  allowed_origins: []
  enable_mfa: true
  session_expiry_minutes: 30
EOF
        echo "Default configuration created."
    else
        echo "Using existing configuration file."
    fi
    
    # Always copy security template if it doesn't exist
    if [ ! -f "$SMARTSTEPS_CONFIG_DIR/security.yaml" ] && [ -f "/app/config/templates/security.yaml" ]; then
        echo "Creating security configuration..."
        cp "/app/config/templates/security.yaml" "$SMARTSTEPS_CONFIG_DIR/security.yaml"
        echo "Security configuration created."
    fi
}

# Function to initialize required directories
initialize_directories() {
    mkdir -p /app/data/personas
    mkdir -p /app/data/sessions
    mkdir -p /app/data/memory
    mkdir -p /app/logs
    
    echo "Directory structure verified."
}

# Function to initialize database
initialize_database() {
    echo "Initializing database..."
    python -m smart_steps_ai.db.init --config "$SMARTSTEPS_CONFIG_DIR/config.yaml"
    echo "Database initialized."
}

# Function to create default personas if needed
create_default_personas() {
    if [ ! -d "/app/data/personas" ] || [ -z "$(ls -A /app/data/personas)" ]; then
        echo "Creating default personas..."
        python -m smart_steps_ai.tools.create_default_personas --config "$SMARTSTEPS_CONFIG_DIR/config.yaml"
        echo "Default personas created."
    else
        echo "Using existing personas."
    fi
}

# Main entrypoint logic
echo "Starting Smart Steps AI Professional Persona Module..."
echo "Environment: $SMARTSTEPS_ENV"
echo "Configuration directory: $SMARTSTEPS_CONFIG_DIR"

# Run initialization steps
initialize_directories
generate_api_key
create_default_config
initialize_database
create_default_personas

echo "Initialization complete. Starting server..."
echo ""

# Execute the provided command (default: start the server)
exec "$@"
