# Odoo 19.0 Setup Guide

## 📋 Table of Contents
- [Quick Start](#quick-start)
- [Platform-Specific Setup](#platform-specific-setup)
- [Manual Setup](#manual-setup)
- [Verification](#verification)
- [Next Steps](#next-steps)

---

## Quick Start

### One-Command Setup

Choose your platform and run the appropriate setup script:

**macOS**:
```bash
chmod +x setup-odoo-mac.sh && ./setup-odoo-mac.sh
```

**Linux (Ubuntu/Debian)**:
```bash
chmod +x setup-odoo-linux.sh && ./setup-odoo-linux.sh
```

**Windows (PowerShell as Administrator)**:
```powershell
.\setup-odoo-windows.ps1
```

After setup completes, start Odoo:
```bash
./start-odoo.sh  # macOS/Linux
.\start-odoo.ps1  # Windows
```

Then open your browser to: **http://localhost:8069**

---

## Platform-Specific Setup

### 🍎 macOS Setup

#### Prerequisites
- macOS 10.15 (Catalina) or later
- Internet connection
- ~5 GB free disk space

#### Automated Setup
```bash
chmod +x setup-odoo-mac.sh
./setup-odoo-mac.sh
```

#### What Gets Installed
- **Homebrew** - Package manager for macOS
- **Python 3.12** - Latest Python version
- **PostgreSQL 14** - Database server
- **Node.js & npm** - JavaScript runtime
- **wkhtmltopdf** - PDF generation tool
- **libsass** - SCSS compiler

#### Manual Setup (if automated fails)
```bash
# 1. Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install dependencies
brew install python@3.12 postgresql@14 node npm wkhtmltopdf libsass

# 3. Start PostgreSQL
brew services start postgresql@14

# 4. Create database
createdb odoo_test_db

# 5. Create virtual environment
/opt/homebrew/bin/python3.12 -m venv odoo-venv

# 6. Install Python packages
source odoo-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. Make scripts executable
chmod +x start-odoo.sh stop-odoo.sh
```

---

### 🐧 Linux Setup (Ubuntu/Debian)

#### Prerequisites
- Ubuntu 20.04+ or Debian 10+
- Internet connection
- sudo privileges
- ~3 GB free disk space

#### Automated Setup
```bash
chmod +x setup-odoo-linux.sh
./setup-odoo-linux.sh
```

#### What Gets Installed
- **Python 3.12** - Latest Python version
- **PostgreSQL** - Database server
- **Node.js & npm** - JavaScript runtime
- **wkhtmltopdf** - PDF generation tool
- **System libraries** - libxml2, libxslt, libsasl2, libldap2, etc.

#### Manual Setup (if automated fails)
```bash
# 1. Update system
sudo apt-get update
sudo apt-get upgrade -y

# 2. Install dependencies
sudo apt-get install -y \
    python3.12 python3.12-venv python3.12-dev \
    postgresql postgresql-client \
    build-essential libxml2-dev libxslt1-dev \
    libldap2-dev libsasl2-dev libssl-dev \
    libjpeg-dev libpq-dev \
    node-less npm wkhtmltopdf

# 3. Create PostgreSQL user
sudo -u postgres createuser -s $USER

# 4. Create database
createdb odoo_test_db

# 5. Create virtual environment
python3.12 -m venv odoo-venv

# 6. Install Python packages
source odoo-venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 7. Make scripts executable
chmod +x start-odoo.sh stop-odoo.sh
```

---

### 🪟 Windows Setup

#### Prerequisites
- Windows 10/11
- Internet connection
- Administrator privileges
- ~5 GB free disk space

#### Automated Setup
```powershell
# 1. Open PowerShell as Administrator
# Right-click PowerShell → "Run as Administrator"

# 2. Run setup script
.\setup-odoo-windows.ps1
```

#### What Gets Installed
- **Chocolatey** - Package manager for Windows
- **Python 3.12** - Latest Python version
- **PostgreSQL 14** - Database server
- **Git** - Version control
- **Node.js** - JavaScript runtime
- **wkhtmltopdf** - PDF generation tool

#### Manual Setup (if automated fails)
```powershell
# 1. Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. Install dependencies
choco install python312 postgresql14 git nodejs wkhtmltopdf -y

# 3. Refresh environment
refreshenv

# 4. Start PostgreSQL
Start-Service postgresql-x64-14

# 5. Create database
& "C:\Program Files\PostgreSQL\14\bin\createdb.exe" odoo_test_db

# 6. Create virtual environment
python -m venv odoo-venv

# 7. Install Python packages
.\odoo-venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Verification

### 1. Check Virtual Environment
```bash
# macOS/Linux
ls -la odoo-venv/

# Windows
dir odoo-venv\
```

### 2. Check PostgreSQL
```bash
# macOS/Linux
pg_isready
psql -U $USER -d odoo_test_db -c "SELECT version();"

# Windows
& "C:\Program Files\PostgreSQL\14\bin\pg_isready.exe"
```

### 3. Check Python Packages
```bash
# macOS/Linux
source odoo-venv/bin/activate
pip list | grep -E "(psycopg2|werkzeug|libsass)"

# Windows
.\odoo-venv\Scripts\Activate.ps1
pip list | findstr "psycopg2 werkzeug libsass"
```

### 4. Test Configuration
```bash
# macOS/Linux
./odoo-venv/bin/python3 odoo-bin --config=odoo.conf --stop-after-init

# Windows
.\odoo-venv\Scripts\python.exe odoo-bin --config=odoo.conf --stop-after-init
```

You should see:
```
INFO ? odoo: Using configuration file at .../odoo.conf
INFO ? odoo: database: luminous_imteaj@localhost:5432
INFO odoo_test_db odoo.modules.loading: Modules loaded.
```

---

## Next Steps

### 1. Start Odoo
```bash
./start-odoo.sh  # macOS/Linux
.\start-odoo.ps1  # Windows
```

### 2. Access Web Interface
Open your browser to: **http://localhost:8069**

### 3. Login
- **Email**: admin
- **Password**: admin

### 4. Install Apps
Navigate to: **Apps** menu → Install desired modules

### 5. Read Documentation
- [Configuration Guide](CONFIGURATION_GUIDE.md) - Detailed configuration options
- [Scripts Documentation](SCRIPTS_DOCUMENTATION.md) - How to use scripts
- [Troubleshooting](#troubleshooting) - Common issues and solutions

---

## Troubleshooting

### Setup Script Fails

**macOS - Homebrew Installation Fails**:
```bash
# Install Homebrew manually
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Add to PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Linux - Permission Denied**:
```bash
# Make script executable
chmod +x setup-odoo-linux.sh

# Run with bash
bash setup-odoo-linux.sh
```

**Windows - Execution Policy Error**:
```powershell
# Allow script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### PostgreSQL Issues

**Database Creation Fails**:
```bash
# Check PostgreSQL is running
pg_isready

# Create database manually
createdb odoo_test_db
```

**Connection Refused**:
```bash
# macOS
brew services restart postgresql@14

# Linux
sudo systemctl restart postgresql

# Windows
Restart-Service postgresql-x64-14
```

### Python Package Installation Fails

**Compilation Errors**:
```bash
# macOS - Install Xcode Command Line Tools
xcode-select --install

# Linux - Install build tools
sudo apt-get install build-essential python3-dev

# Windows - Install Visual Studio Build Tools
choco install visualstudio2022buildtools -y
```

**Network Errors**:
```bash
# Use alternative PyPI mirror
pip install -r requirements.txt --index-url https://pypi.org/simple
```

---

**Last Updated**: 2025-11-19  
**Odoo Version**: 19.0  
**Supported Platforms**: macOS, Linux (Ubuntu/Debian), Windows 10/11

