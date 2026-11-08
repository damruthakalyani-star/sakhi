import asyncio

async def g():
    return 42

if __name__ == "__main__":
    res = asyncio.run(g())
    print("Result:", res)
