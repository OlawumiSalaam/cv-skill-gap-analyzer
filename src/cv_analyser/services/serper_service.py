"""
Serper API service for YouTube video search.
"""

import requests
from typing import List, Optional
from loguru import logger

from cv_analyser.models.schemas import YouTubeVideo
from cv_analyser.config import get_settings


class SerperAPIError(Exception):
    """Custom exception for Serper API errors."""
    pass


class SerperService:
    """Service for interacting with Serper API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Serper service.
        
        Args:
            api_key: Serper API key (if None, loads from settings)
        """
        self.settings = get_settings()
        self.api_key = api_key or self.settings.serper_api_key
        self.base_url = "https://google.serper.dev/videos"
        
        if not self.api_key:
            raise ValueError("Serper API key not provided")
    
    def search_youtube_videos(
        self, 
        query: str, 
        num_results: Optional[int] = None
    ) -> List[YouTubeVideo]:
        """
        Search for YouTube videos using Serper API.
        
        Args:
            query: Search query
            num_results: Number of results to return (default from settings)
            
        Returns:
            List[YouTubeVideo]: List of YouTube videos
            
        Raises:
            SerperAPIError: If API call fails
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        
        num_results = num_results or self.settings.serper_num_results
        
        try:
            logger.info(f"Searching YouTube for: {query}")
            
            # Make API request
            response = requests.post(
                self.base_url,
                headers={
                    "X-API-KEY": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": query,
                    "num": num_results
                },
                timeout=15
            )
            
            # Check response status
            if response.status_code != 200:
                error_msg = f"Serper API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('message', 'Unknown error')}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                logger.error(error_msg)
                raise SerperAPIError(error_msg)
            
            # Parse response
            results = response.json()
            videos = []
            
            if 'videos' not in results:
                logger.warning("No videos found in API response")
                return videos
            
            # Extract video information
            for video_data in results['videos'][:num_results]:
                try:
                    video = YouTubeVideo(
                        title=video_data.get('title', 'N/A'),
                        link=video_data.get('link', '#'),
                        channel=video_data.get('channel', 'N/A'),
                        duration=video_data.get('duration', 'N/A'),
                        thumbnail=video_data.get('imageUrl')
                    )
                    videos.append(video)
                    logger.debug(f"Added video: {video.title}")
                except Exception as e:
                    logger.warning(f"Failed to parse video data: {str(e)}")
                    continue
            
            logger.info(f"Found {len(videos)} videos")
            return videos
            
        except requests.exceptions.Timeout:
            raise SerperAPIError("Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise SerperAPIError(f"Network error: {str(e)}")
        except Exception as e:
            if isinstance(e, SerperAPIError):
                raise
            logger.error(f"Unexpected error in search_youtube_videos: {str(e)}")
            raise SerperAPIError(f"Search failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test connection to Serper API.
        
        Returns:
            bool: True if connection successful
        """
        try:
            response = requests.post(
                self.base_url,
                headers={
                    "X-API-KEY": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "q": "test",
                    "num": 1
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_video_details(self, video_url: str) -> Optional[dict]:
        """
        Get additional details about a specific video.
        Note: This is a placeholder - Serper doesn't provide video details endpoint.
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            dict: Video details (basic info only)
        """
        # Extract video ID from URL
        video_id = None
        if 'youtube.com/watch?v=' in video_url:
            video_id = video_url.split('watch?v=')[1].split('&')[0]
        elif 'youtu.be/' in video_url:
            video_id = video_url.split('youtu.be/')[1].split('?')[0]
        
        if video_id:
            return {
                'video_id': video_id,
                'url': video_url,
                'embed_url': f"https://www.youtube.com/embed/{video_id}"
            }
        
        return None