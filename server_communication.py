import aiohttp
import asyncio
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ServerCommunication:
    def __init__(self, base_url):
        self.base_url = base_url
        self.access_token = None

    async def register(self, username, password):
        try:
            logger.debug(f"Attempting to register user: {username}")
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/register", json={"username": username, "password": password}) as response:
                    logger.debug(f"Registration response status: {response.status}")
                    if response.status == 201:
                        data = await response.json()
                        logger.info(f"Registration successful for user: {username}")
                        return True, "Registration successful"
                    else:
                        error_data = await response.json()
                        logger.warning(f"Registration failed. Server response: {error_data}")
                        return False, error_data.get("error", "Registration failed")
        except Exception as e:
            logger.error(f"Unexpected error during registration: {str(e)}")
            return False, f"Unexpected error: {str(e)}"

    async def login(self, username, password):
        try:
            logger.debug(f"Attempting to login with username: {username}")
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/login", json={"username": username, "password": password}) as response:
                    logger.debug(f"Login response status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Login response data: {data}")
                        self.access_token = data.get("access_token")
                        if self.access_token:
                            logger.info("Login successful")
                            return True, "Login successful"
                        else:
                            logger.warning("Login response didn't contain access token")
                            return False, "Login response didn't contain access token"
                    else:
                        error_data = await response.json()
                        logger.warning(f"Login failed. Server response: {error_data}")
                        return False, error_data.get("error", "Login failed")
        except Exception as e:
            logger.error(f"Unexpected error during login: {str(e)}")
            return False, f"Unexpected error: {str(e)}"

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