#!/bin/bash
################################################################################
# ODOO START SCRIPT
################################################################################
# This script starts the Odoo server with the configuration from odoo.conf
# 
# Usage:
#   ./start-odoo.sh              # Start in normal mode
#   ./start-odoo.sh --dev        # Start in development mode with auto-reload
#   ./start-odoo.sh --debug      # Start with debug logging
#   ./start-odoo.sh --help       # Show help
#
# Author: Senior Software Engineer
# Date: November 19, 2025
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Configuration
ODOO_BIN="./odoo-bin"
ODOO_CONF="./odoo.conf"
VENV_PATH="./odoo-venv"
PID_FILE="./odoo.pid"
LOG_FILE="./odoo.log"

################################################################################
# Functions
################################################################################

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    ODOO 19.0 START SCRIPT                      ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found at: $VENV_PATH"
        print_info "Please run setup script first: ./setup-odoo.sh"
        exit 1
    fi
    print_success "Virtual environment found"
    
    # Check if odoo-bin exists
    if [ ! -f "$ODOO_BIN" ]; then
        print_error "Odoo binary not found at: $ODOO_BIN"
        exit 1
    fi
    print_success "Odoo binary found"
    
    # Check if config file exists
    if [ ! -f "$ODOO_CONF" ]; then
        print_error "Configuration file not found at: $ODOO_CONF"
        exit 1
    fi
    print_success "Configuration file found"
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Odoo is already running (PID: $PID)"
            print_info "Use ./stop-odoo.sh to stop it first"
            exit 1
        else
            print_warning "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
    
    echo ""
}

show_help() {
    print_header
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev          Start in development mode with auto-reload"
    echo "  --debug        Start with debug logging"
    echo "  --shell        Start Odoo shell (interactive Python)"
    echo "  --update-all   Update all modules on startup"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start normally"
    echo "  $0 --dev              # Start with auto-reload"
    echo "  $0 --debug            # Start with debug logging"
    echo ""
    exit 0
}

start_odoo() {
    local MODE="$1"
    
    print_header
    check_prerequisites
    
    # Activate virtual environment
    print_info "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    print_success "Virtual environment activated"
    
    # Build command
    CMD="$VENV_PATH/bin/python3 $ODOO_BIN --config=$ODOO_CONF"
    
    # Add mode-specific options
    case "$MODE" in
        dev)
            print_info "Starting Odoo in DEVELOPMENT mode..."
            CMD="$CMD --dev=all"
            ;;
        debug)
            print_info "Starting Odoo in DEBUG mode..."
            CMD="$CMD --log-level=debug"
            ;;
        shell)
            print_info "Starting Odoo SHELL..."
            CMD="$CMD shell"
            exec $CMD
            exit 0
            ;;
        update)
            print_info "Starting Odoo with UPDATE ALL modules..."
            CMD="$CMD --update=all"
            ;;
        *)
            print_info "Starting Odoo in NORMAL mode..."
            ;;
    esac
    
    echo ""
    print_info "Command: $CMD"
    echo ""
    print_info "Starting Odoo server..."
    print_info "Press Ctrl+C to stop"
    echo ""
    print_success "═══════════════════════════════════════════════════════════════"
    echo ""
    
    # Start Odoo and save PID
    $CMD &
    echo $! > "$PID_FILE"
    
    # Wait a moment to check if it started successfully
    sleep 3
    
    if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
        print_success "Odoo started successfully!"
        print_info "PID: $(cat $PID_FILE)"
        print_info "Access Odoo at: http://localhost:8069"
        print_info "Log file: $LOG_FILE"
        echo ""
        
        # Wait for the process
        wait $(cat "$PID_FILE")
    else
        print_error "Failed to start Odoo"
        rm -f "$PID_FILE"
        exit 1
    fi
}

################################################################################
# Main
################################################################################

# Parse arguments
case "${1:-}" in
    --help|-h)
        show_help
        ;;
    --dev)
        start_odoo "dev"
        ;;
    --debug)
        start_odoo "debug"
        ;;
    --shell)
        start_odoo "shell"
        ;;
    --update-all)
        start_odoo "update"
        ;;
    "")
        start_odoo "normal"
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac

