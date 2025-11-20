#!/usr/bin/env python3
"""
Odoo System Verification Script
Verifies that the Odoo system is running correctly with the new database
"""

import sys
import os

# Add Odoo to path
sys.path.insert(0, '/Users/luminous_imteaj/Documents/officeWork/Odoo/odoo')

try:
    from odoo.modules.registry import Registry
    from odoo.api import Environment
    
    print("=" * 80)
    print("ODOO SYSTEM VERIFICATION")
    print("=" * 80)
    print()
    
    # Connect to database
    db_name = 'odoo_v1'
    print(f"Connecting to database: {db_name}")
    
    try:
        registry = Registry(db_name)
        print("✅ Successfully connected to database")
        print()
        
        with registry.cursor() as cr:
            env = Environment(cr, 1, {})
            
            # 1. Check core models
            print("1. CHECKING CORE MODELS")
            print("-" * 80)
            core_models = ['ir.http', 'ir.module.module', 'res.users', 'res.partner', 'ir.ui.menu']
            all_models_ok = True
            
            for model_name in core_models:
                try:
                    model = env[model_name]
                    print(f"  ✅ {model_name}: OK")
                except KeyError:
                    print(f"  ❌ {model_name}: MISSING")
                    all_models_ok = False
            
            print()
            
            # 2. Check installed modules
            print("2. CHECKING INSTALLED MODULES")
            print("-" * 80)
            installed_modules = env['ir.module.module'].search([
                ('state', '=', 'installed')
            ])
            
            print(f"  Total installed modules: {len(installed_modules)}")
            print()
            print("  Core modules:")
            for mod in installed_modules[:10]:
                print(f"    - {mod.name}")
            
            if len(installed_modules) > 10:
                print(f"    ... and {len(installed_modules) - 10} more")
            
            print()
            
            # 3. Check for event modules
            print("3. CHECKING EVENT MODULES STATUS")
            print("-" * 80)
            event_modules = env['ir.module.module'].search([
                ('name', 'ilike', 'event')
            ])
            
            installed_event_modules = [m for m in event_modules if m.state == 'installed']
            
            if installed_event_modules:
                print(f"  ⚠️  Found {len(installed_event_modules)} installed event modules:")
                for mod in installed_event_modules:
                    print(f"    - {mod.name}: {mod.state}")
            else:
                print("  ✅ No event modules installed")
            
            print()
            
            # 4. Check menu items
            print("4. CHECKING MENU ITEMS")
            print("-" * 80)
            all_menus = env['ir.ui.menu'].search([])
            print(f"  Total menu items: {len(all_menus)}")
            
            # Check for event menus
            event_menus = env['ir.ui.menu'].search([
                ('name', 'ilike', 'event')
            ])
            
            if event_menus:
                print(f"  ⚠️  Found {len(event_menus)} event-related menus:")
                for menu in event_menus[:5]:
                    print(f"    - {menu.name}")
            else:
                print("  ✅ No event-related menus found")
            
            print()
            
            # 5. Check users
            print("5. CHECKING USERS")
            print("-" * 80)
            users = env['res.users'].search([])
            print(f"  Total users: {len(users)}")
            for user in users:
                print(f"    - {user.login} ({user.name})")
            
            print()
            
            # 6. System summary
            print("=" * 80)
            print("VERIFICATION SUMMARY")
            print("=" * 80)
            
            if all_models_ok and not installed_event_modules:
                print("✅ SYSTEM STATUS: HEALTHY")
                print()
                print("All core models are present and working correctly.")
                print("No event modules are installed.")
                print("The system is ready to use!")
            elif all_models_ok:
                print("⚠️  SYSTEM STATUS: WORKING (with event modules)")
                print()
                print("All core models are present and working correctly.")
                print(f"However, {len(installed_event_modules)} event modules are still installed.")
            else:
                print("❌ SYSTEM STATUS: ISSUES DETECTED")
                print()
                print("Some core models are missing. Please check the logs.")
            
            print()
            print("=" * 80)
            print("Access your Odoo instance at: http://localhost:8069")
            print("Database: odoo_v1")
            print("=" * 80)
            
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print()
        print("Make sure:")
        print("1. PostgreSQL is running")
        print("2. Database 'odoo_v1' exists")
        print("3. Odoo server is running")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Error importing Odoo modules: {e}")
    print()
    print("Make sure you're running this script with the correct Python environment:")
    print("  source odoo-venv/bin/activate && python verify_odoo_system.py")
    sys.exit(1)

