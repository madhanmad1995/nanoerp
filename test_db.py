"""
reset_all.py - Completely reset the database and verify
"""
import os
import shutil
import sqlite3

def reset_database():
    # Paths
    db_path = 'data/nano_erp.db'
    backup_path = 'data/nano_erp_backup.db'
    
    print("=" * 60)
    print("COMPLETE DATABASE RESET")
    print("=" * 60)
    
    # Backup old database if exists
    if os.path.exists(db_path):
        shutil.copy2(db_path, backup_path)
        print(f"Backed up old database to: {backup_path}")
    
    # Delete database
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Deleted old database")
    
    # Delete any .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                try:
                    os.remove(os.path.join(root, file))
                except:
                    pass
    print("Cleared Python cache files")
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    print("\nNow manually check your database.py file:")
    print("1. Open database.py")
    print("2. Find the CREATE TABLE invoices statement")
    print("3. Make sure it includes these 3 columns:")
    print("   - discount_amount REAL NOT NULL DEFAULT 0")
    print("   - discount_percentage REAL NOT NULL DEFAULT 0")
    print("   - discounted_subtotal REAL NOT NULL DEFAULT 0")
    print("\nThen restart your application.")
    
    return True

if __name__ == "__main__":
    confirm = input("This will DELETE ALL DATA. Type 'RESET' to confirm: ")
    if confirm == 'RESET':
        reset_database()
    else:
        print("Reset cancelled.")