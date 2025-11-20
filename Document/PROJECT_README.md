# Odoo 19.0 ERP System - Complete Project Guide

## 🚀 Quick Start

### First Time Setup
```bash
# macOS
./setup-odoo-mac.sh

# Linux
./setup-odoo-linux.sh

# Windows (PowerShell as Administrator)
.\setup-odoo-windows.ps1
```

### Start Odoo
```bash
./start-odoo.sh  # macOS/Linux
.\start-odoo.ps1  # Windows
```

### Access Application
Open your browser to: **http://localhost:8069**

---

## 📚 Documentation

### Essential Guides
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup instructions for all platforms
- **[SCRIPTS_DOCUMENTATION.md](SCRIPTS_DOCUMENTATION.md)** - How to use start/stop scripts
- **[CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md)** - Configuration file reference

### Previous Documentation
- **[RUN_GUIDE.md](RUN_GUIDE.md)** - Original running guide
- **[ANALYSIS_SUMMARY.md](ANALYSIS_SUMMARY.md)** - Project architecture analysis
- **[CSS_FIX_SUMMARY.md](CSS_FIX_SUMMARY.md)** - CSS compilation fixes
- **[MODULE_INSTALLATION_FIX.md](MODULE_INSTALLATION_FIX.md)** - Module installation fixes

---

## 🛠️ Available Scripts

### Start Scripts
| Script | Platform | Purpose |
|--------|----------|---------|
| `start-odoo.sh` | macOS/Linux | Start Odoo server |
| `start-odoo.ps1` | Windows | Start Odoo server |

**Usage Examples**:
```bash
./start-odoo.sh           # Normal mode
./start-odoo.sh --dev     # Development mode (auto-reload)
./start-odoo.sh --debug   # Debug logging
./start-odoo.sh --shell   # Python shell
```

### Stop Scripts
| Script | Platform | Purpose |
|--------|----------|---------|
| `stop-odoo.sh` | macOS/Linux | Stop Odoo server |
| `stop-odoo.ps1` | Windows | Stop Odoo server |

**Usage Examples**:
```bash
./stop-odoo.sh           # Graceful stop
./stop-odoo.sh --force   # Force stop
```

### Setup Scripts
| Script | Platform | Purpose |
|--------|----------|---------|
| `setup-odoo-mac.sh` | macOS | First-time setup |
| `setup-odoo-linux.sh` | Ubuntu/Debian | First-time setup |
| `setup-odoo-windows.ps1` | Windows | First-time setup |

---

## ⚙️ Configuration

### Configuration File: `odoo.conf`

**Key Settings**:
```ini
# Database
db_host = localhost
db_port = 5432
db_user = luminous_imteaj
db_name = odoo_test_db

# HTTP Server
http_interface = 0.0.0.0
http_port = 8069

# Paths
addons_path = /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/addons
data_dir = /Users/luminous_imteaj/Library/Application Support/Odoo/addons/19.0

# Performance
workers = 0
log_level = info
```

**See [CONFIGURATION_GUIDE.md](CONFIGURATION_GUIDE.md) for complete reference**

---

## 📁 Project Structure

```
odoo/
├── odoo-bin                    # Main Odoo executable
├── odoo.conf                   # Configuration file
├── requirements.txt            # Python dependencies
├── odoo-venv/                  # Python virtual environment
├── addons/                     # Odoo modules (598+ modules)
│   ├── base/                   # Core module
│   ├── web/                    # Web interface
│   ├── hr/                     # Human Resources
│   └── ...                     # Other modules
├── odoo/                       # Odoo core framework
│   ├── addons/                 # Core addons
│   ├── tools/                  # Utility functions
│   └── ...
├── start-odoo.sh               # Start script (Unix)
├── stop-odoo.sh                # Stop script (Unix)
├── start-odoo.ps1              # Start script (Windows)
├── stop-odoo.ps1               # Stop script (Windows)
├── setup-odoo-mac.sh           # Setup script (macOS)
├── setup-odoo-linux.sh         # Setup script (Linux)
├── setup-odoo-windows.ps1      # Setup script (Windows)
└── .odoo.pid                   # Process ID file (created at runtime)
```

---

## 🔧 System Requirements

### macOS
- macOS 10.15 (Catalina) or later
- 4 GB RAM minimum (8 GB recommended)
- 5 GB free disk space
- Internet connection

### Linux (Ubuntu/Debian)
- Ubuntu 20.04+ or Debian 10+
- 4 GB RAM minimum (8 GB recommended)
- 3 GB free disk space
- sudo privileges

### Windows
- Windows 10/11
- 4 GB RAM minimum (8 GB recommended)
- 5 GB free disk space
- Administrator privileges

---

## 🗄️ Database Information

- **Database Server**: PostgreSQL 14.19
- **Database Name**: `odoo_test_db`
- **Database User**: `luminous_imteaj` (current system user)
- **Database Password**: None (local trust authentication)
- **Connection**: localhost:5432

---

## 🌐 Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| **Web Interface** | http://localhost:8069 | admin / admin |
| **Database Manager** | http://localhost:8069/web/database/manager | Master password: admin |
| **Apps** | http://localhost:8069/web#action=base.open_module_tree | - |

---

## 🎯 Common Tasks

### Install a Module
1. Start Odoo: `./start-odoo.sh`
2. Open browser: http://localhost:8069
3. Login with admin/admin
4. Go to **Apps** menu
5. Search for module
6. Click **Install**

### Update Modules
```bash
./stop-odoo.sh
./start-odoo.sh --update-all
```

### Access Python Shell
```bash
./start-odoo.sh --shell
```

### View Logs
```bash
# If running in foreground
# Logs appear in terminal

# If running in background
tail -f odoo.log  # if logfile configured
```

### Change Port
Edit `odoo.conf`:
```ini
http_port = 8070
```

---

## 🐛 Troubleshooting

### Odoo Won't Start
```bash
# Check if already running
ps aux | grep odoo-bin

# Stop existing process
./stop-odoo.sh --force

# Check configuration
./odoo-venv/bin/python3 odoo-bin --config=odoo.conf --stop-after-init
```

### Database Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql@14  # macOS
sudo systemctl start postgresql     # Linux
Start-Service postgresql-x64-14     # Windows
```

### Port Already in Use
```bash
# Find process using port 8069
lsof -i :8069  # macOS/Linux
netstat -ano | findstr :8069  # Windows

# Kill process or change port in odoo.conf
```

### CSS Not Loading
```bash
# Clear asset cache
rm -rf ~/.local/share/Odoo/filestore/odoo_test_db/assets/*

# Restart Odoo
./stop-odoo.sh && ./start-odoo.sh
```

---

## 📊 Project Status

### ✅ Completed
- [x] Project analysis and architecture documentation
- [x] Python 3.12 virtual environment setup
- [x] PostgreSQL database configuration
- [x] CSS/SCSS compilation fixes
- [x] Module installation system fixes
- [x] Configuration file (`odoo.conf`) creation
- [x] Start/stop scripts for all platforms
- [x] Setup scripts for macOS/Linux/Windows
- [x] Comprehensive documentation

### 🎉 Current Status
- **Server**: Running on http://localhost:8069
- **Database**: Connected and operational
- **Modules**: 75 modules installed
- **CSS**: Rendering correctly (791 KB bundle)
- **Module Installation**: Working correctly

---

## 📞 Support

### Documentation
- [Odoo Official Documentation](https://www.odoo.com/documentation/19.0/)
- [Odoo Developer Documentation](https://www.odoo.com/documentation/19.0/developer.html)

### Common Issues
See [SETUP_GUIDE.md](SETUP_GUIDE.md#troubleshooting) for detailed troubleshooting

---

**Project**: Odoo 19.0 ERP System  
**Version**: 19.0  
**Last Updated**: 2025-11-19  
**Platform**: macOS (Darwin) - Cross-platform compatible

