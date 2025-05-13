# SmartSteps AI Professional Persona Module - Windows Server Installation Script
# This script installs the SmartSteps server components on a Windows system

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator!"
    Break
}

# Display banner
Write-Host "
 _____                      _      _____  _
/  ___|                    | |    /  ___|| |
\ `--.  _ __ ___    __ _  | |_   \ `--. | |_   ___  _ __   ___
 `--. \| '_ ` _ \  / _`` | | __|   `--. \| __| / _ \| '_ \ / __|
/\__/ /| | | | | || (_| | | |_   /\__/ /| |_ |  __/| |_) |\__ \
\____/ |_| |_| |_| \__,_|  \__|  \____/  \__| \___|| .__/ |___/
                                                   | |
                                                   |_|
     AI Professional Persona Module - Windows Server Installation
" -ForegroundColor Cyan

# Configuration Variables
$InstallDir = "C:\Program Files\SmartSteps"
$DataDir = "C:\ProgramData\SmartSteps"
$LogDir = "$DataDir\Logs"
$ConfigDir = "$DataDir\Config"
$ServiceName = "SmartStepsAI"
$ServiceDisplayName = "Smart Steps AI Professional Persona Service"
$ServiceDescription = "Provides AI professional persona capabilities for the Smart Steps application"
$PythonVersion = "3.8"

# Helper Functions
function Write-Section {
    param (
        [string]$Title
    )
    
    Write-Host "`n------------------------------------------------------" -ForegroundColor Yellow
    Write-Host "  $Title" -ForegroundColor Yellow
    Write-Host "------------------------------------------------------" -ForegroundColor Yellow
}

function Check-Prerequisites {
    Write-Section "Checking Prerequisites"
    
    # Check for Python installation
    try {
        $PythonPath = Get-Command python -ErrorAction Stop
        $InstalledVersion = Invoke-Expression "python -c `"import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')`""
        
        if ([version]$InstalledVersion -lt [version]$PythonVersion) {
            Write-Host "Error: Python version $PythonVersion or higher is required (found $InstalledVersion)" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "✓ Python $InstalledVersion found at $($PythonPath.Source)" -ForegroundColor Green
    }
    catch {
        Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install Python $PythonVersion or higher and try again" -ForegroundColor Red
        exit 1
    }
    
    # Check for pip
    try {
        $PipPath = Get-Command pip -ErrorAction Stop
        Write-Host "✓ pip found at $($PipPath.Source)" -ForegroundColor Green
    }
    catch {
        Write-Host "Error: pip is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please ensure pip is installed with Python" -ForegroundColor Red
        exit 1
    }
    
    # Check for virtualenv
    try {
        $VenvPath = Get-Command virtualenv -ErrorAction Stop
        Write-Host "✓ virtualenv found at $($VenvPath.Source)" -ForegroundColor Green
    }
    catch {
        Write-Host "Installing virtualenv..." -ForegroundColor Yellow
        Invoke-Expression "pip install virtualenv"
        Write-Host "✓ virtualenv installed" -ForegroundColor Green
    }
    
    # Check for NSSM (Non-Sucking Service Manager)
    $NssmPath = "$PSScriptRoot\nssm.exe"
    if (-not (Test-Path $NssmPath)) {
        Write-Host "Downloading NSSM for service installation..." -ForegroundColor Yellow
        $NssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
        $NssmZip = "$env:TEMP\nssm.zip"
        
        Invoke-WebRequest -Uri $NssmUrl -OutFile $NssmZip
        Expand-Archive -Path $NssmZip -DestinationPath "$env:TEMP\nssm" -Force
        Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" $NssmPath
        
        Write-Host "✓ NSSM downloaded" -ForegroundColor Green
    }
    else {
        Write-Host "✓ NSSM found at $NssmPath" -ForegroundColor Green
    }
    
    Write-Host "✓ All prerequisites satisfied" -ForegroundColor Green
}

function Create-Directories {
    Write-Section "Creating Directories"
    
    # Create installation directories
    $Directories = @($InstallDir, $DataDir, $LogDir, $ConfigDir, "$DataDir\Sessions", "$DataDir\Personas", "$DataDir\Memory")
    
    foreach ($Dir in $Directories) {
        if (-not (Test-Path $Dir)) {
            New-Item -Path $Dir -ItemType Directory -Force | Out-Null
            Write-Host "✓ Created directory: $Dir" -ForegroundColor Green
        }
        else {
            Write-Host "Directory already exists: $Dir" -ForegroundColor Yellow
        }
    }
}

function Install-PythonEnvironment {
    Write-Section "Setting up Python Environment"
    
    # Create virtual environment
    if (-not (Test-Path "$InstallDir\venv")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        Invoke-Expression "virtualenv $InstallDir\venv"
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    }
    else {
        Write-Host "Virtual environment already exists" -ForegroundColor Yellow
    }
    
    # Activate virtual environment and install dependencies
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    $ActivateScript = "$InstallDir\venv\Scripts\Activate.ps1"
    . $ActivateScript
    
    # Upgrade pip and install wheel
    Invoke-Expression "pip install --upgrade pip"
    Invoke-Expression "pip install wheel"
    
    # Copy application files
    if (Test-Path ".\smart_steps_ai") {
        Copy-Item -Path ".\smart_steps_ai" -Destination $InstallDir -Recurse -Force
        Write-Host "✓ Copied application files from local directory" -ForegroundColor Green
    }
    else {
        # In a real environment, you would fetch from a Git repository or other source
        Write-Host "Application files not found locally. Would need to download from repository." -ForegroundColor Yellow
        # Example: git clone https://github.com/example/smart-steps-ai.git $InstallDir\smart_steps_ai
    }
    
    # Install application
    Set-Location "$InstallDir\smart_steps_ai"
    Invoke-Expression "pip install -e ."
    Invoke-Expression "pip install -r requirements.txt"
    
    # Copy sample configurations
    if (Test-Path ".\config") {
        Copy-Item -Path ".\config\*" -Destination $ConfigDir -Recurse -Force
        Write-Host "✓ Copied sample configuration files" -ForegroundColor Green
    }
    
    Write-Host "✓ Python environment setup complete" -ForegroundColor Green
    
    # Deactivate virtual environment
    deactivate
}

function Configure-Application {
    Write-Section "Configuring Application"
    
    # Create main configuration file if it doesn't exist
    $ConfigFile = "$ConfigDir\config.yaml"
    if (-not (Test-Path $ConfigFile)) {
        $ConfigContent = @"
# Smart Steps AI Professional Persona Module Configuration
app:
  name: SmartSteps AI
  environment: production
  debug: false

paths:
  data: $($DataDir.Replace('\', '\\'))
  logs: $($LogDir.Replace('\', '\\'))
  personas: $($DataDir.Replace('\', '\\'))\\Personas
  sessions: $($DataDir.Replace('\', '\\'))\\Sessions
  memory: $($DataDir.Replace('\', '\\'))\\Memory

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
"@
        $ConfigContent | Out-File -FilePath $ConfigFile -Encoding utf8
        Write-Host "✓ Created default configuration file" -ForegroundColor Green
    }
    
    # Generate secret key
    $ApiKey = [System.Guid]::NewGuid().ToString("N") + [System.Guid]::NewGuid().ToString("N")
    $JwtSecret = [System.Guid]::NewGuid().ToString("N") + [System.Guid]::NewGuid().ToString("N")
    $EncryptionKey = [System.Guid]::NewGuid().ToString("N") + [System.Guid]::NewGuid().ToString("N")
    
    $SecretsContent = @"
# IMPORTANT: This file contains sensitive information
# Keep this file secure and restrict access
secrets:
  api_key: "$ApiKey"
  jwt_secret: "$JwtSecret"
  encryption_key: "$EncryptionKey"
"@
    
    $SecretsContent | Out-File -FilePath "$ConfigDir\secrets.yaml" -Encoding utf8
    
    # Create security configuration
    $SecurityFile = "$ConfigDir\security.yaml"
    if (-not (Test-Path $SecurityFile) -and (Test-Path "$InstallDir\smart_steps_ai\config\templates\security.yaml")) {
        Copy-Item -Path "$InstallDir\smart_steps_ai\config\templates\security.yaml" -Destination $SecurityFile
        Write-Host "✓ Created security configuration" -ForegroundColor Green
    }
    
    Write-Host "✓ Application configuration complete" -ForegroundColor Green
    Write-Host "API Key: $ApiKey" -ForegroundColor Green
}

function Setup-WindowsService {
    Write-Section "Setting up Windows Service"
    
    $NssmPath = "$PSScriptRoot\nssm.exe"
    $PythonExe = "$InstallDir\venv\Scripts\python.exe"
    $ServiceModule = "-m smart_steps_ai.server"
    
    # Check if service already exists
    $ServiceExists = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    
    if ($ServiceExists) {
        Write-Host "Service already exists, removing..." -ForegroundColor Yellow
        Invoke-Expression "$NssmPath remove $ServiceName confirm"
    }
    
    # Create service
    Write-Host "Creating service..." -ForegroundColor Yellow
    Invoke-Expression "$NssmPath install $ServiceName `"$PythonExe`" `"$ServiceModule`""
    
    # Configure service
    Invoke-Expression "$NssmPath set $ServiceName DisplayName `"$ServiceDisplayName`""
    Invoke-Expression "$NssmPath set $ServiceName Description `"$ServiceDescription`""
    Invoke-Expression "$NssmPath set $ServiceName AppDirectory `"$InstallDir\smart_steps_ai`""
    Invoke-Expression "$NssmPath set $ServiceName AppEnvironmentExtra PYTHONPATH=$InstallDir"
    Invoke-Expression "$NssmPath set $ServiceName AppEnvironmentExtra SMARTSTEPS_CONFIG_DIR=$ConfigDir"
    Invoke-Expression "$NssmPath set $ServiceName AppEnvironmentExtra SMARTSTEPS_ENV=production"
    Invoke-Expression "$NssmPath set $ServiceName Start SERVICE_AUTO_START"
    Invoke-Expression "$NssmPath set $ServiceName ObjectName LocalSystem"
    
    # Configure stdout/stderr logging
    Invoke-Expression "$NssmPath set $ServiceName AppStdout `"$LogDir\service_stdout.log`""
    Invoke-Expression "$NssmPath set $ServiceName AppStderr `"$LogDir\service_stderr.log`""
    Invoke-Expression "$NssmPath set $ServiceName AppRotateFiles 1"
    Invoke-Expression "$NssmPath set $ServiceName AppRotateOnline 1"
    Invoke-Expression "$NssmPath set $ServiceName AppRotateSeconds 86400"
    Invoke-Expression "$NssmPath set $ServiceName AppRotateBytes 10485760"
    
    Write-Host "✓ Windows service installed" -ForegroundColor Green
}

function Setup-Database {
    Write-Section "Setting up Database"
    
    # Activate virtual environment and initialize database
    $ActivateScript = "$InstallDir\venv\Scripts\Activate.ps1"
    . $ActivateScript
    
    # Initialize database
    $env:PYTHONPATH = $InstallDir
    Invoke-Expression "python -m smart_steps_ai.db.init --config $ConfigDir\config.yaml"
    
    # Deactivate virtual environment
    deactivate
    
    Write-Host "✓ Database initialized" -ForegroundColor Green
}

function Final-Setup {
    Write-Section "Performing Final Setup"
    
    # Activate virtual environment and create default personas
    $ActivateScript = "$InstallDir\venv\Scripts\Activate.ps1"
    . $ActivateScript
    
    # Create default personas
    $env:PYTHONPATH = $InstallDir
    Invoke-Expression "python -m smart_steps_ai.tools.create_default_personas --config $ConfigDir\config.yaml"
    
    # Deactivate virtual environment
    deactivate
    
    Write-Host "✓ Created default personas" -ForegroundColor Green
}

function Start-SmartStepsService {
    Write-Section "Starting Service"
    
    Start-Service -Name $ServiceName
    $Service = Get-Service -Name $ServiceName
    
    if ($Service.Status -eq "Running") {
        Write-Host "✓ Service started successfully" -ForegroundColor Green
    }
    else {
        Write-Host "Warning: Service could not be started. Check logs for details." -ForegroundColor Yellow
    }
}

function Installation-Summary {
    Write-Section "Installation Summary"
    
    $NetworkIP = (Get-NetIPAddress | Where-Object {$_.AddressFamily -eq "IPv4" -and $_.PrefixOrigin -ne "WellKnown"} | Select-Object -First 1).IPAddress
    
    Write-Host "Smart Steps AI Professional Persona Module has been installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installation Directory: $InstallDir" -ForegroundColor Cyan
    Write-Host "Configuration Directory: $ConfigDir" -ForegroundColor Cyan
    Write-Host "Log Directory: $LogDir" -ForegroundColor Cyan
    Write-Host "Data Directory: $DataDir" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "API Endpoint: http://$NetworkIP`:8543/api" -ForegroundColor Cyan
    Write-Host "API Key: $ApiKey" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To verify the installation, run: " -NoNewline
    Write-Host "Invoke-WebRequest -Uri http://localhost:8543/api/health -Headers @{Authorization = 'Bearer $ApiKey'}" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Management commands:" -ForegroundColor Cyan
    Write-Host "  - Start service: Start-Service -Name $ServiceName" -ForegroundColor Yellow
    Write-Host "  - Stop service: Stop-Service -Name $ServiceName" -ForegroundColor Yellow
    Write-Host "  - Check status: Get-Service -Name $ServiceName" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For more information, refer to the documentation in $InstallDir\smart_steps_ai\docs" -ForegroundColor Cyan
}

# Main Installation Process
function Main {
    Write-Section "Starting Installation"
    
    Check-Prerequisites
    Create-Directories
    Install-PythonEnvironment
    Configure-Application
    Setup-WindowsService
    Setup-Database
    Final-Setup
    Start-SmartStepsService
    Installation-Summary
    
    Write-Section "Installation Complete"
}

# Execute Main Process
Main
