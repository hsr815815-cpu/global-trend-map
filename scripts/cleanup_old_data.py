#!/usr/bin/env python3
"""
cleanup_old_data.py — Archive Cleanup Script
Removes JSON backup files older than 30 days from public/data/archive/.
Runs weekly via GitHub Actions (maintenance.yml).
Usage: python scripts/cleanup_old_data.py
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR    = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = BASE_DIR / "public" / "data" / "archive"
MAX_AGE_DAYS = 30

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("cleanup_old_data")


def main():
    if not ARCHIVE_DIR.exists():
        log.info("Archive directory does not exist yet: %s", ARCHIVE_DIR)
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
    log.info("Cleaning archive files older than %d days (before %s)",
             MAX_AGE_DAYS, cutoff.strftime("%Y-%m-%d"))

    deleted = 0
    kept    = 0
    total_freed_bytes = 0

    for f in sorted(ARCHIVE_DIR.glob("*.json")):
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
        if mtime < cutoff:
            size = f.stat().st_size
            f.unlink()
            total_freed_bytes += size
            deleted += 1
            log.info("  DELETED: %s (modified %s, %d bytes)",
                     f.name, mtime.strftime("%Y-%m-%d"), size)
        else:
            kept += 1

    freed_kb = total_freed_bytes / 1024
    log.info("=" * 50)
    log.info("Cleanup complete: %d deleted | %d kept | %.1f KB freed",
             deleted, kept, freed_kb)
    log.info("=" * 50)


if __name__ == "__main__":
    main()
