"""
Frigate Client for AI Security Lab v4.0
HTTP client for Frigate NVR API integration
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class FrigateClient:
    """
    HTTP client for Frigate Plus NVR system.
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 10
    ):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout

        # Create HTTP client
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=timeout
        )

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def get_cameras(self) -> List[Dict[str, Any]]:
        """
        Get list of cameras from Frigate.
        
        Returns:
            List of camera configurations
        """
        try:
            response = await self.client.get('/api/config')
            if response.status_code == 200:
                config = response.json()
                return list(config.get('cameras', {}).values())
            return []
        except Exception as e:
            logger.error(f"Failed to get cameras from Frigate: {e}")
            return []

    async def get_camera_status(self, camera_id: str) -> Dict[str, Any]:
        """
        Get status for specific camera.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Camera status dictionary
        """
        try:
            response = await self.client.get(f'/api/{camera_id}/status')
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Failed to get camera status for {camera_id}: {e}")
            return {}

    async def get_events(
        self,
        camera_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent events from Frigate.
        
        Args:
            camera_id: Optional camera filter
            limit: Maximum events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            params = {'limit': limit}
            if camera_id:
                params['camera'] = camera_id

            response = await self.client.get('/api/events', params=params)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            logger.error(f"Failed to get events: {e}")
            return []

    async def get_snapshot(self, camera_id: str) -> Optional[bytes]:
        """
        Get latest snapshot for camera.
        
        Args:
            camera_id: Camera identifier
            
        Returns:
            Image bytes or None
        """
        try:
            response = await self.client.get(f'/api/{camera_id}/latest.jpg')
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            logger.error(f"Failed to get snapshot for {camera_id}: {e}")
            return None

    async def health_check(self) -> bool:
        """
        Check if Frigate is accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            response = await self.client.get('/api/version', timeout=3.0)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Frigate health check failed: {e}")
            return False
