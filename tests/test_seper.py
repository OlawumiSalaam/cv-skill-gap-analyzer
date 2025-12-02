"""
Tests for Serper API service.
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from CV_analyser.services.serper_service import SerperService, SerperAPIError
from CV_analyser.models.schemas import YouTubeVideo


class TestSerperService:
    """Test cases for SerperService class."""
    
    @pytest.fixture
    def serper_service(self):
        """Create SerperService instance for testing."""
        return SerperService(api_key="test_serper_key_12345")
    
    @pytest.fixture
    def mock_video_response(self):
        """Mock successful Serper API response with videos."""
        return {
            "videos": [
                {
                    "title": "Python Tutorial - Full Course for Beginners",
                    "link": "https://youtube.com/watch?v=_uQrJ0TkZlc",
                    "channel": "Programming with Mosh",
                    "duration": "6:14:07",
                    "imageUrl": "https://i.ytimg.com/vi/_uQrJ0TkZlc/maxresdefault.jpg"
                },
                {
                    "title": "Learn Python - Full Course for Beginners [Tutorial]",
                    "link": "https://youtube.com/watch?v=rfscVS0vtbw",
                    "channel": "freeCodeCamp.org",
                    "duration": "4:26:52",
                    "imageUrl": "https://i.ytimg.com/vi/rfscVS0vtbw/maxresdefault.jpg"
                },
                {
                    "title": "Python for Everybody - Full Course",
                    "link": "https://youtube.com/watch?v=8DvywoWv6fI",
                    "channel": "freeCodeCamp.org",
                    "duration": "13:45:00",
                    "imageUrl": "https://i.ytimg.com/vi/8DvywoWv6fI/maxresdefault.jpg"
                },
                {
                    "title": "Docker Tutorial for Beginners",
                    "link": "https://youtube.com/watch?v=fqMOX6JJhGo",
                    "channel": "Programming with Mosh",
                    "duration": "1:02:32",
                    "imageUrl": "https://i.ytimg.com/vi/fqMOX6JJhGo/maxresdefault.jpg"
                },
                {
                    "title": "Kubernetes Tutorial for Beginners",
                    "link": "https://youtube.com/watch?v=X48VuDVv0do",
                    "channel": "TechWorld with Nana",
                    "duration": "3:53:14",
                    "imageUrl": "https://i.ytimg.com/vi/X48VuDVv0do/maxresdefault.jpg"
                }
            ]
        }
    
    def test_initialization_with_api_key(self):
        """Test service initialization with API key."""
        service = SerperService(api_key="test_key")
        assert service.api_key == "test_key"
        assert service.base_url == "https://google.serper.dev/videos"
    
    def test_initialization_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with patch('cv_analyzer.services.serper_service.get_settings') as mock_settings:
            mock_settings.return_value.serper_api_key = None
            with pytest.raises(ValueError, match="Serper API key not provided"):
                SerperService()
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_search_youtube_videos_success(
        self, 
        mock_post, 
        serper_service, 
        mock_video_response
    ):
        """Test successful YouTube video search."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_video_response
        mock_post.return_value = mock_response
        
        # Execute
        videos = serper_service.search_youtube_videos("Python tutorial")
        
        # Verify
        assert len(videos) == 5
        assert all(isinstance(v, YouTubeVideo) for v in videos)
        assert videos[0].title == "Python Tutorial - Full Course for Beginners"
        assert videos[0].channel == "Programming with Mosh"
        assert "youtube.com" in videos[0].link
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["headers"]["X-API-KEY"] == "test_serper_key_12345"
        assert call_args[1]["json"]["q"] == "Python tutorial"
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_search_youtube_videos_custom_num_results(
        self, 
        mock_post, 
        serper_service, 
        mock_video_response
    ):
        """Test video search with custom number of results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_video_response
        mock_post.return_value = mock_response
        
        videos = serper_service.search_youtube_videos("Python tutorial", num_results=3)
        
        # Should still return all available, but API call should request 3
        call_args = mock_post.call_args
        assert call_args[1]["json"]["num"] == 3
    
    def test_search_youtube_videos_empty_query(self, serper_service):
        """Test video search with empty query."""
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            serper_service.search_youtube_videos("")
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_search_youtube_videos_api_error(self, mock_post, serper_service):
        """Test video search with API error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid API key"}
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        with pytest.raises(SerperAPIError, match="Serper API error: 401"):
            serper_service.search_youtube_videos("Python tutorial")
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_search_youtube_videos_no_videos_in_response(
        self, 
        mock_post, 
        serper_service
    ):
        """Test video search when no videos found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # No 'videos' key
        mock_post.return_value = mock_response
        
        videos = serper_service.search_youtube_videos("Python tutorial")
        
        assert videos == []
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_search_youtube_videos_timeout(self, mock_post, serper_service):
        """Test video search with timeout."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(SerperAPIError, match="Request timed out"):
            serper_service.search_youtube_videos("Python tutorial")
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_search_youtube_videos_network_error(self, mock_post, serper_service):
        """Test video search with network error."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")
        
        with pytest.raises(SerperAPIError, match="Network error"):
            serper_service.search_youtube_videos("Python tutorial")
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_search_youtube_videos_partial_data(self, mock_post, serper_service):
        """Test video search with incomplete video data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "videos": [
                {
                    "title": "Complete Video",
                    "link": "https://youtube.com/watch?v=abc123",
                    "channel": "TestChannel",
                    "duration": "10:00",
                    "imageUrl": "https://img.youtube.com/vi/abc123/0.jpg"
                },
                {
                    "title": "Missing Duration",
                    "link": "https://youtube.com/watch?v=def456",
                    "channel": "TestChannel2",
                    # Missing duration and imageUrl
                },
                {
                    # Completely broken video data
                    "some_field": "invalid"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        videos = serper_service.search_youtube_videos("test")
        
        # Should handle gracefully - valid videos parsed, invalid ones skipped
        assert len(videos) >= 1
        assert videos[0].title == "Complete Video"
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_search_youtube_videos_validates_youtube_links(
        self, 
        mock_post, 
        serper_service
    ):
        """Test that non-YouTube links are validated."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "videos": [
                {
                    "title": "Valid YouTube Video",
                    "link": "https://youtube.com/watch?v=valid123",
                    "channel": "Channel1",
                    "duration": "10:00"
                },
                {
                    "title": "Invalid Link",
                    "link": "https://notyoutube.com/video",
                    "channel": "Channel2",
                    "duration": "5:00"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        videos = serper_service.search_youtube_videos("test")
        
        # Invalid YouTube link should be caught by Pydantic validation
        # Only valid YouTube videos should be returned
        assert all("youtube.com" in v.link or "youtu.be" in v.link for v in videos)
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_test_connection_success(self, mock_post, serper_service):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = serper_service.test_connection()
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_test_connection_failure(self, mock_post, serper_service):
        """Test failed connection test."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        result = serper_service.test_connection()
        
        assert result is False
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_test_connection_exception(self, mock_post, serper_service):
        """Test connection test with exception."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        result = serper_service.test_connection()
        
        assert result is False
    
    def test_get_video_details_youtube_url(self, serper_service):
        """Test extracting video details from YouTube URL."""
        url = "https://www.youtube.com/watch?v=abc123"
        details = serper_service.get_video_details(url)
        
        assert details is not None
        assert details["video_id"] == "abc123"
        assert details["url"] == url
        assert "embed" in details["embed_url"]
    
    def test_get_video_details_youtu_be_url(self, serper_service):
        """Test extracting video details from youtu.be URL."""
        url = "https://youtu.be/xyz789"
        details = serper_service.get_video_details(url)
        
        assert details is not None
        assert details["video_id"] == "xyz789"
        assert details["embed_url"] == "https://www.youtube.com/embed/xyz789"
    
    def test_get_video_details_invalid_url(self, serper_service):
        """Test video details with invalid URL."""
        url = "https://notayoutubeurl.com/video"
        details = serper_service.get_video_details(url)
        
        assert details is None
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_search_respects_settings_num_results(self, mock_post, serper_service):
        """Test that search respects settings for number of results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"videos": []}
        mock_post.return_value = mock_response
        
        # Call without specifying num_results - should use settings default
        serper_service.search_youtube_videos("test")
        
        call_args = mock_post.call_args
        # Should use default from settings (5)
        assert call_args[1]["json"]["num"] == 5
    
    @patch('cv_analyzer.services.serper_service.requests.post')
    def test_search_handles_special_characters_in_query(
        self, 
        mock_post, 
        serper_service, 
        mock_video_response
    ):
        """Test search with special characters in query."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_video_response
        mock_post.return_value = mock_response
        
        query = "Python & Docker: Complete Guide (2024)"
        videos = serper_service.search_youtube_videos(query)
        
        # Should handle special characters without errors
        assert len(videos) > 0
        call_args = mock_post.call_args
        assert call_args[1]["json"]["q"] == query