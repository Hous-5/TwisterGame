import aiohttp
import asyncio

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
                        return data
                    else:
                        print(f"Failed to get leaderboard. Status: {response.status}")
                        return []
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error getting leaderboard: {str(e)}")
            return []

    async def submit_score(self, score):
        if not self.access_token:
            return False, "Not authenticated"
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/submit_score", json={"score": score}, headers=headers, timeout=5) as response:
                    if response.status == 200:
                        return True, "Score submitted successfully"
                    else:
                        try:
                            data = await response.json()
                            return False, data.get("error", "Failed to submit score")
                        except aiohttp.ContentTypeError:
                            text = await response.text()
                            return False, f"Server error: {response.status}, {text[:100]}..."
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return False, str(e)

server_comm = ServerCommunication("http://127.0.0.1:5000/api")