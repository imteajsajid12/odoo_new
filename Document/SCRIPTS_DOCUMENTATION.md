# Odoo 19.0 Scripts Documentation

## 📋 Table of Contents
- [Start Script](#start-script)
- [Stop Script](#stop-script)
- [Setup Scripts](#setup-scripts)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)

---

## Start Script

### `start-odoo.sh` (macOS/Linux)

**Purpose**: Start the Odoo server with various modes

**Usage**:
```bash
./start-odoo.sh [OPTIONS]
```

**Options**:
- `--dev` - Start in development mode with auto-reload
- `--debug` - Start with debug logging
- `--shell` - Start Odoo shell (interactive Python)
- `--update-all` - Update all modules on startup
- `--help` - Show help message

**Examples**:
```bash
# Start normally
./start-odoo.sh

# Start with auto-reload (watches file changes)
./start-odoo.sh --dev

# Start with debug logging
./start-odoo.sh --debug

# Open Odoo Python shell
./start-odoo.sh --shell

# Update all modules and start
./start-odoo.sh --update-all
```

**Features**:
- ✅ Checks prerequisites (virtual environment, odoo-bin, config file)
- ✅ Creates PID file for process management
- ✅ Color-coded output for easy reading
- ✅ Runs in background (daemon mode)
- ✅ Loads configuration from `odoo.conf`

**PID File Location**: `.odoo.pid`

---

### `start-odoo.ps1` (Windows)

**Purpose**: Start the Odoo server on Windows

**Usage**:
```powershell
.\start-odoo.ps1 [OPTIONS]
```

**Options**: Same as Unix version

**Examples**:
```powershell
# Start normally
.\start-odoo.ps1

# Start in development mode
.\start-odoo.ps1 -dev
```

---

## Stop Script

### `stop-odoo.sh` (macOS/Linux)

**Purpose**: Stop the running Odoo server gracefully or forcefully

**Usage**:
```bash
./stop-odoo.sh [OPTIONS]
```

**Options**:
- `--force` - Force stop (kill -9)
- `--help` - Show help message

**Examples**:
```bash
# Stop gracefully (recommended)
./stop-odoo.sh

# Force stop (if graceful fails)
./stop-odoo.sh --force
```

**How It Works**:
1. Reads PID from `.odoo.pid` file
2. Sends SIGTERM signal (graceful shutdown)
3. Waits up to 30 seconds for process to exit
4. If `--force` is used, sends SIGKILL (immediate termination)
5. Removes PID file

**Graceful vs Force Stop**:
- **Graceful** (`./stop-odoo.sh`):
  - Allows Odoo to finish current requests
  - Closes database connections properly
  - Saves pending data
  - **Recommended for normal use**

- **Force** (`./stop-odoo.sh --force`):
  - Immediately terminates process
  - May lose unsaved data
  - **Use only when graceful fails**

---

### `stop-odoo.ps1` (Windows)

**Purpose**: Stop the running Odoo server on Windows

**Usage**:
```powershell
.\stop-odoo.ps1 [OPTIONS]
```

**Options**: Same as Unix version

**Examples**:
```powershell
# Stop gracefully
.\stop-odoo.ps1

# Force stop
.\stop-odoo.ps1 -force
```

---

## Setup Scripts

### `setup-odoo-mac.sh` (macOS)

**Purpose**: First-time setup on macOS

**What It Does**:
1. ✅ Checks macOS version compatibility
2. ✅ Installs Homebrew (if not installed)
3. ✅ Installs Python 3.12, PostgreSQL 14, Node.js, wkhtmltopdf
4. ✅ Starts PostgreSQL service
5. ✅ Creates database `odoo_test_db`
6. ✅ Creates Python virtual environment
7. ✅ Installs Python dependencies
8. ✅ Makes scripts executable
9. ✅ Updates `odoo.conf` with current user

**Usage**:
```bash
chmod +x setup-odoo-mac.sh
./setup-odoo-mac.sh
```

**Prerequisites**:
- macOS 10.15 or later
- Internet connection
- Administrator privileges (for Homebrew)

**Time**: ~15-30 minutes (depending on internet speed)

---

### `setup-odoo-linux.sh` (Ubuntu/Debian)

**Purpose**: First-time setup on Ubuntu/Debian Linux

**What It Does**:
1. ✅ Checks Linux distribution
2. ✅ Installs system dependencies via apt-get
3. ✅ Installs PostgreSQL
4. ✅ Creates PostgreSQL user and database
5. ✅ Creates Python virtual environment
6. ✅ Installs Python dependencies
7. ✅ Makes scripts executable
8. ✅ Updates `odoo.conf` with current user

**Usage**:
```bash
chmod +x setup-odoo-linux.sh
./setup-odoo-linux.sh
```

**Prerequisites**:
- Ubuntu 20.04+ or Debian 10+
- Internet connection
- sudo privileges

**Time**: ~10-20 minutes

---

### `setup-odoo-windows.ps1` (Windows)

**Purpose**: First-time setup on Windows

**What It Does**:
1. ✅ Checks Administrator privileges
2. ✅ Installs Chocolatey package manager
3. ✅ Installs Python 3.12, PostgreSQL 14, Git, Node.js, wkhtmltopdf
4. ✅ Starts PostgreSQL service
5. ✅ Creates database user and database
6. ✅ Creates Python virtual environment
7. ✅ Installs Python dependencies
8. ✅ Updates `odoo.conf` with Windows paths

**Usage**:
```powershell
# Run PowerShell as Administrator
.\setup-odoo-windows.ps1
```

**Prerequisites**:
- Windows 10/11
- Internet connection
- Administrator privileges

**Time**: ~20-40 minutes

---

## Common Use Cases

### Daily Development Workflow
```bash
# Morning: Start Odoo in dev mode
./start-odoo.sh --dev

# Work on code (auto-reloads on file changes)

# Evening: Stop Odoo
./stop-odoo.sh
```

### Installing a New Module
```bash
# Stop Odoo
./stop-odoo.sh

# Update all modules
./start-odoo.sh --update-all

# Or manually install via web interface
./start-odoo.sh
# Then go to http://localhost:8069/web#action=base.open_module_tree
```

### Debugging Issues
```bash
# Start with debug logging
./start-odoo.sh --debug

# Check logs in terminal
# Or check log file if configured in odoo.conf
```

### Database Operations
```bash
# Open Odoo shell
./start-odoo.sh --shell

# Then in Python shell:
>>> self.env['res.partner'].search([])
>>> exit()
```

---

## Troubleshooting

### Script Won't Execute
```bash
# Make script executable
chmod +x start-odoo.sh stop-odoo.sh
```

### "Virtual environment not found"
```bash
# Run setup script first
./setup-odoo-mac.sh  # or setup-odoo-linux.sh
```

### "Port 8069 already in use"
```bash
# Stop existing Odoo
./stop-odoo.sh --force

# Or change port in odoo.conf
# http_port = 8070
```

### "Cannot connect to database"
```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL (macOS)
brew services start postgresql@14

# Start PostgreSQL (Linux)
sudo systemctl start postgresql
```

### Process Won't Stop
```bash
# Force stop
./stop-odoo.sh --force

# Or manually kill
ps aux | grep odoo-bin
kill -9 <PID>
rm .odoo.pid
```

---

**Last Updated**: 2025-11-19  
**Odoo Version**: 19.0  
**Platforms**: macOS, Linux, Windows

