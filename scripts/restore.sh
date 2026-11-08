#!/usr/bin/env bash
# ==============================================================================
# SAKHISAHAY MongoDB Database Restore Script
# Restores database from a compressed mongodump archive.
# ==============================================================================

set -euo pipefail

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <path_to_backup_archive.gz>"
    echo "Example: $0 ./backups/sakhisahay_backup_20261108_120000.gz"
    exit 1
fi

BACKUP_FILE="$1"
MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017}"
MONGODB_DB_NAME="${MONGODB_DB_NAME:-sakhisahay}"

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "[ERROR] Backup file does not exist: ${BACKUP_FILE}"
    exit 1
fi

echo "[CAUTION] This operation will restore database '${MONGODB_DB_NAME}' from '${BACKUP_FILE}'."
echo "[INFO] Starting restore..."

if command -v mongorestore &> /dev/null; then
    mongorestore --uri="${MONGODB_URI}" --nsInclude="${MONGODB_DB_NAME}.*" --archive="${BACKUP_FILE}" --gzip --drop
    echo "[SUCCESS] Restore completed successfully."
else
    echo "[WARN] 'mongorestore' binary not found locally. Attempting Docker restore..."
    if docker ps | grep -q sakhisahay_mongodb; then
        CONTAINER_NAME=$(docker ps --format '{{.Names}}' | grep sakhisahay_mongodb | head -n 1)
        cat "${BACKUP_FILE}" | docker exec -i "${CONTAINER_NAME}" mongorestore --nsInclude="${MONGODB_DB_NAME}.*" --archive --gzip --drop
        echo "[SUCCESS] Docker-based restore completed successfully."
    else
        echo "[ERROR] Neither local 'mongorestore' nor a running MongoDB Docker container was found."
        exit 1
    fi
fi
