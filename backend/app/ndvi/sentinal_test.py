# test_sentinel_auth.py
import asyncio
from sentinel_client import get_oauth_token

async def main():
    token = await get_oauth_token()
    print("Token:", token[:20] + "..." if token else None)

asyncio.run(main())
