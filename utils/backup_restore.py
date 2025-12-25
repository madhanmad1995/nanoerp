"""
backup_restore.py - Database backup and restore utilities
"""
import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
import json

class BackupManager:
    """Manage database backups"""
    
    def __init__(self, db_path="data/nano_erp.db", backup_dir="backups"):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, comment=""):
        """Create a backup of the database"""
        if not self.db_path.exists():
            return None
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"nanoerp_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_name
        
        # Copy database file
        shutil.copy2(self.db_path, backup_path)
        
        # Create metadata file
        metadata = {
            "timestamp": timestamp,
            "original_path": str(self.db_path),
            "backup_path": str(backup_path),
            "size": os.path.getsize(backup_path),
            "comment": comment,
            "created_at": datetime.now().isoformat()
        }
        
        metadata_path = self.backup_dir / f"nanoerp_backup_{timestamp}.meta.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Clean old backups (keep last 30 days)
        self.clean_old_backups(days=30)
        
        return backup_path
    
    def restore_backup(self, backup_path):
        """Restore database from backup"""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        # Close any existing database connections
        try:
            from database import db
            db.close()
        except:
            pass
        
        # Create backup of current database before restore
        if self.db_path.exists():
            temp_backup = self.db_path.with_suffix('.db.bak')
            shutil.copy2(self.db_path, temp_backup)
        
        # Restore from backup
        shutil.copy2(backup_path, self.db_path)
        
        return True
    
    def list_backups(self):
        """List all available backups"""
        backups = []
        
        for file in self.backup_dir.glob("nanoerp_backup_*.db"):
            meta_file = file.with_suffix('.meta.json')
            metadata = {}
            
            if meta_file.exists():
                try:
                    with open(meta_file, 'r') as f:
                        metadata = json.load(f)
                except:
                    metadata = {"error": "Could not read metadata"}
            
            backups.append({
                "file": file.name,
                "path": str(file),
                "size": file.stat().st_size,
                "created": file.stat().st_ctime,
                "metadata": metadata
            })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return backups
    
    def clean_old_backups(self, days=30):
        """Delete backups older than specified days"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        for file in self.backup_dir.glob("nanoerp_backup_*"):
            if file.stat().st_ctime < cutoff_time:
                # Delete backup file and metadata
                file.unlink(missing_ok=True)
                meta_file = file.with_suffix('.meta.json')
                meta_file.unlink(missing_ok=True)
    
    def auto_backup(self):
        """Create automatic backup if needed (daily)"""
        # Check if backup needed (once per day)
        last_backup_time = self.get_last_backup_time()
        
        if last_backup_time is None or (datetime.now() - last_backup_time).days >= 1:
            return self.create_backup(comment="Automatic daily backup")
        
        return None
    
    def get_last_backup_time(self):
        """Get time of last backup"""
        backups = self.list_backups()
        if not backups:
            return None
        
        latest_backup = backups[0]
        return datetime.fromtimestamp(latest_backup["created"])
    
    def export_to_sql(self, output_path):
        """Export database to SQL file"""
        conn = sqlite3.connect(self.db_path)
        
        with open(output_path, 'w') as f:
            for line in conn.iterdump():
                f.write(f'{line}\n')
        
        conn.close()
        return output_path
    
    def import_from_sql(self, sql_path):
        """Import database from SQL file"""
        # Backup current database
        self.create_backup(comment="Pre-import backup")
        
        # Close existing connection
        try:
            from database import db
            db.close()
        except:
            pass
        
        # Remove existing database
        if self.db_path.exists():
            self.db_path.unlink()
        
        # Create new database and import
        conn = sqlite3.connect(self.db_path)
        
        with open(sql_path, 'r') as f:
            sql_script = f.read()
        
        conn.executescript(sql_script)
        conn.commit()
        conn.close()
        
        return True