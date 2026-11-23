param(
    [string]$BackupDir = "C:\backups\ecompra",
    [string]$DbName = "ecompra",
    [string]$User = "root",
    [string]$Password = "Admin2627"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $BackupDir "ecompra_$timestamp.sql"

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force
}

Write-Host "Starting backup to $backupFile..."
& mysqldump -u $User -p$Password --single-transaction --routines --triggers --default-character-set=utf8mb4 $DbName | Set-Content -Path $backupFile -Encoding utf8

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup successful: $backupFile"
    # Keep only last 7 backups
    Get-ChildItem $BackupDir -Filter "ecompra_*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 7 | Remove-Item -Force
} else {
    Write-Error "Backup failed with exit code $LASTEXITCODE"
    exit 1
}