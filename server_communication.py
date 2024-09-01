import aiohttp
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServerCommunication:
    def __init__(self, base_url):
        self.base_url = base_url
        self.access_token = None

    async def register(self, username, password):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/register", json={"username": username, "password": password}) as response:
                    if response.status == 201:
                        return True, "User registered successfully"
                    else:
                        data = await response.json()
                        return False, data.get("error", "Registration failed")
        except aiohttp.ClientError as e:
            return False, str(e)

    async def login(self, username, password):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/login", json={"username": username, "password": password}) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data["access_token"]
                        return True, "Login successful"
                    else:
                        data = await response.json()
                        return False, data.get("error", "Login failed")
        except aiohttp.ClientError as e:
            return False, str(e)

    async def get_leaderboard(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/leaderboard") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Failed to fetch leaderboard: {response.status}")
        except aiohttp.ClientError as e:
            raise Exception(f"Network error: {str(e)}")

    async def submit_score(self, score):
        if not self.access_token:
            return False, "Not authenticated"
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/submit_score", json={"score": score}, headers=headers) as response:
                    if response.status == 200:
                        return True, "Score submitted successfully"
                    else:
                        data = await response.json()
                        return False, data.get("error", "Failed to submit score")
        except aiohttp.ClientError as e:
            return False, f"Network error: {str(e)}"

server_comm = ServerCommunication("http://localhost:5000/api")