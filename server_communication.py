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
                async with session.post(f"{self.base_url}/register", json={"username": username, "password": password}, timeout=5) as response:
                    if response.status == 201:
                        return True, "User registered successfully"
                    else:
                        data = await response.json()
                        return False, data.get("error", "Registration failed")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return False, str(e)

    async def login(self, username, password):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/login", json={"username": username, "password": password}, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data["access_token"]
                        return True, "Login successful"
                    else:
                        data = await response.json()
                        return False, data.get("error", "Login failed")
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return False, str(e)

    async def get_leaderboard(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/leaderboard", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data, None
                    else:
                        try:
                            error_data = await response.json()
                            error_message = error_data.get('error', 'Unknown error')
                            error_details = error_data.get('details', '')
                            error_stack_trace = error_data.get('stack_trace', '')
                            logger.error(f"Server error: {error_message}\nDetails: {error_details}\nStack trace: {error_stack_trace}")
                        except json.JSONDecodeError:
                            error_message = await response.text()
                            logger.error(f"Failed to decode JSON response: {error_message}")
                        return [], f"Server error: {response.status}, {error_message}"
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Connection error: {str(e)}")
            return [], f"Connection error: {str(e)}"

    async def submit_score(self, player_name, score):
        if not self.access_token:
            return False, "Not authenticated"
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/submit_score", 
                                        json={"name": player_name, "score": score}, 
                                        headers=headers, 
                                        timeout=5) as response:
                    if response.status == 200:
                        return True, "Score submitted successfully"
                    else:
                        error_data = await response.json()
                        return False, f"Server error: {response.status}, {error_data.get('error', 'Unknown error')}"
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return False, f"Connection error: {str(e)}"

server_comm = ServerCommunication("http://127.0.0.1:5000/api")