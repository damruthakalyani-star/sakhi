#!/usr/bin/env python3
"""Container & Deployment Healthcheck Probe for SAKHISAHAY."""

import sys
import urllib.request
import json

HEALTH_URL = "http://localhost:8000/api/v1/health/ready"


def check_health():
    try:
        req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "HealthcheckProbe/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")
            data = json.loads(body)

            if status_code == 200 and data.get("status") == "healthy":
                print(f"[HEALTHCHECK OK] Status: {data.get('status')} | Database: {data.get('database')}")
                sys.exit(0)
            else:
                print(f"[HEALTHCHECK WARN] Status code: {status_code} | Body: {body}")
                sys.exit(1)
    except Exception as err:
        print(f"[HEALTHCHECK FAIL] Error connecting to {HEALTH_URL}: {err}")
        sys.exit(1)


if __name__ == "__main__":
    check_health()
