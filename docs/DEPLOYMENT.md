# SAKHISAHAY: Production Deployment Guide

This guide walks you through deploying the SAKHISAHAY platform to production using Docker Compose, Nginx, and MongoDB Atlas (or self-hosted MongoDB).

---

## 1. Prerequisites & Server Sizing

### 1.1 Minimum Hardware Requirements (Single Node VPS)
- **OS:** Ubuntu 22.04 LTS or 24.04 LTS (x86_64)
- **CPU:** 2 vCPUs
- **RAM:** 4 GB RAM (2 GB minimum with swap)
- **Disk:** 40 GB SSD
- **Network:** Static public IPv4 address with ports `80` and `443` open in security groups/firewall.

### 1.2 Required Software
- Docker Engine 24.0+
- Docker Compose v2.20+
- Git

Install on Ubuntu:
```bash
sudo apt update && sudo apt install -y curl git ufw
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

---

## 2. Environment Configuration

### 2.1 Backend Production Variables (`backend/.env`)

Generate a secure 64-character random secret key:
```bash
openssl rand -hex 32
```

Create `backend/.env`:
```ini
APP_NAME=SAKHISAHAY
APP_ENV=production
DEBUG=false
API_V1_PREFIX=/api/v1
SECRET_KEY=paste_the_64_char_hex_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256

# MongoDB Atlas or Self-hosted URI
MONGODB_URI=mongodb+srv://<db_user>:<db_password>@cluster0.example.mongodb.net/sakhisahay_prod?retryWrites=true&w=majority
MONGODB_DB_NAME=sakhisahay_prod
MONGODB_MAX_POOL_SIZE=50
MONGODB_MIN_POOL_SIZE=5

# Production Domain(s) - NO WILDCARDS
CORS_ORIGINS=https://sakhisahay.example.org,https://www.sakhisahay.example.org
ALLOWED_HOSTS=sakhisahay.example.org,api.sakhisahay.example.org

RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_AUTH=5/minute
LOG_LEVEL=INFO

# First administrator account created automatically on first run
FIRST_ADMIN_EMAIL=admin@sakhisahay.example.org
FIRST_ADMIN_PASSWORD=SetAStrongRandomPassword123!
```

### 2.2 Frontend Production Variables (`frontend/.env`)
```ini
VITE_API_BASE_URL=/api/v1
```

---

## 3. SSL/TLS Certificate Setup (Let's Encrypt / Certbot)

Install Certbot and obtain free certificates:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --standalone -d sakhisahay.example.org -d www.sakhisahay.example.org
```

Certificates will be saved to `/etc/letsencrypt/live/sakhisahay.example.org/`.
Mount these certificates into `nginx/nginx.conf` under `/etc/nginx/ssl/`.

---

## 4. Production Deployment with Docker Compose

### 4.1 Clone Repository and Prepare Environment
```bash
git clone https://github.com/your-org/SAKHISAHAY.git /opt/sakhisahay
cd /opt/sakhisahay
cp backend/.env.example backend/.env
# Edit backend/.env with your production credentials
```

### 4.2 Run Database Migrations
```bash
docker compose -f docker-compose.prod.yml run --rm backend python scripts/migrate.py
```

### 4.3 Launch Application Stack
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### 4.4 Verify Container Health
```bash
docker compose -f docker-compose.prod.yml ps
```
Confirm all services (`backend`, `frontend`, `proxy`, `mongodb`) indicate `healthy` or `running`.

Run the automated healthcheck:
```bash
docker compose -f docker-compose.prod.yml exec backend python /app/scripts/healthcheck.py
```
Output:
```
[HEALTHCHECK OK] Status: healthy | Database: connected
```

---

## 5. Zero-Downtime Rolling Update Procedure

When deploying new updates or bugfixes:

```bash
# 1. Pull latest code
git pull origin main

# 2. Build updated images in background
docker compose -f docker-compose.prod.yml build

# 3. Run any pending database migrations
docker compose -f docker-compose.prod.yml run --rm backend python scripts/migrate.py

# 4. Restart services with minimal downtime
docker compose -f docker-compose.prod.yml up -d --no-deps backend frontend

# 5. Verify healthcheck probe
curl -f https://sakhisahay.example.org/api/v1/health/live
```

---

## 6. Pre-Flight Production Checklist

- [ ] `DEBUG=false` confirmed in `backend/.env`.
- [ ] `SECRET_KEY` is a 64+ char random string, not the default development string.
- [ ] `CORS_ORIGINS` has exact production domains without wildcard `*`.
- [ ] MongoDB Atlas IP whitelist allows connection from production server IP.
- [ ] HTTPS redirect active; SSL certificates valid and set to auto-renew via cron.
- [ ] Daily backup cron job active (`scripts/backup.sh`).
