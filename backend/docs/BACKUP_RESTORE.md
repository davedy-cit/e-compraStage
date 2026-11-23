# E-Compra Backup & Restore Procedure

## Backup Script
Location: `scripts/backup.ps1`
Runs: `mysqldump --single-transaction --routines --triggers --default-character-set=utf8mb4`
Retention: 7 days (auto-cleanup)

## Restore Script
Location: `scripts/restore.ps1`
Drops and recreates target database, then restores.

## Drill Log (2026-11-23)
- Backup file: `ecompra_20261123_135807.sql` (76 KB)
- Restore target: `test_ecompra_restore`
- Tables restored: 35 (28 domain + 7 Django)
- Data verified: 34 products, 6 vendors, 9 categories, 26 orders
- Time: Backup ~2s, Restore ~3s
- Status: ✅ SUCCESS

## Production Schedule
- Daily at 02:00 via Windows Task Scheduler
- Off-site copy: Upload to cloud storage (not implemented in scope)
- Monthly restore test: First Monday of each month