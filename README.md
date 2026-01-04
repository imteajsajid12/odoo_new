# Odoo 19.0 ERP System

[![Build Status](https://runbot.odoo.com/runbot/badge/flat/1/master.svg)](https://runbot.odoo.com/runbot)
[![Tech Doc](https://img.shields.io/badge/master-docs-875A7B.svg?style=flat&colorA=8F8F8F)](https://www.odoo.com/documentation/master)
[![Help](https://img.shields.io/badge/master-help-875A7B.svg?style=flat&colorA=8F8F8F)](https://www.odoo.com/forum/help-1)

A comprehensive, production-ready Odoo 19.0 ERP installation featuring 599+ official modules and custom event management capabilities.

## Table of Contents

- [About This Project](#about-this-project)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Detailed Installation](#detailed-installation)
  - [macOS Setup](#macos-setup)
  - [Linux Setup](#linux-setup)
  - [Windows Setup](#windows-setup)
- [Configuration](#configuration)
- [Running Odoo](#running-odoo)
- [Custom Modules](#custom-modules)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

## About This Project

Odoo is a suite of web-based open source business apps. This installation includes:

- **Odoo 19.0** - Latest stable release
- **599 Official Modules** - Complete ERP suite covering all business needs
- **Custom Event Management** - Extended events module with trainer support
- **PostgreSQL 14+** - Robust database backend
- **Production Ready** - Fully configured for both development and deployment

### Main Odoo Applications

- [Open Source CRM](https://www.odoo.com/page/crm)
- [Website Builder](https://www.odoo.com/app/website)
- [eCommerce](https://www.odoo.com/app/ecommerce)
- [Warehouse Management](https://www.odoo.com/app/inventory)
- [Project Management](https://www.odoo.com/app/project)
- [Billing & Accounting](https://www.odoo.com/app/accounting)
- [Point of Sale](https://www.odoo.com/app/point-of-sale-shop)
- [Human Resources](https://www.odoo.com/app/employees)
- [Marketing](https://www.odoo.com/app/social-marketing)
- [Manufacturing](https://www.odoo.com/app/manufacturing)
- [And many more...](https://www.odoo.com/)

## Features

### Core Features
- Multi-company and multi-currency support
- Advanced access rights and security groups
- Comprehensive REST/JSON-RPC/XML-RPC APIs
- Real-time collaboration and messaging
- Mobile-responsive web interface
- Multi-language support with 50+ localizations
- Powerful reporting and analytics
- Automated workflows and business rules

### Custom Features
- **Events Clone Module (v1.0)** - Advanced event management with:
  - Event organization and registration tracking
  - Trainer assignment and management
  - Ticket pricing and seat management
  - Email notifications and activity tracking
  - Stage-based workflow (Kanban view)
  - Barcode support for attendee check-in

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Operating System** | macOS 10.15+, Ubuntu 20.04+, Debian 11+, Windows 10+ |
| **Python** | 3.10 - 3.13 (recommended: 3.12) |
| **PostgreSQL** | 13.0+ (recommended: 14.0+) |
| **RAM** | 2 GB minimum (4 GB recommended) |
| **Disk Space** | 5 GB minimum (10 GB recommended) |
| **Node.js** | 18.0+ (for asset compilation) |

### Python Dependencies

65+ Python packages including:
- `psycopg2` - PostgreSQL adapter
- `lxml` - XML processing
- `Pillow` - Image processing
- `reportlab` - PDF generation
- `Werkzeug` - WSGI web server
- `gevent` - Asynchronous networking
- `Babel` - Internationalization
- And many more (see [requirements.txt](requirements.txt))

## Quick Start

If you're on macOS and want to get started quickly:

```bash
# 1. Clone or navigate to the project directory
cd /path/to/odoo

# 2. Run the setup script (installs all dependencies)
./setup-odoo-mac.sh

# 3. Start Odoo
./start-odoo.sh

# 4. Access Odoo in your browser
# http://localhost:8069
```

Default credentials:
- **Database**: odoo_v1
- **Admin Password**: admin (change in production!)

## Detailed Installation

### macOS Setup

#### Prerequisites
- macOS 10.15 (Catalina) or later
- Homebrew (will be installed automatically if not present)
- Internet connection

#### Step 1: Run Setup Script

```bash
# Make the script executable
chmod +x setup-odoo-mac.sh

# Run the setup script
./setup-odoo-mac.sh
```

The script will automatically:
1. Check macOS version compatibility
2. Install/update Homebrew
3. Install Python 3.12, PostgreSQL 14, Node.js
4. Install system dependencies (wkhtmltopdf, cairo, etc.)
5. Create and configure PostgreSQL database
6. Set up Python virtual environment
7. Install all Python dependencies
8. Configure Odoo

#### Step 2: Verify Installation

```bash
# Check Python version
source odoo-venv/bin/activate
python --version  # Should show Python 3.12.x

# Check PostgreSQL
psql -U $(whoami) -d odoo_v1 -c "SELECT version();"
```

### Linux Setup

#### Prerequisites
- Ubuntu 20.04+, Debian 11+, or equivalent
- sudo privileges
- Internet connection

#### Step 1: Run Setup Script

```bash
# Make the script executable
chmod +x setup-odoo-linux.sh

# Run the setup script
./setup-odoo-linux.sh
```

The script will:
1. Install Python 3.12 and build dependencies
2. Install and configure PostgreSQL
3. Install Node.js and npm
4. Install wkhtmltopdf and graphics libraries
5. Create virtual environment
6. Install Python dependencies

#### Step 2: Configure PostgreSQL

```bash
# Create PostgreSQL user (if needed)
sudo -u postgres createuser -s $USER

# Create database
createdb odoo_v1
```

### Windows Setup

#### Prerequisites
- Windows 10 or later
- PowerShell 5.1 or later
- Administrator privileges

#### Step 1: Run Setup Script

Open PowerShell as Administrator:

```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run setup script
.\setup-odoo-windows.ps1
```

The script will install:
- Python 3.12 via Microsoft Store or official installer
- PostgreSQL 14 via installer
- Node.js and required tools
- Python dependencies

#### Step 2: Manual Steps

1. **Install wkhtmltopdf** (for PDF reports):
   - Download from: https://wkhtmltopdf.org/downloads.html
   - Install to default location
   - Add to system PATH

2. **Configure PostgreSQL**:
   - Open pgAdmin
   - Create database `odoo_v1`
   - Note the password for configuration

## Configuration

### Main Configuration File

The main configuration is in [odoo.conf](odoo.conf):

```ini
[options]
# Database settings
db_host = localhost
db_port = 5432
db_user = luminous_imteaj
db_password =
db_name = odoo_v1

# Server settings
http_interface = 0.0.0.0
http_port = 8069

# Addons path
addons_path = /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/addons,/Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/custom_addons

# Performance (for development)
workers = 0
```

### Important Settings to Customize

#### For Production

```ini
# Change admin password!
admin_passwd = YOUR_SECURE_PASSWORD_HERE

# Enable workers for better performance
workers = 4  # Recommended: (CPU cores * 2) + 1

# Set memory limits
limit_memory_soft = 2147483648
limit_memory_hard = 2684354560

# Configure logging
logfile = /var/log/odoo/odoo.log
log_level = warn
```

#### For Development

```ini
# Single worker for easier debugging
workers = 0

# Verbose logging
log_level = debug
log_handler = :DEBUG

# Enable auto-reload (via command line)
# Use: ./start-odoo.sh --dev
```

### Email Configuration

To send emails from Odoo:

```ini
[options]
email_from = odoo@yourcompany.com
smtp_server = smtp.gmail.com
smtp_port = 587
smtp_ssl = True
smtp_user = your-email@gmail.com
smtp_password = your-app-password
```

## Running Odoo

### Start Odoo Server

#### Normal Mode
```bash
./start-odoo.sh
```

#### Development Mode (auto-reload on file changes)
```bash
./start-odoo.sh --dev
```

#### Debug Mode (verbose logging)
```bash
./start-odoo.sh --debug
```

#### Interactive Shell
```bash
./start-odoo.sh --shell
```

### Stop Odoo Server

```bash
./stop-odoo.sh
```

Or press `Ctrl+C` in the terminal where Odoo is running.

### Access Odoo

1. Open your browser
2. Navigate to: `http://localhost:8069`
3. Create your first database or log in to existing one

**Default Credentials:**
- Master Password: `admin` (set in odoo.conf)
- First login will prompt you to create admin user

### Database Management

Access the database manager at: `http://localhost:8069/web/database/manager`

Master password: `admin` (as configured in odoo.conf)

Operations available:
- Create new database
- Backup/Restore databases
- Delete databases
- Duplicate databases

## Custom Modules

### Events Clone Module

Located in: [custom_addons/events_clone/](custom_addons/events_clone/)

#### Features
- Create and manage events with detailed information
- Track attendee registrations
- Multiple ticket types with pricing
- Trainer assignment (integrated with res.partner)
- Stage-based workflow (New, Confirmed, In Progress, Done, Cancelled)
- Tag categorization system
- Email integration and notifications
- Kanban/Calendar/List views
- Barcode support for check-in
- UTM campaign tracking

#### Installation

1. **Ensure module is in addons path** (already configured):
   ```ini
   addons_path = .../odoo/addons,.../odoo/custom_addons
   ```

2. **Update Apps List**:
   - Log in to Odoo as admin
   - Go to Apps menu
   - Click "Update Apps List"
   - Confirm the update

3. **Install the module**:
   - Remove "Apps" filter to see all modules
   - Search for "Events Clone"
   - Click Install

For detailed usage, see [custom_addons/events_clone/README.md](custom_addons/events_clone/README.md)

## Project Structure

```
odoo/
├── odoo-bin                    # Main executable entry point
├── odoo.conf                   # Server configuration file
├── requirements.txt            # Python dependencies
├── setup.py                    # Installation script
│
├── addons/                     # 599 official Odoo modules
│   ├── account/                # Accounting
│   ├── sale/                   # Sales
│   ├── purchase/               # Purchase
│   ├── hr/                     # Human Resources
│   ├── website/                # Website Builder
│   └── ...                     # And 594 more
│
├── custom_addons/              # Custom modules
│   └── events_clone/           # Event management module
│       ├── models/             # Python models
│       ├── views/              # XML views
│       ├── security/           # Access rights
│       ├── data/               # Demo/default data
│       └── static/             # CSS/JS/Images
│
├── odoo/                       # Core framework
│   ├── api/                    # API layer
│   ├── models/                 # ORM models
│   ├── fields/                 # Field types
│   ├── cli/                    # CLI commands
│   ├── service/                # Services (HTTP, cron)
│   └── tools/                  # Utilities
│
├── odoo-venv/                  # Python virtual environment
│
├── Document/                   # Project documentation
│   ├── PROJECT_OVERVIEW.md
│   ├── SETUP_GUIDE.md
│   ├── RUN_GUIDE.md
│   └── CONFIGURATION_GUIDE.md
│
└── Scripts
    ├── start-odoo.sh           # Start script (macOS/Linux)
    ├── stop-odoo.sh            # Stop script
    ├── setup-odoo-mac.sh       # macOS setup
    ├── setup-odoo-linux.sh     # Linux setup
    └── setup-odoo-windows.ps1  # Windows setup
```

## Development

### Creating a New Module

Use Odoo's scaffold command:

```bash
# Activate virtual environment
source odoo-venv/bin/activate

# Create module skeleton
./odoo-bin scaffold my_module custom_addons/
```

This creates a basic module structure with:
- `__manifest__.py` - Module metadata
- `models/` - Python models
- `views/` - XML views
- `security/` - Access control
- `data/` - Default data

### Enable Developer Mode

Two methods:

1. **Via Settings**:
   - Go to Settings
   - Scroll to bottom
   - Click "Activate the developer mode"

2. **Via URL**:
   - Navigate to: `http://localhost:8069/web?debug=1`

Developer mode enables:
- Technical menu access
- Update Apps List option
- View metadata
- Edit views
- Python debugging

### Debugging

#### Enable Debug Logging

```bash
./start-odoo.sh --debug
```

Or in odoo.conf:
```ini
log_level = debug
log_handler = :DEBUG
```

#### Python Debugger

Add breakpoint in your code:
```python
import pdb; pdb.set_trace()
```

Then run Odoo in single worker mode:
```bash
./odoo-bin -c odoo.conf --workers=0
```

### Running Tests

```bash
# Test specific module
./odoo-bin -c odoo.conf -d odoo_v1 -u events_clone --test-enable --stop-after-init

# Test all modules
./odoo-bin -c odoo.conf -d test_db -i all --test-enable --stop-after-init
```

## Troubleshooting

### Installation Issues

#### PostgreSQL Connection Error

```
Error: could not connect to server
```

**Solution:**
```bash
# macOS
brew services start postgresql@14

# Linux
sudo systemctl start postgresql
```

#### Python Version Mismatch

```
Error: Python 3.10+ required
```

**Solution:**
```bash
# macOS
brew install python@3.12
/opt/homebrew/bin/python3.12 -m venv odoo-venv

# Linux
sudo apt install python3.12 python3.12-venv
python3.12 -m venv odoo-venv
```

#### Missing Dependencies

```
ModuleNotFoundError: No module named 'psycopg2'
```

**Solution:**
```bash
source odoo-venv/bin/activate
pip install -r requirements.txt
```

### Runtime Issues

#### Port Already in Use

```
Error: Address already in use
```

**Solution:**
```bash
# Find process using port 8069
lsof -i :8069

# Kill the process
kill -9 <PID>

# Or change port in odoo.conf
http_port = 8070
```

#### Module Not Found

**Solution:**
1. Check addons_path in odoo.conf includes your module directory
2. Restart Odoo server
3. Update Apps List (Apps menu)
4. Check for syntax errors in `__manifest__.py`

#### Database Lock Error

```
Error: database is being accessed by other users
```

**Solution:**
```bash
# Disconnect all users from database
psql -U $(whoami) -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'odoo_v1';"
```

#### Permission Denied

```
Error: [Errno 13] Permission denied
```

**Solution:**
```bash
# macOS/Linux
chmod -R 755 custom_addons/
chown -R $(whoami) odoo-venv/

# Windows (run as Administrator)
icacls custom_addons /grant Users:F /t
```

### Performance Issues

#### Slow Startup

**Solutions:**
- Reduce number of workers: `workers = 0` (development)
- Increase memory limits in odoo.conf
- Check PostgreSQL performance
- Disable unnecessary modules

#### High Memory Usage

**Solutions:**
```ini
# In odoo.conf
limit_memory_soft = 2147483648  # 2 GB
limit_memory_hard = 2684354560  # 2.5 GB
workers = 2  # Reduce workers
```

## Resources

### Documentation

- **Official Odoo Documentation**: https://www.odoo.com/documentation/19.0/
- **Developer Tutorials**: https://www.odoo.com/documentation/19.0/developer/howtos.html
- **API Reference**: https://www.odoo.com/documentation/19.0/developer/reference.html
- **Project Documentation**: [Document/](Document/) folder

### Learning

- **Odoo eLearning**: https://www.odoo.com/slides
- **Scale-up Business Game**: https://www.odoo.com/page/scale-up-business-game
- **Community Forum**: https://www.odoo.com/forum/help-1

### Support

- **GitHub Issues**: https://github.com/odoo/odoo/issues
- **Community Forums**: https://www.odoo.com/forum
- **Stack Overflow**: Tag `odoo`
- **Security Issues**: https://www.odoo.com/security-report

### Useful Commands

```bash
# Start Odoo
./start-odoo.sh

# Start with development mode
./start-odoo.sh --dev

# Start with debug logging
./start-odoo.sh --debug

# Stop Odoo
./stop-odoo.sh

# Update specific module
./odoo-bin -c odoo.conf -d odoo_v1 -u events_clone

# Install new module
./odoo-bin -c odoo.conf -d odoo_v1 -i module_name

# Create database backup
./odoo-bin -c odoo.conf -d odoo_v1 --db-filter=odoo_v1 --save

# Shell access
./odoo-bin shell -c odoo.conf -d odoo_v1
```

## Security

If you believe you have found a security issue, check the [Responsible Disclosure page](https://www.odoo.com/security-report) and get in touch with Odoo security team.

**Important Security Notes:**
- Change `admin_passwd` in odoo.conf for production
- Use strong database passwords
- Configure firewall rules appropriately
- Keep Odoo and dependencies updated
- Use HTTPS in production (via reverse proxy)
- Regular database backups

## License

Odoo is released under the LGPL-3 license. See the [LICENSE](LICENSE) file for more details.

## Contributing

To contribute to Odoo:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For custom modules, maintain the same code quality standards as the core.

---

**Project Location**: `/Users/luminous_imteaj/Documents/officeWork/Odoo/odoo`

**Version**: Odoo 19.0 (Final Release)

**Last Updated**: January 2026

For more detailed information, refer to the documentation in the [Document/](Document/) folder.
