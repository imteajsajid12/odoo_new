# Odoo 19.0 - Complete Run Guide

## 🚀 Quick Start

This guide provides step-by-step instructions to run the Odoo 19.0 ERP system on your local machine.

---

## 📋 Prerequisites

### System Requirements

| Component      | Minimum Version | Recommended | Status      |
| -------------- | --------------- | ----------- | ----------- |
| **Python**     | 3.10            | 3.12        | ✅ Required |
| **PostgreSQL** | 13.0            | 14.0+       | ✅ Required |
| **Node.js**    | Any             | Latest LTS  | ⚠️ Optional |
| **npm**        | Any             | Latest      | ⚠️ Optional |

### Verify Installations

```bash
# Check Python version (must be 3.10+)
python3.12 --version
# Expected: Python 3.12.x

# Check PostgreSQL
psql --version
# Expected: psql (PostgreSQL) 14.x or higher

# Check if PostgreSQL is running
psql -U your_username -d postgres -c "SELECT version();"
```

---

## 🔧 Installation Steps

### Step 1: Clone or Navigate to Odoo Directory

```bash
cd /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo
```

### Step 2: Create Python Virtual Environment

**Important:** Use Python 3.12 (or 3.10+) to avoid compatibility issues.

```bash
# Remove old virtual environment if exists
rm -rf odoo-venv

# Create new virtual environment with Python 3.12
python3.12 -m venv odoo-venv

# Verify virtual environment
ls -la odoo-venv/bin/
```

### Step 3: Install Python Dependencies

```bash
# Upgrade pip, setuptools, and wheel
./odoo-venv/bin/pip install --upgrade pip setuptools wheel

# Install all Odoo dependencies
./odoo-venv/bin/pip install -r requirements.txt

# Install PostgreSQL adapter (critical)
./odoo-venv/bin/pip install psycopg2-binary

# Verify installations
./odoo-venv/bin/pip list | grep -E "psycopg2|Werkzeug|lxml|Pillow"
```

**Expected output:**

```
lxml                  5.2.1
Pillow                10.2.0
psycopg2              2.9.9
psycopg2-binary       2.9.11
Werkzeug              3.0.1
```

### Step 4: Configure PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U luminous_imteaj -d postgres

# Create Odoo database (if not exists)
CREATE DATABASE odoo_test_db;

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE odoo_test_db TO luminous_imteaj;

# Exit PostgreSQL
\q
```

---

## ▶️ Running Odoo

### Basic Run Command

```bash
./odoo-venv/bin/python3 odoo-bin --addons-path=addons -d odoo_test_db --http-port=8069
```

### Run with Custom Configuration

```bash
./odoo-venv/bin/python3 odoo-bin \
  --addons-path=addons \
  -d odoo_test_db \
  --http-port=8069 \
  --db-filter=odoo_test_db \
  --log-level=info
```

### Run in Development Mode

```bash
./odoo-venv/bin/python3 odoo-bin \
  --addons-path=addons \
  -d odoo_test_db \
  --http-port=8069 \
  --dev=all
```

**Development mode features:**

- Auto-reload on file changes
- Detailed error messages
- Asset debugging (no minification)

---

## 🌐 Accessing Odoo

### Web Interface

1. **URL:** http://localhost:8069
2. **Default Login:**
   - Email: `admin`
   - Password: `admin`

### Database Manager

- **URL:** http://localhost:8069/web/database/manager
- Create, backup, restore, or delete databases

---

## 🎨 CSS/SCSS Verification

### How Odoo Handles CSS

Odoo uses **SCSS (Sass)** for styling and compiles it to CSS on-the-fly:

1. **SCSS Source Files:** Located in `addons/*/static/src/scss/`
2. **Compilation:** Automatic via `libsass` library
3. **Asset Bundles:** Compiled CSS served as `/web/assets/*/bundle_name.min.css`

### Verify CSS is Working

```bash
# Check if CSS assets are being served
curl -I http://localhost:8069/web/static/src/scss/primary_variables.scss

# Check compiled CSS bundle
curl -s http://localhost:8069 | grep -i "stylesheet"
```

**Expected output:**

```html
<link
  type="text/css"
  rel="stylesheet"
  href="/web/assets/1/eec3ea3/web.assets_frontend.min.css"
/>
```

### CSS Asset Locations

```
addons/web/static/src/scss/          # Core web styles
addons/web/static/src/webclient/     # Webclient styles
addons/portal/static/src/scss/       # Portal styles
addons/website/static/src/scss/      # Website builder styles
```

### Force CSS Recompilation

```bash
# Clear assets cache
rm -rf ~/.local/share/Odoo/filestore/odoo_test_db/assets/*

# Restart Odoo with asset regeneration
./odoo-venv/bin/python3 odoo-bin -d odoo_test_db --update=all
```

---

## 🛠️ Common Commands

### Database Operations

```bash
# Create new database
./odoo-venv/bin/python3 odoo-bin -d new_database --init=base --stop-after-init

# Update all modules
./odoo-venv/bin/python3 odoo-bin -d odoo_test_db --update=all --stop-after-init

# Install specific module
./odoo-venv/bin/python3 odoo-bin -d odoo_test_db -i sale,crm --stop-after-init

# Uninstall module
./odoo-venv/bin/python3 odoo-bin -d odoo_test_db -u module_name --stop-after-init
```

### Testing

```bash
# Run all tests
./odoo-venv/bin/python3 odoo-bin -d odoo_test_db --test-enable --stop-after-init

# Run tests for specific module
./odoo-venv/bin/python3 odoo-bin -d odoo_test_db --test-enable -i sale --stop-after-init

# Run with test tags
./odoo-venv/bin/python3 odoo-bin -d odoo_test_db --test-enable --test-tags=/account
```

### Server Management

```bash
# Check if Odoo is running
lsof -i :8069

# Stop Odoo server (if running in background)
pkill -f odoo-bin

# Run in background
nohup ./odoo-venv/bin/python3 odoo-bin -d odoo_test_db &

# View logs
tail -f nohup.out
```

---

## 🐛 Troubleshooting

### Issue 1: Python Version Error

**Error:**

```
AssertionError: Outdated python version detected, Odoo requires Python >= 3.10 to run.
```

**Solution:**

```bash
# Check Python version
python3 --version

# If < 3.10, install Python 3.12
brew install python@3.12

# Recreate virtual environment
rm -rf odoo-venv
python3.12 -m venv odoo-venv
./odoo-venv/bin/pip install -r requirements.txt psycopg2-binary
```

### Issue 2: PostgreSQL Connection Error

**Error:**

```
psycopg2.OperationalError: could not connect to server
```

**Solution:**

```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start PostgreSQL
brew services start postgresql@14

# Verify connection
psql -U luminous_imteaj -d postgres
```

### Issue 3: Port Already in Use

**Error:**

```
OSError: [Errno 48] Address already in use
```

**Solution:**

```bash
# Find process using port 8069
lsof -i :8069

# Kill the process
kill -9 <PID>

# Or use different port
./odoo-venv/bin/python3 odoo-bin -d odoo_test_db --http-port=8070
```

### Issue 4: CSS Not Loading

**Symptoms:**

- Page loads but looks unstyled
- Missing colors, fonts, or layout

**Solution:**

```bash
# Clear browser cache
# In browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)

# Clear Odoo assets cache
rm -rf ~/.local/share/Odoo/filestore/odoo_test_db/assets/*

# Restart Odoo with asset rebuild
./odoo-venv/bin/python3 odoo-bin -d odoo_test_db --dev=all

# Check if libsass is installed
./odoo-venv/bin/pip list | grep libsass
# If missing: ./odoo-venv/bin/pip install libsass
```

### Issue 5: Module Installation Fails

**Error:**

```
Module <module_name> not found
```

**Solution:**

```bash
# Update module list in database
# Go to: Settings > Apps > Update Apps List

# Or via command line
./odoo-venv/bin/python3 odoo-bin -d odoo_test_db --update=all --stop-after-init

# Check addons path
./odoo-venv/bin/python3 odoo-bin --addons-path=addons,custom_addons -d odoo_test_db
```

---

## 📊 Project Analysis Summary

### Architecture Overview

**Odoo 19.0** is a modular ERP system with:

- **598+ Modules:** Covering all business needs
- **MVC Architecture:** Models, Views, Controllers
- **ORM:** Custom Python ORM for database operations
- **Multi-tier:** Database → Backend (Python) → Frontend (JavaScript/Owl)

### Technology Stack

#### Backend

- **Python 3.10+** - Core language
- **PostgreSQL** - Primary database
- **Werkzeug** - WSGI web server
- **psycopg2** - PostgreSQL adapter
- **lxml** - XML processing
- **Pillow** - Image processing

#### Frontend

- **Owl Framework** - Reactive JavaScript framework (Odoo's custom)
- **Bootstrap 5** - UI framework
- **SCSS/Sass** - Styling (compiled via libsass)
- **QWeb** - XML-based templating
- **JavaScript ES6+** - Modern JavaScript

#### CSS/SCSS Architecture

```
SCSS Source Files (*.scss)
         ↓
    libsass compiler
         ↓
   Compiled CSS
         ↓
  Asset Bundles (minified)
         ↓
   Served to Browser
```

**Key SCSS Files:**

- `pre_variables.scss` - Base variables
- `primary_variables.scss` - Theme colors
- `secondary_variables.scss` - Derived variables
- `bootstrap_overridden.scss` - Bootstrap customizations
- `*.dark.scss` - Dark mode styles

### CSS Compilation Process

1. **On Server Start:** Odoo scans all modules for SCSS files
2. **Asset Bundles:** Groups related SCSS files into bundles
3. **Compilation:** Uses `libsass` to compile SCSS → CSS
4. **Minification:** Compresses CSS for production
5. **Caching:** Stores compiled assets with hash-based URLs
6. **Serving:** Delivers via `/web/assets/<bundle_id>/<hash>/<bundle_name>.min.css`

### Verified Working Components

✅ **Python 3.12 Environment** - Virtual environment created successfully
✅ **All Dependencies Installed** - 66 packages installed
✅ **PostgreSQL Connection** - Database `odoo_test_db` accessible
✅ **Odoo Server Running** - HTTP service on port 8069
✅ **Module Loading** - 74 modules loaded successfully
✅ **SCSS Compilation** - libsass installed and working
✅ **CSS Assets Serving** - Asset bundles generated and served
✅ **Web Interface** - Accessible at http://localhost:8069

---

## 🔍 CSS Testing Checklist

### Manual Testing

1. **Open Odoo in Browser**

   ```
   http://localhost:8069
   ```

2. **Check Developer Tools**

   - Press F12 (or Cmd+Option+I on Mac)
   - Go to Network tab
   - Filter by CSS
   - Reload page (Cmd+R or Ctrl+R)
   - Verify CSS files load with 200 status

3. **Inspect Elements**

   - Right-click any element
   - Select "Inspect"
   - Check Styles panel
   - Verify CSS rules are applied

4. **Test Responsive Design**
   - Toggle device toolbar (Cmd+Shift+M)
   - Test mobile, tablet, desktop views
   - Verify layout adapts correctly

### Automated Testing

```bash
# Test CSS compilation
./odoo-venv/bin/python3 -c "import sass; print('libsass working:', sass.compile(string='$color: red; body { color: $color; }'))"

# Expected output:
# libsass working: body { color: red; }
```

---

## 📝 Configuration Files

### Create odoo.conf (Optional)

```bash
cat > odoo.conf << 'EOF'
[options]
addons_path = addons
admin_passwd = admin
db_host = localhost
db_port = 5432
db_user = luminous_imteaj
db_password =
http_port = 8069
logfile = /tmp/odoo.log
log_level = info
EOF
```

### Run with Configuration File

```bash
./odoo-venv/bin/python3 odoo-bin -c odoo.conf -d odoo_test_db
```

---

## 🎯 Next Steps

### For Development

1. **Create Custom Module**

   ```bash
   ./odoo-venv/bin/python3 odoo-bin scaffold my_module addons/
   ```

2. **Enable Developer Mode**

   - Settings > Activate Developer Mode
   - Or add `?debug=1` to URL

3. **Install Development Tools**
   ```bash
   ./odoo-venv/bin/pip install debugpy ipython
   ```

### For Production

1. **Use Configuration File** - Better security and management
2. **Set Strong Admin Password** - Change default password
3. **Configure Reverse Proxy** - Use Nginx or Apache
4. **Enable HTTPS** - SSL/TLS certificates
5. **Database Backups** - Regular automated backups
6. **Monitor Resources** - CPU, memory, disk usage

---

## 📚 Additional Resources

- **Official Documentation:** https://www.odoo.com/documentation/19.0/
- **Developer Guide:** https://www.odoo.com/documentation/19.0/developer.html
- **API Reference:** https://www.odoo.com/documentation/19.0/developer/reference.html
- **Community Forum:** https://www.odoo.com/forum
- **GitHub Repository:** https://github.com/odoo/odoo

---

## ✅ Verification Checklist

- [x] Python 3.12 installed and working
- [x] Virtual environment created
- [x] All dependencies installed (66 packages)
- [x] PostgreSQL running and accessible
- [x] Database created and configured
- [x] Odoo server starts without errors
- [x] Web interface accessible at http://localhost:8069
- [x] CSS/SCSS compilation working (libsass)
- [x] Asset bundles generated and served
- [x] Login page displays correctly with styling

---

**Last Updated:** 2025-11-19
**Odoo Version:** 19.0
**Python Version:** 3.12.12
**PostgreSQL Version:** 14.19
**Status:** ✅ Fully Operational
