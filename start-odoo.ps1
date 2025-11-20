################################################################################
# ODOO START SCRIPT FOR WINDOWS
################################################################################
# This script starts the Odoo server on Windows
# 
# Usage:
#   .\start-odoo.ps1              # Start in normal mode
#   .\start-odoo.ps1 -Dev         # Start in development mode
#   .\start-odoo.ps1 -Debug       # Start with debug logging
#   .\start-odoo.ps1 -Help        # Show help
#
# Author: Senior Software Engineer
# Date: November 19, 2025
################################################################################

param(
    [switch]$Dev,
    [switch]$Debug,
    [switch]$Shell,
    [switch]$UpdateAll,
    [switch]$Help
)

# Configuration
$ODOO_BIN = ".\odoo-bin"
$ODOO_CONF = ".\odoo.conf"
$VENV_PATH = ".\odoo-venv"
$PID_FILE = ".\odoo.pid"

################################################################################
# Functions
################################################################################

function Write-Header {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║                    ODOO 19.0 START SCRIPT                      ║" -ForegroundColor Blue
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

function Show-Help {
    Write-Header
    Write-Host "Usage: .\start-odoo.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Dev          Start in development mode with auto-reload"
    Write-Host "  -Debug        Start with debug logging"
    Write-Host "  -Shell        Start Odoo shell (interactive Python)"
    Write-Host "  -UpdateAll    Update all modules on startup"
    Write-Host "  -Help         Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\start-odoo.ps1                # Start normally"
    Write-Host "  .\start-odoo.ps1 -Dev           # Start with auto-reload"
    Write-Host "  .\start-odoo.ps1 -Debug         # Start with debug logging"
    Write-Host ""
    exit 0
}

function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check virtual environment
    if (-not (Test-Path $VENV_PATH)) {
        Write-Error-Custom "Virtual environment not found at: $VENV_PATH"
        Write-Info "Please run setup script first: .\setup-odoo-windows.ps1"
        exit 1
    }
    Write-Success "Virtual environment found"
    
    # Check odoo-bin
    if (-not (Test-Path $ODOO_BIN)) {
        Write-Error-Custom "Odoo binary not found at: $ODOO_BIN"
        exit 1
    }
    Write-Success "Odoo binary found"
    
    # Check config file
    if (-not (Test-Path $ODOO_CONF)) {
        Write-Error-Custom "Configuration file not found at: $ODOO_CONF"
        exit 1
    }
    Write-Success "Configuration file found"
    
    # Check if already running
    if (Test-Path $PID_FILE) {
        $PID = Get-Content $PID_FILE
        if (Get-Process -Id $PID -ErrorAction SilentlyContinue) {
            Write-Warning-Custom "Odoo is already running (PID: $PID)"
            Write-Info "Use .\stop-odoo.ps1 to stop it first"
            exit 1
        } else {
            Write-Warning-Custom "Stale PID file found, removing..."
            Remove-Item $PID_FILE
        }
    }
    
    Write-Host ""
}

function Start-Odoo {
    param([string]$Mode)
    
    Write-Header
    Test-Prerequisites
    
    # Activate virtual environment
    Write-Info "Activating virtual environment..."
    & "$VENV_PATH\Scripts\Activate.ps1"
    Write-Success "Virtual environment activated"
    
    # Build command
    $CMD = "python $ODOO_BIN --config=$ODOO_CONF"
    
    # Add mode-specific options
    switch ($Mode) {
        "dev" {
            Write-Info "Starting Odoo in DEVELOPMENT mode..."
            $CMD += " --dev=all"
        }
        "debug" {
            Write-Info "Starting Odoo in DEBUG mode..."
            $CMD += " --log-level=debug"
        }
        "shell" {
            Write-Info "Starting Odoo SHELL..."
            $CMD += " shell"
            Invoke-Expression $CMD
            exit 0
        }
        "update" {
            Write-Info "Starting Odoo with UPDATE ALL modules..."
            $CMD += " --update=all"
        }
        default {
            Write-Info "Starting Odoo in NORMAL mode..."
        }
    }
    
    Write-Host ""
    Write-Info "Command: $CMD"
    Write-Host ""
    Write-Info "Starting Odoo server..."
    Write-Info "Press Ctrl+C to stop"
    Write-Host ""
    Write-Success "═══════════════════════════════════════════════════════════════"
    Write-Host ""
    
    # Start Odoo
    $process = Start-Process -FilePath "python" -ArgumentList "$ODOO_BIN --config=$ODOO_CONF" -PassThru -NoNewWindow
    $process.Id | Out-File $PID_FILE
    
    # Wait a moment to check if it started
    Start-Sleep -Seconds 3
    
    if (Get-Process -Id $process.Id -ErrorAction SilentlyContinue) {
        Write-Success "Odoo started successfully!"
        Write-Info "PID: $($process.Id)"
        Write-Info "Access Odoo at: http://localhost:8069"
        Write-Host ""
        
        # Wait for the process
        Wait-Process -Id $process.Id
    } else {
        Write-Error-Custom "Failed to start Odoo"
        Remove-Item $PID_FILE -ErrorAction SilentlyContinue
        exit 1
    }
}

################################################################################
# Main
################################################################################

if ($Help) {
    Show-Help
}

if ($Dev) {
    Start-Odoo "dev"
} elseif ($Debug) {
    Start-Odoo "debug"
} elseif ($Shell) {
    Start-Odoo "shell"
} elseif ($UpdateAll) {
    Start-Odoo "update"
} else {
    Start-Odoo "normal"
}

