"""
Tests for Groq API service.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from CV_analyser.services.groq_service import GroqService, GroqAPIError
from CV_analyser.models.schemas import CVAnalysis


class TestGroqService:
    """Test cases for GroqService class."""
    
    @pytest.fixture
    def groq_service(self):
        """Create GroqService instance for testing."""
        return GroqService(api_key="test_groq_key_12345")
    
    @pytest.fixture
    def mock_successful_response(self):
        """Mock successful Groq API response."""
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "overall_score": 75,
                            "strengths": [
                                "Strong Python programming skills",
                                "Experience with Docker and Kubernetes",
                                "AWS cloud deployment knowledge"
                            ],
                            "missing_skills": [
                                "GraphQL API experience",
                                "Go or Rust programming",
                                "Machine learning background"
                            ],
                            "gaps_analysis": "The candidate demonstrates solid backend development skills with strong Python experience and DevOps capabilities. However, there are notable gaps in modern API technologies like GraphQL and additional programming languages that would strengthen the application.",
                            "youtube_search_query": "GraphQL tutorial Python backend development"
                        })
                    }
                }
            ]
        }
    
    def test_initialization_with_api_key(self):
        """Test service initialization with API key."""
        service = GroqService(api_key="test_key")
        assert service.api_key == "test_key"
        assert service.base_url == "https://api.groq.com/openai/v1/chat/completions"
    
    def test_initialization_without_api_key_raises_error(self):
        """Test that initialization without API key raises ValueError."""
        with patch('cv_analyzer.services.groq_service.get_settings') as mock_settings:
            mock_settings.return_value.groq_api_key = None
            with pytest.raises(ValueError, match="Groq API key not provided"):
                GroqService()
    
    def test_build_analysis_prompt(self, groq_service, sample_cv_text, sample_job_description):
        """Test prompt building."""
        prompt = groq_service._build_analysis_prompt(sample_cv_text, sample_job_description)
        
        assert "CV:" in prompt
        assert "Job Description:" in prompt
        assert sample_cv_text in prompt
        assert sample_job_description in prompt
        assert "JSON format" in prompt
        assert "overall_score" in prompt
    
    def test_extract_json_from_response_plain_json(self, groq_service):
        """Test JSON extraction from plain JSON response."""
        content = '{"overall_score": 75, "strengths": ["Python"], "missing_skills": ["Go"], "gaps_analysis": "Test", "youtube_search_query": "test"}'
        result = groq_service._extract_json_from_response(content)
        
        assert result["overall_score"] == 75
        assert "Python" in result["strengths"]
    
    def test_extract_json_from_response_with_markdown(self, groq_service):
        """Test JSON extraction from markdown code blocks."""
        content = '```json\n{"overall_score": 80, "strengths": ["Python"], "missing_skills": ["Go"], "gaps_analysis": "Test", "youtube_search_query": "test"}\n```'
        result = groq_service._extract_json_from_response(content)
        
        assert result["overall_score"] == 80
    
    def test_extract_json_from_response_invalid_json(self, groq_service):
        """Test JSON extraction with invalid JSON."""
        content = "This is not valid JSON"
        
        with pytest.raises(GroqAPIError, match="Invalid JSON response"):
            groq_service._extract_json_from_response(content)
    
    @patch('cv_analyzer.services.groq_service.requests.post')
    def test_analyze_cv_success(
        self, 
        mock_post, 
        groq_service, 
        sample_cv_text, 
        sample_job_description, 
        mock_successful_response
    ):
        """Test successful CV analysis."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_successful_response
        mock_post.return_value = mock_response
        
        # Execute
        result = groq_service.analyze_cv(sample_cv_text, sample_job_description)
        
        # Verify
        assert isinstance(result, CVAnalysis)
        assert result.overall_score == 75
        assert len(result.strengths) == 3
        assert len(result.missing_skills) == 3
        assert "Python" in result.strengths[0]
        assert result.youtube_search_query == "GraphQL tutorial Python backend development"
        
        # Verify API call
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "Bearer test_groq_key_12345" in call_args[1]["headers"]["Authorization"]
    
    @patch('cv_analyzer.services.groq_service.requests.post')
    def test_analyze_cv_api_error(
        self, 
        mock_post, 
        groq_service, 
        sample_cv_text, 
        sample_job_description
    ):
        """Test CV analysis with API error."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {"message": "Invalid API key"}
        }
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response
        
        # Execute and verify
        with pytest.raises(GroqAPIError, match="Groq API error: 401"):
            groq_service.analyze_cv(sample_cv_text, sample_job_description)
    
    @patch('cv_analyzer.services.groq_service.requests.post')
    def test_analyze_cv_timeout(
        self, 
        mock_post, 
        groq_service, 
        sample_cv_text, 
        sample_job_description
    ):
        """Test CV analysis with timeout."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()
        
        with pytest.raises(GroqAPIError, match="Request timed out"):
            groq_service.analyze_cv(sample_cv_text, sample_job_description)
    
    @patch('cv_analyzer.services.groq_service.requests.post')
    def test_analyze_cv_network_error(
        self, 
        mock_post, 
        groq_service, 
        sample_cv_text, 
        sample_job_description
    ):
        """Test CV analysis with network error."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")
        
        with pytest.raises(GroqAPIError, match="Network error"):
            groq_service.analyze_cv(sample_cv_text, sample_job_description)
    
    @patch('cv_analyzer.services.groq_service.requests.post')
    def test_analyze_cv_invalid_json_response(
        self, 
        mock_post, 
        groq_service, 
        sample_cv_text, 
        sample_job_description
    ):
        """Test CV analysis with invalid JSON in response."""
        # Setup mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is not valid JSON"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Execute and verify
        with pytest.raises(GroqAPIError, match="Invalid JSON response"):
            groq_service.analyze_cv(sample_cv_text, sample_job_description)
    
    @patch('cv_analyzer.services.groq_service.requests.post')
    def test_analyze_cv_missing_required_fields(
        self, 
        mock_post, 
        groq_service, 
        sample_cv_text, 
        sample_job_description
    ):
        """Test CV analysis with incomplete data."""
        # Setup mock with missing fields
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "overall_score": 75,
                            "strengths": ["Python"],
                            # Missing required fields
                        })
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Execute and verify - should raise validation error
        with pytest.raises(GroqAPIError):
            groq_service.analyze_cv(sample_cv_text, sample_job_description)
    
    @patch('cv_analyzer.services.groq_service.requests.post')
    def test_test_connection_success(self, mock_post, groq_service):
        """Test successful connection test."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = groq_service.test_connection()
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('cv_analyzer.services.groq_service.requests.post')
    def test_test_connection_failure(self, mock_post, groq_service):
        """Test failed connection test."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response
        
        result = groq_service.test_connection()
        
        assert result is False
    
    @patch('cv_analyzer.services.groq_service.requests.post')
    def test_test_connection_exception(self, mock_post, groq_service):
        """Test connection test with exception."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        result = groq_service.test_connection()
        
        assert result is False
    
    def test_analyze_cv_validates_pydantic_model(
        self, 
        groq_service, 
        sample_cv_text, 
        sample_job_description
    ):
        """Test that analysis result is validated by Pydantic."""
        with patch('cv_analyzer.services.groq_service.requests.post') as mock_post:
            # Setup mock with score out of range
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps({
                                "overall_score": 150,  # Invalid: > 100
                                "strengths": ["Python"],
                                "missing_skills": ["Go"],
                                "gaps_analysis": "Test",
                                "youtube_search_query": "test"
                            })
                        }
                    }
                ]
            }
            mock_post.return_value = mock_response
            
            # Should raise error due to Pydantic validation
            with pytest.raises(GroqAPIError):
                groq_service.analyze_cv(sample_cv_text, sample_job_description)