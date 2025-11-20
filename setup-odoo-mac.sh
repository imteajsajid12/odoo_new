#!/bin/bash
################################################################################
# ODOO SETUP SCRIPT FOR macOS
################################################################################
# This script sets up Odoo 19.0 on macOS from scratch
# 
# Prerequisites:
#   - macOS 10.15 or later
#   - Homebrew (will be installed if not present)
#   - Internet connection
#
# Usage:
#   ./setup-odoo-mac.sh
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

################################################################################
# Functions
################################################################################

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              ODOO 19.0 SETUP SCRIPT FOR macOS                  ║${NC}"
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

print_step() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

check_macos() {
    print_step "STEP 1: Checking macOS Version"
    
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script is for macOS only"
        exit 1
    fi
    
    MACOS_VERSION=$(sw_vers -productVersion)
    print_success "macOS version: $MACOS_VERSION"
}

install_homebrew() {
    print_step "STEP 2: Installing Homebrew"
    
    if command -v brew &> /dev/null; then
        print_success "Homebrew already installed"
        brew --version
    else
        print_info "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        if [ $? -eq 0 ]; then
            print_success "Homebrew installed successfully"
        else
            print_error "Failed to install Homebrew"
            exit 1
        fi
    fi
}

install_dependencies() {
    print_step "STEP 3: Installing System Dependencies"
    
    print_info "Updating Homebrew..."
    brew update
    
    print_info "Installing Python 3.12..."
    brew install python@3.12 || print_warning "Python 3.12 may already be installed"
    
    print_info "Installing PostgreSQL..."
    brew install postgresql@14 || print_warning "PostgreSQL may already be installed"
    
    print_info "Installing other dependencies..."
    brew install node npm wkhtmltopdf libsass || print_warning "Some packages may already be installed"
    
    print_success "System dependencies installed"
}

setup_postgresql() {
    print_step "STEP 4: Setting up PostgreSQL"
    
    print_info "Starting PostgreSQL service..."
    brew services start postgresql@14
    
    sleep 3
    
    # Check if database exists
    if psql -U $(whoami) -lqt | cut -d \| -f 1 | grep -qw odoo_test_db; then
        print_success "Database 'odoo_test_db' already exists"
    else
        print_info "Creating database 'odoo_test_db'..."
        createdb odoo_test_db
        
        if [ $? -eq 0 ]; then
            print_success "Database created successfully"
        else
            print_error "Failed to create database"
            exit 1
        fi
    fi
}

setup_python_venv() {
    print_step "STEP 5: Setting up Python Virtual Environment"
    
    if [ -d "odoo-venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing virtual environment..."
            rm -rf odoo-venv
        else
            print_info "Skipping virtual environment creation"
            return 0
        fi
    fi
    
    print_info "Creating virtual environment with Python 3.12..."
    /opt/homebrew/bin/python3.12 -m venv odoo-venv
    
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    print_info "Activating virtual environment..."
    source odoo-venv/bin/activate
    
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    print_info "Installing Python dependencies..."
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "Python dependencies installed"
    else
        print_error "Failed to install Python dependencies"
        exit 1
    fi
}

setup_configuration() {
    print_step "STEP 6: Configuring Odoo"
    
    if [ -f "odoo.conf" ]; then
        print_success "Configuration file already exists: odoo.conf"
    else
        print_error "Configuration file not found!"
        print_info "Please ensure odoo.conf exists in the project directory"
        exit 1
    fi
    
    # Make scripts executable
    print_info "Making scripts executable..."
    chmod +x start-odoo.sh stop-odoo.sh setup-odoo-mac.sh
    print_success "Scripts are now executable"
}

print_summary() {
    print_step "SETUP COMPLETE!"
    
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    SETUP SUCCESSFUL!                           ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo ""
    echo -e "  1. Start Odoo:        ${GREEN}./start-odoo.sh${NC}"
    echo -e "  2. Stop Odoo:         ${GREEN}./stop-odoo.sh${NC}"
    echo -e "  3. Access Odoo:       ${GREEN}http://localhost:8069${NC}"
    echo ""
    echo -e "${BLUE}Configuration:${NC}"
    echo ""
    echo -e "  Database:             ${GREEN}odoo_test_db${NC}"
    echo -e "  Database User:        ${GREEN}$(whoami)${NC}"
    echo -e "  HTTP Port:            ${GREEN}8069${NC}"
    echo -e "  Config File:          ${GREEN}odoo.conf${NC}"
    echo ""
    echo -e "${YELLOW}Important:${NC}"
    echo -e "  - Change admin password in odoo.conf for production"
    echo -e "  - Review and customize odoo.conf settings"
    echo -e "  - PostgreSQL is running as a service"
    echo ""
}

################################################################################
# Main
################################################################################

print_header

check_macos
install_homebrew
install_dependencies
setup_postgresql
setup_python_venv
setup_configuration
print_summary

