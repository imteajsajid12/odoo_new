# Odoo 19.0 Configuration Guide

## 📋 Table of Contents
- [Configuration File Overview](#configuration-file-overview)
- [Configuration Options](#configuration-options)
- [Platform-Specific Paths](#platform-specific-paths)
- [Environment Variables](#environment-variables)
- [Advanced Configuration](#advanced-configuration)

---

## Configuration File Overview

The `odoo.conf` file contains all configuration settings for running Odoo. This file is loaded automatically by the start scripts.

### Configuration File Location
```
/Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/odoo.conf
```

### Configuration Hierarchy
Odoo loads configuration in the following order (later sources override earlier ones):
1. **Default values** (hardcoded in Odoo)
2. **Configuration file** (`odoo.conf`)
3. **Environment variables** (prefixed with `ODOO_`)
4. **Command-line arguments** (highest priority)

---

## Configuration Options

### 🔐 Admin Password
```ini
admin_passwd = admin
```
- **Purpose**: Master password for database operations
- **Security**: ⚠️ **CHANGE THIS IN PRODUCTION!**
- **Usage**: Required for creating/dropping databases, installing modules

### 🗄️ Database Configuration
```ini
db_host = localhost
db_port = 5432
db_user = luminous_imteaj
db_password = 
db_name = odoo_test_db
```
- **db_host**: PostgreSQL server hostname (default: localhost)
- **db_port**: PostgreSQL port (default: 5432)
- **db_user**: PostgreSQL username (current macOS user)
- **db_password**: PostgreSQL password (empty = no password)
- **db_name**: Default database name

### 🌐 HTTP Server Configuration
```ini
http_interface = 0.0.0.0
http_port = 8069
```
- **http_interface**: Network interface to bind to
  - `0.0.0.0` = all interfaces (accessible from network)
  - `127.0.0.1` = localhost only (more secure)
- **http_port**: Port number (default: 8069)
- **Access URL**: http://localhost:8069

### 📁 Paths Configuration
```ini
addons_path = /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/addons
data_dir = /Users/luminous_imteaj/Library/Application Support/Odoo/addons/19.0
```
- **addons_path**: Comma-separated list of addon directories
- **data_dir**: Directory for filestore, sessions, and generated assets

### 🔧 Performance Configuration
```ini
workers = 0
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 60
limit_time_real = 120
```
- **workers**: Number of worker processes
  - `0` = single-process mode (development)
  - `>0` = multi-process mode (production)
- **max_cron_threads**: Number of cron worker threads
- **limit_memory_hard**: Hard memory limit per worker (2.5 GB)
- **limit_memory_soft**: Soft memory limit per worker (2 GB)
- **limit_request**: Max requests per worker before restart
- **limit_time_cpu**: CPU time limit per request (seconds)
- **limit_time_real**: Real time limit per request (seconds)

### 📝 Logging Configuration
```ini
log_level = info
logfile = 
log_handler = :INFO
```
- **log_level**: Logging verbosity
  - `debug` = very verbose (development)
  - `info` = normal (default)
  - `warn` = warnings only
  - `error` = errors only
- **logfile**: Log file path (empty = stdout)
- **log_handler**: Fine-grained logging control

### 🔒 Security Configuration
```ini
list_db = True
dbfilter = 
proxy_mode = False
```
- **list_db**: Show database selector (False in production)
- **dbfilter**: Regex to filter database names
- **proxy_mode**: Enable when behind reverse proxy

---

## Platform-Specific Paths

### macOS (Current Platform)
```ini
data_dir = /Users/luminous_imteaj/Library/Application Support/Odoo/addons/19.0
addons_path = /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo/addons
```

### Linux
```ini
data_dir = /home/username/.local/share/Odoo/addons/19.0
addons_path = /home/username/odoo/addons
```

### Windows
```ini
data_dir = C:\Users\username\AppData\Local\Odoo\addons\19.0
addons_path = C:\Users\username\odoo\addons
```

---

## Environment Variables

You can override configuration using environment variables:
```bash
export ODOO_HTTP_PORT=8080
export ODOO_DB_NAME=production_db
export ODOO_LOG_LEVEL=debug
./start-odoo.sh
```

---

## Advanced Configuration

### Multi-Database Setup
```ini
dbfilter = ^%d$
```
This filters databases by subdomain (e.g., `company1.example.com` → `company1` database)

### Production Settings
```ini
workers = 4
max_cron_threads = 2
http_interface = 127.0.0.1
list_db = False
proxy_mode = True
log_level = warn
```

### Development Settings
```ini
workers = 0
log_level = debug
dev_mode = reload,qweb,werkzeug,xml
```

---

## 🔍 Troubleshooting

### Configuration Not Loading
- Verify file path: `./odoo-bin --config=odoo.conf --stop-after-init`
- Check file permissions: `ls -l odoo.conf`

### Database Connection Errors
- Verify PostgreSQL is running: `pg_isready`
- Check credentials: `psql -U luminous_imteaj -d odoo_test_db`

### Port Already in Use
- Change port in config: `http_port = 8070`
- Or kill existing process: `./stop-odoo.sh`

---

**Last Updated**: 2025-11-19  
**Odoo Version**: 19.0  
**Platform**: macOS (Darwin)

