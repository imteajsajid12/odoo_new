# Odoo 19.0 Setup Scripts

Complete setup scripts for installing Odoo 19.0 with all required dependencies on Linux, macOS, and Windows.

## 📋 What's Included

All setup scripts now include **complete dependencies** for:
- ✅ Python 3.12 environment
- ✅ PostgreSQL database
- ✅ PDF generation (wkhtmltopdf)
- ✅ Barcode rendering (Cairo, pycairo, rlPyCairo)
- ✅ Graphics libraries (freetype, pixman, fontconfig)
- ✅ Build tools and compilers
- ✅ Node.js and npm

## 🚀 Quick Start

### macOS
```bash
chmod +x setup-odoo-mac.sh
./setup-odoo-mac.sh
```

### Linux (Ubuntu/Debian)
```bash
chmod +x setup-odoo-linux.sh
./setup-odoo-linux.sh
```

### Windows
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup-odoo-windows.ps1
```

## 📦 Dependencies Installed

### System Dependencies

#### macOS (via Homebrew)
- Python 3.12
- PostgreSQL 14
- wkhtmltopdf
- cairo, pkg-config, pixman, freetype, fontconfig
- Node.js, npm, libsass

#### Linux (via apt-get)
- Python 3.12 + development tools
- PostgreSQL + contrib
- wkhtmltopdf
- libcairo2-dev, pkg-config, libpixman-1-dev
- libfreetype6-dev, fontconfig
- Build essentials (gcc, make, etc.)
- XML/XSLT libraries
- Image libraries (libjpeg, libpng)
- Node.js, npm

#### Windows (via Chocolatey)
- Python 3.12
- PostgreSQL 14
- wkhtmltopdf
- GTK+ runtime (includes Cairo)
- Git
- Node.js

### Python Packages

All platforms install:
- All packages from `requirements.txt`
- **pycairo** - Python bindings for Cairo
- **rlPyCairo** - ReportLab's Cairo integration
- **freetype-py** - Font rendering library

## 🎯 What Gets Fixed

These enhanced scripts solve the following issues:

1. **PDF Generation** - wkhtmltopdf installed and configured
2. **Barcode Rendering** - Cairo libraries for QR codes and barcodes
3. **Graphics Rendering** - Complete graphics stack for ReportLab
4. **Font Rendering** - FreeType for proper font display
5. **Build Tools** - All compilers needed for Python packages

## 📖 Platform-Specific Notes

### macOS

**Requirements:**
- macOS 10.15 (Catalina) or later
- Homebrew will be installed automatically if not present

**Post-Installation:**
- PostgreSQL runs as a Homebrew service
- Python 3.12 is installed via Homebrew
- All paths are automatically configured

### Linux (Ubuntu/Debian)

**Requirements:**
- Ubuntu 20.04+ or Debian 11+
- sudo privileges
- Internet connection

**Post-Installation:**
- PostgreSQL runs as a systemd service
- Database user matches your system username
- Configuration file is updated automatically

### Windows

**Requirements:**
- Windows 10 (build 19041+) or Windows 11
- Administrator privileges
- Internet connection

**Post-Installation:**
- PostgreSQL runs as a Windows service
- Default password: `odoo123` (change in production!)
- GTK+ runtime provides Cairo support
- May need to restart terminal for PATH changes

**Known Issues:**
- pycairo installation may fail if GTK+ runtime isn't installed
- Some packages require Visual C++ Build Tools
- wkhtmltopdf from Chocolatey may be outdated

## 🔧 Troubleshooting

### Common Issues

#### "wkhtmltopdf not found"
**Solution:**
- macOS: `brew install wkhtmltopdf`
- Linux: `sudo apt-get install wkhtmltopdf`
- Windows: Download from https://wkhtmltopdf.org/downloads.html

#### "ModuleNotFoundError: No module named 'cairo'"
**Solution:**
```bash
# macOS
brew install cairo pkg-config
pip install pycairo

# Linux
sudo apt-get install libcairo2-dev pkg-config
pip install pycairo

# Windows
choco install gtk-runtime
pip install pycairo
```

#### "Unable to find Wkhtmltopdf on this system"
**Solution:**
1. Verify installation: `which wkhtmltopdf` (Unix) or `where wkhtmltopdf` (Windows)
2. Add to PATH if needed
3. Restart Odoo server

#### "Barcode rendering failed"
**Solution:**
```bash
# Install barcode dependencies
pip install pycairo rlPyCairo freetype-py

# Verify Cairo is available
python -c "import cairo; print(cairo.version)"
```

#### PostgreSQL Connection Failed
**Solution:**
- Check service is running
- Verify credentials in `odoo.conf`
- Check PostgreSQL logs

### Verification Commands

Test your installation:

```bash
# Activate virtual environment
source odoo-venv/bin/activate  # Unix
.\odoo-venv\Scripts\Activate.ps1  # Windows

# Test Python packages
python -c "import cairo; print('Cairo OK')"
python -c "import rlPyCairo; print('rlPyCairo OK')"
python -c "from reportlab.graphics import renderPM; print('ReportLab OK')"

# Test wkhtmltopdf
wkhtmltopdf --version

# Test PostgreSQL
psql -U odoo -d odoo_test_db -c "SELECT version();"
```

## 🎓 What Each Script Does

### Step-by-Step Process

1. **System Check** - Verifies OS version and requirements
2. **Package Manager** - Installs Homebrew/Chocolatey if needed
3. **System Dependencies** - Installs all system packages
4. **PDF Tools** - Installs wkhtmltopdf and Cairo
5. **Database Setup** - Installs and configures PostgreSQL
6. **Python Environment** - Creates virtual environment
7. **Python Packages** - Installs all Python dependencies
8. **Barcode Support** - Installs pycairo and related packages
9. **Configuration** - Updates odoo.conf for your system
10. **Verification** - Provides next steps and configuration info

## 📝 Configuration

After running the setup script, you'll have:

- **Database Name:** `odoo_test_db`
- **Database User:** Your system username (or `odoo` on Windows)
- **HTTP Port:** 8069
- **Config File:** `odoo.conf`

### Important Security Notes

🔒 **For Production Use:**
1. Change admin password in `odoo.conf`
2. Change PostgreSQL password
3. Use SSL/TLS for database connections
4. Configure firewall rules
5. Use a reverse proxy (nginx/Apache)
6. Enable security features in `odoo.conf`

## 🚦 Starting Odoo

After setup completes:

```bash
# macOS/Linux
./start-odoo.sh

# Windows
.\start-odoo.ps1

# Or manually
source odoo-venv/bin/activate  # Unix
python odoo-bin -c odoo.conf
```

Access Odoo at: **http://localhost:8069**

## 📚 Additional Resources

- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [wkhtmltopdf Downloads](https://wkhtmltopdf.org/downloads.html)
- [Cairo Graphics](https://www.cairographics.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🐛 Reporting Issues

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Check Odoo logs: `odoo.log`
4. Check PostgreSQL logs
5. Ensure virtual environment is activated

## 📄 License

These setup scripts are provided as-is for setting up Odoo development environments.

## ✨ Recent Updates

**November 25, 2025:**
- ✅ Added Cairo graphics library support
- ✅ Added pycairo for barcode rendering
- ✅ Added rlPyCairo for ReportLab integration
- ✅ Added freetype-py for font rendering
- ✅ Enhanced error handling and verification
- ✅ Updated all three platform scripts
- ✅ Added comprehensive troubleshooting guide

These updates ensure complete PDF generation and barcode rendering functionality out of the box!
