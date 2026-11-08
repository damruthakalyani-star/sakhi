# SAKHISAHAY: Operations & Incident Response Runbook

This runbook guides system administrators, DevOps engineers, and on-call operators in monitoring, maintaining, and troubleshooting the SAKHISAHAY production environment.

---

## 1. Quick Diagnostic Triage

### 1.1 Health Probe Verification
```bash
# Liveness probe (checks application process)
curl -s http://localhost:8000/api/v1/health/live | jq .

# Readiness probe (checks database ping and connection pool)
curl -s http://localhost:8000/api/v1/health/ready | jq .
```

Expected Response:
```json
{
  "status": "healthy",
  "app": "SAKHISAHAY",
  "environment": "production",
  "database": "connected",
  "database_latency_ms": 1.42,
  "timestamp": "2026-11-08T12:00:00Z"
}
```

### 1.2 Inspect Container Status
```bash
docker compose -f docker-compose.prod.yml ps
```

### 1.3 View Live Logs
```bash
# View backend application logs
docker compose -f docker-compose.prod.yml logs -f --tail=100 backend

# View Nginx proxy logs
docker compose -f docker-compose.prod.yml logs -f --tail=100 proxy
```

---

## 2. Correlating Requests with `request_id`

Every request processed by the backend receives a unique UUIDv4 `request_id` header `X-Request-ID`. All JSON logs emitted during that request lifecycle include `"request_id"`.

To trace an error reported by a user:
```bash
docker compose -f docker-compose.prod.yml logs backend | grep '"request_id": "<ID_HERE>"' | jq .
```

---

## 3. Incident Scenarios & Remediation

### 3.1 Scenario A: 502 Bad Gateway
- **Symptom:** Nginx returns `502 Bad Gateway` to users.
- **Root Causes:** Backend container crashed, OOM killed, or restarted.
- **Diagnostic Steps:**
  ```bash
  docker compose -f docker-compose.prod.yml ps backend
  docker compose -f docker-compose.prod.yml logs --tail=100 backend
  ```
- **Remediation:**
  1. If container status is `Exited`, inspect exit code: `docker inspect sakhisahay_backend_prod --format='{{.State.ExitCode}}'`.
  2. If OOM killed (`ExitCode 137`), increase memory limit in `docker-compose.prod.yml`.
  3. Restart the backend service: `docker compose -f docker-compose.prod.yml restart backend`.

### 3.2 Scenario B: Database Connection Timeout
- **Symptom:** `/api/v1/health/ready` returns `503 Service Unavailable` with `"database": "disconnected"`.
- **Root Causes:** MongoDB process stopped, Atlas IP whitelist expired, network partition.
- **Diagnostic Steps:**
  ```bash
  # Check MongoDB container if self-hosted
  docker compose -f docker-compose.prod.yml ps mongodb
  # Test connection string from inside container
  docker compose -f docker-compose.prod.yml exec backend python -c "
  import asyncio
  from app.db.mongo import mongo_manager
  async def ping():
      await mongo_manager.connect()
      print('DB Connected successfully!')
      await mongo_manager.close()
  asyncio.run(ping())
  "
  ```
- **Remediation:**
  1. Restart MongoDB container: `docker compose -f docker-compose.prod.yml restart mongodb`.
  2. If using Atlas, log into MongoDB Atlas web console and verify Network Access IP whitelist.

### 3.3 Scenario C: Account Lockout Reset
- **Symptom:** Legitimate user locked out after entering incorrect password 5 times.
- **Remediation:**
  Unlock the user immediately using the administrative command:
  ```bash
  docker compose -f docker-compose.prod.yml exec backend python -c "
  import asyncio
  from app.db.mongo import mongo_manager, get_database
  async def unlock(email):
      await mongo_manager.connect()
      db = get_database()
      res = await db['users'].update_one(
          {'email': email.lower()},
          {'\$set': {'failed_login_attempts': 0, 'locked_until': None}}
      )
      print(f'Unlocked {email}: modified {res.modified_count} records')
      await mongo_manager.close()
  asyncio.run(unlock('user@example.com'))
  "
  ```

---

## 4. Automated Daily Backup via Cron

Schedule daily compressed backups at 02:00 AM UTC:
```bash
sudo crontab -e
```
Add the following entry:
```cron
0 2 * * * /opt/sakhisahay/scripts/backup.sh >> /var/log/sakhisahay_backup.log 2>&1
```

To test disaster recovery in staging:
```bash
bash scripts/restore.sh /opt/sakhisahay/backups/sakhisahay_backup_YYYYMMDD_HHMMSS.gz
```
