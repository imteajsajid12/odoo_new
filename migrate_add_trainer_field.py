#!/usr/bin/env python3
"""
Migration script to add trainer_id column to event_event table
"""

import psycopg2
import sys

def migrate_database():
    """Add trainer_id column to event_event table"""
    
    print("=" * 80)
    print("MIGRATING DATABASE - ADDING TRAINER_ID COLUMN")
    print("=" * 80)
    print()
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            database="odoo_v1",
            user="luminous_imteaj",
            password=""
        )
        cursor = conn.cursor()
        
        print("✓ Connected to PostgreSQL database: odoo_v1")
        print()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'event_event' AND column_name = 'trainer_id'
        """)
        
        if cursor.fetchone():
            print("✓ trainer_id column already exists in event_event table")
            print()
            conn.close()
            return True
        
        print("Adding trainer_id column to event_event table...")
        
        # Add the trainer_id column
        cursor.execute("""
            ALTER TABLE event_event 
            ADD COLUMN trainer_id INTEGER REFERENCES res_partner(id) ON DELETE SET NULL
        """)
        
        print("✓ Column trainer_id added successfully!")
        print()
        
        # Commit the changes
        conn.commit()
        print("✓ Database migration completed!")
        print()
        
        # Verify the column was created
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'event_event' AND column_name = 'trainer_id'
        """)
        
        result = cursor.fetchone()
        if result:
            column_name, data_type = result
            print(f"Verification:")
            print(f"  - Column name: {column_name}")
            print(f"  - Data type: {data_type}")
            print(f"  - Foreign key: res_partner(id)")
            print()
            print("✓ MIGRATION SUCCESSFUL!")
            return True
        else:
            print("✗ Column verification failed!")
            return False
            
    except psycopg2.errors.DuplicateColumn:
        print("✓ Column trainer_id already exists (no action needed)")
        return True
    except Exception as e:
        print(f"✗ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    success = migrate_database()
    sys.exit(0 if success else 1)
