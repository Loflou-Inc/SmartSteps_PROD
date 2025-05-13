# Smart Steps AI Professional Persona Module - Unity Package Installation Script
# This script installs the Unity integration package for the Smart Steps application

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
     AI Professional Persona Module - Unity Package Installation
" -ForegroundColor Cyan

# Configuration Variables
$PackageName = "com.smartsteps.ai"
$PackageDisplayName = "Smart Steps AI Professional Persona"
$UnityProjectPath = ""
$PackageSourcePath = "$PSScriptRoot\..\unity_package"
$ApiEndpoint = ""
$ApiKey = ""

# Helper Functions
function Write-Section {
    param (
        [string]$Title
    )
    
    Write-Host "`n------------------------------------------------------" -ForegroundColor Yellow
    Write-Host "  $Title" -ForegroundColor Yellow
    Write-Host "------------------------------------------------------" -ForegroundColor Yellow
}

function Get-UserInput {
    param (
        [string]$Prompt,
        [string]$Default = "",
        [switch]$Required
    )
    
    $PromptText = "$Prompt"
    if ($Default -ne "") {
        $PromptText += " (default: $Default)"
    }
    $PromptText += ": "
    
    do {
        Write-Host $PromptText -NoNewline -ForegroundColor Cyan
        $Input = Read-Host
        
        if ($Input -eq "" -and $Default -ne "") {
            $Input = $Default
        }
        
        if ($Required -and $Input -eq "") {
            Write-Host "  This field is required." -ForegroundColor Red
        }
    } while ($Required -and $Input -eq "")
    
    return $Input
}

function Test-UnityProject {
    param (
        [string]$Path
    )
    
    if (-not (Test-Path $Path)) {
        return $false
    }
    
    if (-not (Test-Path "$Path\Assets") -or -not (Test-Path "$Path\ProjectSettings")) {
        return $false
    }
    
    return $true
}

function Test-ApiConnection {
    param (
        [string]$Endpoint,
        [string]$Key
    )
    
    try {
        $Response = Invoke-WebRequest -Uri "$Endpoint/health" -Headers @{
            "Authorization" = "Bearer $Key"
        } -UseBasicParsing
        
        if ($Response.StatusCode -eq 200) {
            $Content = $Response.Content | ConvertFrom-Json
            if ($Content.status -eq "ok") {
                return $true
            }
        }
        
        return $false
    }
    catch {
        return $false
    }
}

function Copy-PackageFiles {
    param (
        [string]$ProjectPath,
        [string]$PackagePath
    )
    
    # Create the package directory in the Unity project
    $DestinationPath = Join-Path $ProjectPath "Packages\$PackageName"
    
    # Create directory if it doesn't exist
    if (-not (Test-Path $DestinationPath)) {
        New-Item -Path $DestinationPath -ItemType Directory -Force | Out-Null
    }
    
    # Copy package files
    Copy-Item -Path "$PackagePath\*" -Destination $DestinationPath -Recurse -Force
    
    return $DestinationPath
}

function Configure-Package {
    param (
        [string]$PackagePath,
        [string]$ApiEndpoint,
        [string]$ApiKey
    )
    
    # Create configuration file
    $ConfigPath = Join-Path $PackagePath "Runtime\Resources"
    
    if (-not (Test-Path $ConfigPath)) {
        New-Item -Path $ConfigPath -ItemType Directory -Force | Out-Null
    }
    
    $ConfigContent = @"
{
    "apiEndpoint": "$ApiEndpoint",
    "apiKey": "$ApiKey",
    "defaultPersona": "dr_morgan_hayes",
    "logLevel": "INFO",
    "useEncryption": true,
    "cacheTimeoutMinutes": 30,
    "enableOfflineMode": true,
    "syncIntervalMinutes": 60
}
"@
    
    $ConfigContent | Out-File -FilePath "$ConfigPath\SmartStepsAIConfig.json" -Encoding utf8
    
    Write-Host "✓ Configuration file created" -ForegroundColor Green
}

function Create-SampleScene {
    param (
        [string]$ProjectPath
    )
    
    $SampleScenePath = Join-Path $ProjectPath "Assets\Scenes\SmartStepsAISample.unity"
    $SampleSceneDir = Join-Path $ProjectPath "Assets\Scenes"
    
    if (-not (Test-Path $SampleSceneDir)) {
        New-Item -Path $SampleSceneDir -ItemType Directory -Force | Out-Null
    }
    
    # Copy sample scene if it exists in the package
    $SourceScenePath = Join-Path $PackageSourcePath "Samples~/SampleScene/SmartStepsAISample.unity"
    
    if (Test-Path $SourceScenePath) {
        Copy-Item -Path $SourceScenePath -Destination $SampleScenePath -Force
        Write-Host "✓ Sample scene created at $SampleScenePath" -ForegroundColor Green
    }
    else {
        Write-Host "Sample scene template not found. You'll need to create a scene manually." -ForegroundColor Yellow
    }
}

function Installation-Summary {
    Write-Section "Installation Summary"
    
    Write-Host "Smart Steps AI Professional Persona Module has been installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Package Information:" -ForegroundColor Cyan
    Write-Host "  Package Name: $PackageName" -ForegroundColor Cyan
    Write-Host "  Installation Path: Packages\$PackageName" -ForegroundColor Cyan
    Write-Host "  Unity Project: $UnityProjectPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "API Connection:" -ForegroundColor Cyan
    Write-Host "  Endpoint: $ApiEndpoint" -ForegroundColor Cyan
    Write-Host "  API Key: $(if ($ApiKey.Length -gt 8) { $ApiKey.Substring(0, 4) + "..." + $ApiKey.Substring($ApiKey.Length - 4) } else { "Not configured" })" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Green
    Write-Host "  1. Open your Unity project" -ForegroundColor Yellow
    Write-Host "  2. Wait for Unity to detect and import the new package" -ForegroundColor Yellow
    Write-Host "  3. Open the sample scene at Assets/Scenes/SmartStepsAISample.unity" -ForegroundColor Yellow
    Write-Host "  4. Refer to the documentation at Packages/$PackageName/Documentation~/index.md" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For more information, visit the Smart Steps documentation." -ForegroundColor Cyan
}

# Main Installation Process
function Main {
    Write-Section "Starting Unity Package Installation"
    
    # Get Unity project path
    Write-Host "Please provide the path to your Unity project:" -ForegroundColor Cyan
    $UnityProjectPath = Get-UserInput -Prompt "Unity Project Path" -Required
    
    # Validate Unity project
    if (-not (Test-UnityProject $UnityProjectPath)) {
        Write-Host "Error: The specified path does not appear to be a valid Unity project." -ForegroundColor Red
        Write-Host "A valid Unity project should contain 'Assets' and 'ProjectSettings' folders." -ForegroundColor Red
        exit 1
    }
    
    # Get API endpoint and key
    Write-Host "`nPlease provide the Smart Steps AI API information:" -ForegroundColor Cyan
    $ApiEndpoint = Get-UserInput -Prompt "API Endpoint (e.g., http://localhost:8543/api)" -Required
    $ApiKey = Get-UserInput -Prompt "API Key" -Required
    
    # Test API connection
    Write-Host "`nTesting API connection..." -ForegroundColor Yellow
    if (-not (Test-ApiConnection -Endpoint $ApiEndpoint -Key $ApiKey)) {
        Write-Host "Warning: Could not connect to the API. The package will be installed but may not function correctly." -ForegroundColor Yellow
        Write-Host "Please check your API endpoint and key, and ensure the server is running." -ForegroundColor Yellow
        
        $Continue = Get-UserInput -Prompt "Continue anyway? (y/n)" -Default "n"
        if ($Continue -ne "y") {
            Write-Host "Installation cancelled." -ForegroundColor Red
            exit
        }
    }
    else {
        Write-Host "✓ API connection successful" -ForegroundColor Green
    }
    
    # Check if package source exists
    if (-not (Test-Path $PackageSourcePath)) {
        Write-Host "Error: Package source not found at $PackageSourcePath" -ForegroundColor Red
        exit 1
    }
    
    # Copy package files
    Write-Section "Installing Package Files"
    $InstalledPath = Copy-PackageFiles -ProjectPath $UnityProjectPath -PackagePath $PackageSourcePath
    Write-Host "✓ Package files copied to $InstalledPath" -ForegroundColor Green
    
    # Configure package
    Write-Section "Configuring Package"
    Configure-Package -PackagePath $InstalledPath -ApiEndpoint $ApiEndpoint -ApiKey $ApiKey
    
    # Create sample scene
    Write-Section "Setting Up Sample Scene"
    Create-SampleScene -ProjectPath $UnityProjectPath
    
    # Installation summary
    Installation-Summary
    
    Write-Section "Installation Complete"
}

# Execute Main Process
Main
