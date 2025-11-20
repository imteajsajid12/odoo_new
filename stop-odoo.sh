#!/bin/bash
################################################################################
# ODOO STOP SCRIPT
################################################################################
# This script stops the running Odoo server
# 
# Usage:
#   ./stop-odoo.sh              # Stop gracefully
#   ./stop-odoo.sh --force      # Force stop (kill -9)
#   ./stop-odoo.sh --help       # Show help
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
PID_FILE="./odoo.pid"

################################################################################
# Functions
################################################################################

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    ODOO 19.0 STOP SCRIPT                       ║${NC}"
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

show_help() {
    print_header
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --force        Force stop (kill -9)"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0             # Stop gracefully"
    echo "  $0 --force     # Force stop"
    echo ""
    exit 0
}

stop_odoo() {
    local FORCE="$1"
    
    print_header
    
    # Check if PID file exists
    if [ ! -f "$PID_FILE" ]; then
        print_warning "PID file not found at: $PID_FILE"
        print_info "Odoo may not be running or was started manually"
        
        # Try to find Odoo process anyway
        print_info "Searching for Odoo processes..."
        ODOO_PIDS=$(pgrep -f "odoo-bin")
        
        if [ -z "$ODOO_PIDS" ]; then
            print_info "No Odoo processes found"
            exit 0
        else
            print_warning "Found Odoo processes: $ODOO_PIDS"
            read -p "Do you want to stop these processes? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_info "Aborted"
                exit 0
            fi
            
            for PID in $ODOO_PIDS; do
                if [ "$FORCE" = "force" ]; then
                    print_info "Force killing process $PID..."
                    kill -9 "$PID" 2>/dev/null
                else
                    print_info "Stopping process $PID gracefully..."
                    kill "$PID" 2>/dev/null
                fi
            done
            
            sleep 2
            print_success "Odoo stopped"
            exit 0
        fi
    fi
    
    # Read PID from file
    PID=$(cat "$PID_FILE")
    
    # Check if process is running
    if ! ps -p "$PID" > /dev/null 2>&1; then
        print_warning "Process $PID is not running"
        print_info "Removing stale PID file..."
        rm -f "$PID_FILE"
        print_success "Cleaned up"
        exit 0
    fi
    
    # Stop the process
    if [ "$FORCE" = "force" ]; then
        print_info "Force stopping Odoo (PID: $PID)..."
        kill -9 "$PID" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            print_success "Odoo force stopped"
        else
            print_error "Failed to stop Odoo"
            exit 1
        fi
    else
        print_info "Stopping Odoo gracefully (PID: $PID)..."
        kill "$PID" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            # Wait for process to stop (max 30 seconds)
            print_info "Waiting for Odoo to stop..."
            for i in {1..30}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    break
                fi
                sleep 1
                echo -n "."
            done
            echo ""
            
            # Check if stopped
            if ps -p "$PID" > /dev/null 2>&1; then
                print_warning "Odoo did not stop gracefully"
                print_info "Use --force to force stop"
                exit 1
            else
                print_success "Odoo stopped gracefully"
            fi
        else
            print_error "Failed to stop Odoo"
            exit 1
        fi
    fi
    
    # Remove PID file
    rm -f "$PID_FILE"
    print_success "Cleaned up PID file"
    echo ""
}

################################################################################
# Main
################################################################################

# Parse arguments
case "${1:-}" in
    --help|-h)
        show_help
        ;;
    --force|-f)
        stop_odoo "force"
        ;;
    "")
        stop_odoo "normal"
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac

