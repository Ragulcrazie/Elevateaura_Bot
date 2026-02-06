
import asyncio
import aiohttp
import sys

async def test_api():
    url = "https://elevateaura-bot.onrender.com/api/ghosts?pack_id=10&user_id=1&mode=daily"
    print(f"Testing URL: {url}")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                data = await response.json()
                ghosts = data.get("ghosts", [])
                print(f"Ghost Count: {len(ghosts)}")
                print(f"First Ghost: {ghosts[0] if ghosts else 'None'}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # If on windows, loop policy might differ, but simple run should work
    asyncio.run(test_api())
