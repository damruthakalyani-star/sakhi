#!/usr/bin/env bash
# ==============================================================================
# SAKHISAHAY MongoDB Database Backup Script
# Creates a compressed, timestamped mongodump archive.
# ==============================================================================

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/sakhisahay_backup_${TIMESTAMP}.gz"

MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017}"
MONGODB_DB_NAME="${MONGODB_DB_NAME:-sakhisahay}"

mkdir -p "${BACKUP_DIR}"

echo "[INFO] Starting MongoDB backup for database '${MONGODB_DB_NAME}'..."
echo "[INFO] Destination: ${BACKUP_FILE}"

if command -v mongodump &> /dev/null; then
    mongodump --uri="${MONGODB_URI}" --db="${MONGODB_DB_NAME}" --archive="${BACKUP_FILE}" --gzip
    echo "[SUCCESS] Backup completed successfully: ${BACKUP_FILE}"
    echo "[INFO] Archive size: $(du -h "${BACKUP_FILE}" | cut -f1)"
else
    echo "[WARN] 'mongodump' binary not found locally. Attempting Docker backup..."
    if docker ps | grep -q sakhisahay_mongodb; then
        CONTAINER_NAME=$(docker ps --format '{{.Names}}' | grep sakhisahay_mongodb | head -n 1)
        docker exec "${CONTAINER_NAME}" mongodump --db="${MONGODB_DB_NAME}" --archive --gzip > "${BACKUP_FILE}"
        echo "[SUCCESS] Docker-based backup completed successfully: ${BACKUP_FILE}"
    else
        echo "[ERROR] Neither local 'mongodump' nor a running MongoDB Docker container was found."
        exit 1
    fi
fi
