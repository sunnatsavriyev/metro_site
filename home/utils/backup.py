# home/utils/backup.py
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def trigger_backup(reason="auto"):
    """
    Django management command orqali DB backup yaratadi.
    Fayl BACKUP_DIR ichida saqlanadi.
    """
    try:
        call_command("db_backup")
        logger.info(f"Backup triggered due to: {reason}")
    except Exception as e:
        logger.exception(f"Backup failed: {e}")
