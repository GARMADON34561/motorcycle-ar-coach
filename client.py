"""
Client for connecting to the Motorcycle AR Coach environment
"""

import httpx
from typing import Optional
from models import MotorcycleAction, MotorcycleObservation

class MotorcycleEnvClient:
    """Client to connect to the environment server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30.0)
        self._session_id = None
    
    def reset(self) -> MotorcycleObservation:
        """Reset the environment"""
        response = self.client.post(f"{self.base_url}/reset")
        data = response.json()
        self._session_id = data.get("session_id")
        return MotorcycleObservation(**data["observation"])
    
    def step(self, action: MotorcycleAction) -> tuple:
        """Take a step in the environment"""
        response = self.client.post(
            f"{self.base_url}/step",
            json=action.dict()
        )
        data = response.json()
        obs = MotorcycleObservation(**data["observation"])
        return obs, data["reward"], data["done"], data.get("info", {})
    
    def close(self):
        """Close the client"""
        self.client.close()