################################################################################
# ODOO STOP SCRIPT FOR WINDOWS
################################################################################
# This script stops the running Odoo server on Windows
# 
# Usage:
#   .\stop-odoo.ps1              # Stop gracefully
#   .\stop-odoo.ps1 -Force       # Force stop
#   .\stop-odoo.ps1 -Help        # Show help
#
# Author: Senior Software Engineer
# Date: November 19, 2025
################################################################################

param(
    [switch]$Force,
    [switch]$Help
)

# Configuration
$PID_FILE = ".\odoo.pid"

################################################################################
# Functions
################################################################################

function Write-Header {
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║                    ODOO 19.0 STOP SCRIPT                       ║" -ForegroundColor Blue
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
    Write-Host "Usage: .\stop-odoo.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Force        Force stop"
    Write-Host "  -Help         Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\stop-odoo.ps1           # Stop gracefully"
    Write-Host "  .\stop-odoo.ps1 -Force    # Force stop"
    Write-Host ""
    exit 0
}

function Stop-Odoo {
    param([bool]$ForceStop)
    
    Write-Header
    
    # Check if PID file exists
    if (-not (Test-Path $PID_FILE)) {
        Write-Warning-Custom "PID file not found at: $PID_FILE"
        Write-Info "Odoo may not be running or was started manually"
        
        # Try to find Odoo process anyway
        Write-Info "Searching for Odoo processes..."
        $processes = Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*odoo-bin*" }
        
        if ($processes.Count -eq 0) {
            Write-Info "No Odoo processes found"
            exit 0
        } else {
            Write-Warning-Custom "Found Odoo processes:"
            $processes | ForEach-Object { Write-Host "  PID: $($_.Id)" }
            
            $response = Read-Host "Do you want to stop these processes? (y/n)"
            if ($response -ne 'y') {
                Write-Info "Aborted"
                exit 0
            }
            
            foreach ($proc in $processes) {
                if ($ForceStop) {
                    Write-Info "Force stopping process $($proc.Id)..."
                    Stop-Process -Id $proc.Id -Force
                } else {
                    Write-Info "Stopping process $($proc.Id) gracefully..."
                    Stop-Process -Id $proc.Id
                }
            }
            
            Start-Sleep -Seconds 2
            Write-Success "Odoo stopped"
            exit 0
        }
    }
    
    # Read PID from file
    $PID = Get-Content $PID_FILE
    
    # Check if process is running
    if (-not (Get-Process -Id $PID -ErrorAction SilentlyContinue)) {
        Write-Warning-Custom "Process $PID is not running"
        Write-Info "Removing stale PID file..."
        Remove-Item $PID_FILE
        Write-Success "Cleaned up"
        exit 0
    }
    
    # Stop the process
    if ($ForceStop) {
        Write-Info "Force stopping Odoo (PID: $PID)..."
        Stop-Process -Id $PID -Force
        
        if ($?) {
            Write-Success "Odoo force stopped"
        } else {
            Write-Error-Custom "Failed to stop Odoo"
            exit 1
        }
    } else {
        Write-Info "Stopping Odoo gracefully (PID: $PID)..."
        Stop-Process -Id $PID
        
        if ($?) {
            # Wait for process to stop (max 30 seconds)
            Write-Info "Waiting for Odoo to stop..."
            $timeout = 30
            $elapsed = 0
            
            while ((Get-Process -Id $PID -ErrorAction SilentlyContinue) -and ($elapsed -lt $timeout)) {
                Start-Sleep -Seconds 1
                $elapsed++
                Write-Host "." -NoNewline
            }
            Write-Host ""
            
            # Check if stopped
            if (Get-Process -Id $PID -ErrorAction SilentlyContinue) {
                Write-Warning-Custom "Odoo did not stop gracefully"
                Write-Info "Use -Force to force stop"
                exit 1
            } else {
                Write-Success "Odoo stopped gracefully"
            }
        } else {
            Write-Error-Custom "Failed to stop Odoo"
            exit 1
        }
    }
    
    # Remove PID file
    Remove-Item $PID_FILE -ErrorAction SilentlyContinue
    Write-Success "Cleaned up PID file"
    Write-Host ""
}

################################################################################
# Main
################################################################################

if ($Help) {
    Show-Help
}

Stop-Odoo -ForceStop $Force

