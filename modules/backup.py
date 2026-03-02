import shutil
import datetime
import os
import streamlit as st

DB_FILE = "volts.db"
BACKUP_DIR = "backups"

def perform_backup():
    """Copies volts.db to backups/ folder with timestamp."""
    try:
        if not os.path.exists(DB_FILE):
            return # No DB to backup
            
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        backup_path = os.path.join(BACKUP_DIR, f"volts_backup_{timestamp}.db")
        
        shutil.copy2(DB_FILE, backup_path)
        
        # Cleanup old backups (keep last 7 days or last 10 backups)
        cleanup_old_backups()
        
    except Exception as e:
        print(f"Backup Warning: {e}")

def cleanup_old_backups(keep=10):
    """Keeps only the last 'keep' backups."""
    try:
        files = [os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.endswith(".db")]
        files.sort(key=os.path.getmtime)
        
        if len(files) > keep:
            to_remove = files[:-keep]
            for f in to_remove:
                os.remove(f)
    except:
        pass
