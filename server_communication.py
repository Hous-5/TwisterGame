import aiohttp
import asyncio

class ServerCommunication:
    def __init__(self, base_url):
        self.base_url = base_url

    async def get_leaderboard(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/leaderboard", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"Received leaderboard data: {data}")  # Debug print
                        return data
                    else:
                        print(f"Failed to get leaderboard. Status: {response.status}")  # Debug print
                        return []
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error getting leaderboard: {str(e)}")  # Debug print
            return []

    async def submit_score(self, player_name, score):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/submit_score", json={"name": player_name, "score": score}, timeout=5) as response:
                    success = response.status == 200
                    print(f"Score submission {'successful' if success else 'failed'}. Status: {response.status}")  # Debug print
                    return success
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error submitting score: {str(e)}")  # Debug print
            return False

server_comm = ServerCommunication("http://127.0.0.1:5000/api")