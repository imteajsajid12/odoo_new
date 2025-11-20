################################################################################
# ODOO SETUP SCRIPT FOR WINDOWS
################################################################################
# This script sets up Odoo 19.0 on Windows from scratch
# 
# Prerequisites:
#   - Windows 10 or later
#   - Administrator privileges
#   - Internet connection
#
# Usage:
#   Right-click and "Run with PowerShell" (as Administrator)
#   OR
#   .\setup-odoo-windows.ps1
#
# Author: Senior Software Engineer
# Date: November 19, 2025
################################################################################

# Require Administrator privileges
#Requires -RunAsAdministrator

# Set execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Configuration
$PYTHON_VERSION = "3.12.0"
$POSTGRESQL_VERSION = "14"
$DB_NAME = "odoo_test_db"
$DB_USER = $env:USERNAME

################################################################################
# Functions
################################################################################

function Write-Header {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║              ODOO 19.0 SETUP SCRIPT FOR WINDOWS                ║" -ForegroundColor Blue
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host "  $Message" -ForegroundColor Blue
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Blue
    Write-Host ""
}

function Test-Administrator {
    Write-Step "STEP 1: Checking Administrator Privileges"
    
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if ($isAdmin) {
        Write-Success "Running with Administrator privileges"
    } else {
        Write-Error-Custom "This script requires Administrator privileges"
        Write-Info "Please right-click and select 'Run as Administrator'"
        exit 1
    }
}

function Install-Chocolatey {
    Write-Step "STEP 2: Installing Chocolatey Package Manager"
    
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        Write-Success "Chocolatey already installed"
        choco --version
    } else {
        Write-Info "Installing Chocolatey..."
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        
        if ($?) {
            Write-Success "Chocolatey installed successfully"
        } else {
            Write-Error-Custom "Failed to install Chocolatey"
            exit 1
        }
    }
}

function Install-Dependencies {
    Write-Step "STEP 3: Installing System Dependencies"
    
    Write-Info "Installing Python 3.12..."
    choco install python312 -y
    
    Write-Info "Installing PostgreSQL..."
    choco install postgresql14 -y --params '/Password:odoo123'
    
    Write-Info "Installing Git..."
    choco install git -y
    
    Write-Info "Installing Node.js..."
    choco install nodejs -y
    
    Write-Info "Installing wkhtmltopdf..."
    choco install wkhtmltopdf -y
    
    Write-Success "System dependencies installed"
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

function Setup-PostgreSQL {
    Write-Step "STEP 4: Setting up PostgreSQL"
    
    Write-Info "Starting PostgreSQL service..."
    Start-Service postgresql-x64-14
    
    Start-Sleep -Seconds 3
    
    Write-Info "Creating database user and database..."
    
    # Set PostgreSQL bin path
    $pgPath = "C:\Program Files\PostgreSQL\14\bin"
    
    # Create user (if not exists)
    & "$pgPath\psql.exe" -U postgres -c "CREATE USER $DB_USER WITH CREATEDB PASSWORD 'odoo';" 2>$null
    
    # Create database
    & "$pgPath\createdb.exe" -U postgres -O $DB_USER $DB_NAME 2>$null
    
    Write-Success "PostgreSQL setup complete"
}

function Setup-PythonVenv {
    Write-Step "STEP 5: Setting up Python Virtual Environment"
    
    if (Test-Path "odoo-venv") {
        Write-Warning-Custom "Virtual environment already exists"
        $response = Read-Host "Do you want to recreate it? (y/n)"
        if ($response -eq 'y') {
            Write-Info "Removing existing virtual environment..."
            Remove-Item -Recurse -Force odoo-venv
        } else {
            Write-Info "Skipping virtual environment creation"
            return
        }
    }
    
    Write-Info "Creating virtual environment with Python 3.12..."
    python -m venv odoo-venv
    
    if ($?) {
        Write-Success "Virtual environment created"
    } else {
        Write-Error-Custom "Failed to create virtual environment"
        exit 1
    }
    
    Write-Info "Activating virtual environment..."
    & .\odoo-venv\Scripts\Activate.ps1
    
    Write-Info "Upgrading pip..."
    python -m pip install --upgrade pip
    
    Write-Info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    if ($?) {
        Write-Success "Python dependencies installed"
    } else {
        Write-Error-Custom "Failed to install Python dependencies"
        exit 1
    }
}

function Setup-Configuration {
    Write-Step "STEP 6: Configuring Odoo"
    
    if (Test-Path "odoo.conf") {
        Write-Success "Configuration file already exists: odoo.conf"
        
        # Update config file with Windows paths
        Write-Info "Updating configuration for Windows..."
        $config = Get-Content odoo.conf
        $config = $config -replace 'db_user = .*', "db_user = $DB_USER"
        $config = $config -replace 'db_name = .*', "db_name = $DB_NAME"
        $config = $config -replace 'addons_path = .*', "addons_path = $PWD\addons"
        $config = $config -replace 'data_dir = .*', "data_dir = $env:APPDATA\Odoo"
        $config | Set-Content odoo.conf
    } else {
        Write-Error-Custom "Configuration file not found!"
        Write-Info "Please ensure odoo.conf exists in the project directory"
        exit 1
    }
    
    Write-Success "Configuration updated"
}

function Write-Summary {
    Write-Step "SETUP COMPLETE!"
    
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                    SETUP SUCCESSFUL!                           ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  1. Start Odoo:        " -NoNewline; Write-Host ".\start-odoo.ps1" -ForegroundColor Green
    Write-Host "  2. Stop Odoo:         " -NoNewline; Write-Host ".\stop-odoo.ps1" -ForegroundColor Green
    Write-Host "  3. Access Odoo:       " -NoNewline; Write-Host "http://localhost:8069" -ForegroundColor Green
    Write-Host ""
    Write-Host "Configuration:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Database:             " -NoNewline; Write-Host "$DB_NAME" -ForegroundColor Green
    Write-Host "  Database User:        " -NoNewline; Write-Host "$DB_USER" -ForegroundColor Green
    Write-Host "  HTTP Port:            " -NoNewline; Write-Host "8069" -ForegroundColor Green
    Write-Host "  Config File:          " -NoNewline; Write-Host "odoo.conf" -ForegroundColor Green
    Write-Host ""
    Write-Host "Important:" -ForegroundColor Yellow
    Write-Host "  - Change admin password in odoo.conf for production"
    Write-Host "  - Review and customize odoo.conf settings"
    Write-Host "  - PostgreSQL password is 'odoo' (change in production)"
    Write-Host ""
}

################################################################################
# Main
################################################################################

Write-Header

Test-Administrator
Install-Chocolatey
Install-Dependencies
Setup-PostgreSQL
Setup-PythonVenv
Setup-Configuration
Write-Summary

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

