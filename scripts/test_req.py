import sys
import asyncio
import httpx
from backend.app.main import create_application

print("Starting test...", flush=True)

app = create_application()
print("App created", flush=True)

async def test():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("Calling /health...", flush=True)
        r = await client.get("/api/v1/health")
        print("Result:", r.status_code, r.text, flush=True)

asyncio.run(test())
