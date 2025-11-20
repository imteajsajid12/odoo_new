# Odoo 19.0 - Project Overview

## 📋 Table of Contents

- [Introduction](#introduction)
- [System Requirements](#system-requirements)
- [Project Structure](#project-structure)
- [Core Features](#core-features)
- [Technology Stack](#technology-stack)
- [Setup Status](#setup-status)
- [Getting Started](#getting-started)
- [Development Guide](#development-guide)
- [Resources](#resources)

---

## 🎯 Introduction

**Odoo** is a comprehensive open-source Enterprise Resource Planning (ERP) and Customer Relationship Management (CRM) system. It provides a complete suite of business applications that can work standalone or integrate seamlessly.

- **Version:** 19.0 (Final Release)
- **License:** LGPL-3
- **Author:** OpenERP S.A.
- **Website:** https://www.odoo.com
- **Repository:** https://github.com/odoo/odoo

### Key Characteristics

- **Modular Architecture:** 598+ modules available
- **Web-Based:** Modern responsive UI accessible from any browser
- **Multi-Company:** Support for multiple companies in one instance
- **Multi-Language:** Internationalization support for global deployment
- **Extensible:** Easy to customize and extend with custom modules

---

## 💻 System Requirements

### Required Components

| Component      | Minimum Version | Recommended | Current Status |
| -------------- | --------------- | ----------- | -------------- |
| **Python**     | 3.10            | 3.12        | ✅ 3.12.12     |
| **PostgreSQL** | 13.0            | 14.0+       | ✅ 14.19       |
| **Node.js**    | Any             | Latest LTS  | ✅ 24.10.0     |
| **npm**        | Any             | Latest      | ✅ 11.6.0      |

### Optional Components

| Component       | Version | Purpose                             | Status                   |
| --------------- | ------- | ----------------------------------- | ------------------------ |
| **wkhtmltopdf** | 0.12.6  | PDF generation with headers/footers | ⚠️ Manual install needed |
| **rtlcss**      | Latest  | Right-to-left language support      | ✅ Installed             |

### Python Version Support

- **Minimum:** Python 3.10
- **Maximum:** Python 3.13
- **Recommended:** Python 3.12

---

## 📁 Project Structure

```
odoo/
├── addons/                 # Community Edition modules (598 modules)
│   ├── account/           # Accounting & Finance
│   ├── crm/              # Customer Relationship Management
│   ├── sale/             # Sales Management
│   ├── purchase/         # Purchase Management
│   ├── stock/            # Inventory & Warehouse
│   ├── mrp/              # Manufacturing
│   ├── hr/               # Human Resources
│   ├── project/          # Project Management
│   ├── website/          # Website Builder
│   ├── point_of_sale/    # POS System
│   └── ...               # 588+ more modules
│
├── odoo/                  # Core framework
│   ├── addons/           # Base addons
│   ├── api/              # API layer
│   ├── cli/              # Command-line interface
│   ├── fields/           # Field types
│   ├── models/           # ORM models
│   ├── modules/          # Module management
│   ├── service/          # Services (HTTP, cron, etc.)
│   ├── tools/            # Utility functions
│   └── tests/            # Testing framework
│
├── odoo-bin              # Main executable
├── requirements.txt      # Python dependencies
├── setup.py              # Installation script
└── doc/                  # Documentation
```

---

## 🚀 Core Features

### Business Applications

#### 1. **Sales & CRM**

- Lead and opportunity management
- Sales pipeline visualization
- Quotation and order management
- Customer portal

#### 2. **Accounting & Finance**

- Multi-currency support
- Invoicing and billing
- Bank reconciliation
- Financial reporting
- Tax management

#### 3. **Inventory & Warehouse**

- Stock management
- Multi-warehouse support
- Barcode scanning
- Lot and serial number tracking
- Automated replenishment

#### 4. **Manufacturing (MRP)**

- Bill of Materials (BoM)
- Work orders and routing
- Quality control
- Maintenance management

#### 5. **Human Resources**

- Employee management
- Recruitment
- Time tracking
- Expense management
- Payroll integration

#### 6. **Project Management**

- Task management
- Kanban, Gantt, and Calendar views
- Time tracking
- Resource planning

#### 7. **E-Commerce & Website**

- Drag-and-drop website builder
- Online store
- Blog and forum
- SEO tools
- Live chat

#### 8. **Point of Sale**

- Offline-capable POS
- Multiple payment methods
- Receipt printing
- Inventory integration

---

## 🛠️ Technology Stack

### Backend

- **Language:** Python 3.10+
- **Framework:** Custom Odoo framework with ORM
- **Database:** PostgreSQL 13+
- **Web Server:** Werkzeug (WSGI)
- **API:** XML-RPC, JSON-RPC, REST

### Frontend

- **Framework:** Owl (Odoo Web Library) - Custom reactive framework
- **UI:** Bootstrap-based responsive design
- **JavaScript:** ES6+ modules
- **CSS:** SCSS/SASS with libsass
- **Templating:** QWeb (XML-based)

### Key Python Libraries

- **psycopg2:** PostgreSQL adapter
- **lxml:** XML processing
- **Pillow:** Image processing
- **reportlab:** PDF generation
- **Werkzeug:** WSGI utilities
- **Babel:** Internationalization
- **Jinja2:** Template engine
- **gevent:** Asynchronous networking

---

## ✅ Setup Status

### Current Installation

**Environment:** macOS (Apple Silicon/ARM64)
**Installation Date:** 2025-11-18
**Installation Type:** Source Installation with Virtual Environment

#### Completed Steps

- ✅ Python 3.12.12 installed via Homebrew
- ✅ Virtual environment created (`odoo-venv/`)
- ✅ All 65+ Python dependencies installed
- ✅ PostgreSQL 14.19 configured
- ✅ Database user configured with superuser privileges
- ✅ Odoo server successfully started
- ✅ Test database initialized (`odoo_test_db`)
- ✅ 14 core modules loaded

#### Pending (Optional)

- ⚠️ wkhtmltopdf 0.12.6 - Downloaded, requires manual installation

---

## 🚀 Getting Started

### Starting Odoo Server

```bash
# Navigate to project directory
cd /Users/luminous_imteaj/Documents/officeWork/Odoo/odoo

# Start Odoo with virtual environment
./odoo-venv/bin/python3 odoo-bin --addons-path=addons -d odoo_test_db

# Or with custom options
./odoo-venv/bin/python3 odoo-bin \
  --addons-path=addons \
  -d your_database_name \
  --http-port=8069 \
  --db-filter=your_database_name
```

### Accessing Odoo

1. **URL:** http://localhost:8069
2. **Default Credentials:**
   - Email: `admin`
   - Password: `admin`

### Common Commands

```bash
# Activate virtual environment
source odoo-venv/bin/activate

# Install a module
./odoo-venv/bin/python3 odoo-bin -d mydb -i module_name

# Update a module
./odoo-venv/bin/python3 odoo-bin -d mydb -u module_name

# Update all modules
./odoo-venv/bin/python3 odoo-bin -d mydb -u all

# Run tests
./odoo-venv/bin/python3 odoo-bin -d mydb --test-enable --stop-after-init

# Create a new database
./odoo-venv/bin/python3 odoo-bin -d newdb --init=base --stop-after-init
```

---

## 👨‍💻 Development Guide

### Creating a Custom Module

1. **Create module directory:**

```bash
mkdir -p custom_addons/my_module
cd custom_addons/my_module
```

2. **Create `__manifest__.py`:**

```python
{
    'name': 'My Module',
    'version': '19.0.1.0.0',
    'category': 'Custom',
    'summary': 'Module description',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

3. **Create `__init__.py`:**

```python
from . import models
```

4. **Start Odoo with custom addons:**

```bash
./odoo-venv/bin/python3 odoo-bin \
  --addons-path=addons,custom_addons \
  -d mydb
```

### Module Structure

```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── data.xml
├── static/
│   ├── src/
│   │   ├── js/
│   │   ├── css/
│   │   └── xml/
│   └── description/
│       └── icon.png
└── tests/
    ├── __init__.py
    └── test_my_module.py
```

### Best Practices

1. **Follow Odoo Guidelines:**

   - Use proper naming conventions
   - Follow Python PEP 8 style guide
   - Add proper documentation

2. **Version Control:**

   - Keep custom modules in separate repository
   - Use `.gitignore` for generated files

3. **Testing:**

   - Write unit tests for models
   - Test UI with tours
   - Use `--test-enable` flag

4. **Security:**
   - Define proper access rights
   - Use record rules for row-level security
   - Validate user inputs

---

## 📚 Resources

### Official Documentation

- **Main Documentation:** https://www.odoo.com/documentation/19.0/
- **Developer Documentation:** https://www.odoo.com/documentation/19.0/developer.html
- **API Reference:** https://www.odoo.com/documentation/19.0/developer/reference.html

### Learning Resources

- **Odoo eLearning:** https://www.odoo.com/slides
- **Odoo Tutorials:** https://www.odoo.com/documentation/19.0/developer/tutorials.html
- **Community Forum:** https://www.odoo.com/forum

### Source Code

- **GitHub Repository:** https://github.com/odoo/odoo
- **Branch:** 19.0
- **Contributing Guide:** See CONTRIBUTING.md

### Community

- **Odoo Community Association (OCA):** https://odoo-community.org/
- **OCA GitHub:** https://github.com/OCA

---

## 🔧 Troubleshooting

### Common Issues

**1. Server won't start**

```bash
# Check if port is already in use
lsof -i :8069

# Check PostgreSQL is running
psql -l
```

**2. Module not found**

```bash
# Verify addons path
./odoo-venv/bin/python3 odoo-bin --addons-path=addons,custom_addons

# Update module list in database
# Settings > Apps > Update Apps List
```

**3. Database connection errors**

```bash
# Check PostgreSQL service
brew services list | grep postgresql

# Test connection
psql -U luminous_imteaj -d postgres
```

**4. Permission errors**

```bash
# Ensure proper file permissions
chmod +x odoo-bin

# Check virtual environment
source odoo-venv/bin/activate
which python3
```

---

## 📊 Project Statistics

- **Total Modules:** 598+
- **Core Framework Files:** 1000+
- **Programming Languages:** Python, JavaScript, XML, CSS
- **Lines of Code:** 1M+ (estimated)
- **Active Development:** Yes
- **Release Cycle:** Annual major releases

---

## 📝 License

Odoo is licensed under **LGPL-3** (GNU Lesser General Public License v3).

See the [LICENSE](LICENSE) file for full details.

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Contribution Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

---

## 📞 Support

- **Enterprise Support:** Available for Odoo Enterprise customers
- **Community Support:** Forum and mailing lists
- **Professional Services:** Available through Odoo partners

---

**Last Updated:** 2025-11-18
**Odoo Version:** 19.0
**Setup Status:** ✅ Complete and Running
