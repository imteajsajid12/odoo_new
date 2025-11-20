#!/bin/bash
################################################################################
# ODOO SETUP SCRIPT FOR LINUX (Ubuntu/Debian)
################################################################################
# This script sets up Odoo 19.0 on Ubuntu/Debian Linux from scratch
# 
# Prerequisites:
#   - Ubuntu 20.04+ or Debian 11+
#   - sudo privileges
#   - Internet connection
#
# Usage:
#   ./setup-odoo-linux.sh
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
DB_USER=$(whoami)
DB_NAME="odoo_test_db"

################################################################################
# Functions
################################################################################

print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              ODOO 19.0 SETUP SCRIPT FOR LINUX                  ║${NC}"
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

check_linux() {
    print_step "STEP 1: Checking Linux Distribution"
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        print_success "Distribution: $NAME $VERSION"
        
        if [[ "$ID" != "ubuntu" && "$ID" != "debian" ]]; then
            print_warning "This script is optimized for Ubuntu/Debian"
            print_warning "It may work on other distributions but is not tested"
        fi
    else
        print_warning "Cannot determine Linux distribution"
    fi
}

install_system_dependencies() {
    print_step "STEP 2: Installing System Dependencies"
    
    print_info "Updating package list..."
    sudo apt-get update
    
    print_info "Installing Python 3.12 and development tools..."
    sudo apt-get install -y \
        python3.12 \
        python3.12-venv \
        python3.12-dev \
        python3-pip \
        build-essential \
        wget \
        git \
        libxml2-dev \
        libxslt1-dev \
        libevent-dev \
        libsasl2-dev \
        libldap2-dev \
        libpq-dev \
        libjpeg-dev \
        libpng-dev \
        libfreetype6-dev \
        zlib1g-dev \
        fonts-liberation \
        libssl-dev \
        node-less \
        npm
    
    if [ $? -eq 0 ]; then
        print_success "System dependencies installed"
    else
        print_error "Failed to install system dependencies"
        exit 1
    fi
    
    print_info "Installing wkhtmltopdf..."
    sudo apt-get install -y wkhtmltopdf || print_warning "wkhtmltopdf installation failed, will continue"
}

install_postgresql() {
    print_step "STEP 3: Installing and Configuring PostgreSQL"
    
    print_info "Installing PostgreSQL..."
    sudo apt-get install -y postgresql postgresql-contrib
    
    if [ $? -eq 0 ]; then
        print_success "PostgreSQL installed"
    else
        print_error "Failed to install PostgreSQL"
        exit 1
    fi
    
    print_info "Starting PostgreSQL service..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    print_success "PostgreSQL service started"
}

setup_postgresql() {
    print_step "STEP 4: Setting up PostgreSQL Database"
    
    # Create PostgreSQL user
    print_info "Creating PostgreSQL user: $DB_USER"
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH CREATEDB;" 2>/dev/null || print_warning "User may already exist"
    
    # Create database
    print_info "Creating database: $DB_NAME"
    sudo -u postgres createdb -O $DB_USER $DB_NAME 2>/dev/null || print_warning "Database may already exist"
    
    print_success "PostgreSQL setup complete"
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
    python3.12 -m venv odoo-venv
    
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
    
    print_info "Activating virtual environment..."
    source odoo-venv/bin/activate
    
    print_info "Upgrading pip..."
    pip install --upgrade pip wheel setuptools
    
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
        
        # Update config file with current user
        print_info "Updating configuration with current user..."
        sed -i "s/db_user = .*/db_user = $DB_USER/" odoo.conf
        sed -i "s/db_name = .*/db_name = $DB_NAME/" odoo.conf
    else
        print_error "Configuration file not found!"
        print_info "Please ensure odoo.conf exists in the project directory"
        exit 1
    fi
    
    # Make scripts executable
    print_info "Making scripts executable..."
    chmod +x start-odoo.sh stop-odoo.sh setup-odoo-linux.sh
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
    echo -e "  Database:             ${GREEN}$DB_NAME${NC}"
    echo -e "  Database User:        ${GREEN}$DB_USER${NC}"
    echo -e "  HTTP Port:            ${GREEN}8069${NC}"
    echo -e "  Config File:          ${GREEN}odoo.conf${NC}"
    echo ""
    echo -e "${YELLOW}Important:${NC}"
    echo -e "  - Change admin password in odoo.conf for production"
    echo -e "  - Review and customize odoo.conf settings"
    echo -e "  - PostgreSQL is running as a systemd service"
    echo ""
}

################################################################################
# Main
################################################################################

print_header

check_linux
install_system_dependencies
install_postgresql
setup_postgresql
setup_python_venv
setup_configuration
print_summary

