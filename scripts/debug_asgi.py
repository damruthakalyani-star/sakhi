import sys
from backend.app.main import create_application

print("Creating app...", flush=True)
app = create_application()
print("App created. Testing ASGI call directly...", flush=True)

import asyncio

async def run_asgi():
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/v1/health",
        "raw_path": b"/api/v1/health",
        "query_string": b"",
        "headers": [(b"host", b"testserver")],
        "client": ("127.0.0.1", 12345),
        "server": ("127.0.0.1", 80),
    }

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        print("ASGI Send:", message["type"], flush=True)

    print("Calling app directly...", flush=True)
    await app(scope, receive, send)
    print("ASGI call finished!", flush=True)

asyncio.run(run_asgi())
