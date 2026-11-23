param(
    [string]$BackupFile,
    [string]$DbName = "ecompra",
    [string]$User = "root",
    [string]$Password = "Admin2627"
)

if (-not (Test-Path $BackupFile)) {
    Write-Error "Backup file not found: $BackupFile"
    exit 1
}

Write-Host "Restoring $BackupFile to $DbName..."
# Drop and recreate database
& mysql -u $User -p$Password -e "DROP DATABASE IF EXISTS $DbName; CREATE DATABASE $DbName CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
# Restore
Get-Content $BackupFile | & mysql -u $User -p$Password $DbName

if ($LASTEXITCODE -eq 0) {
    Write-Host "Restore successful"
} else {
    Write-Error "Restore failed with exit code $LASTEXITCODE"
    exit 1
}