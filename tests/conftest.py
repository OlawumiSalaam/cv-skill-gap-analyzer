"""
Pytest configuration and shared fixtures.
"""

import pytest
import os
from pathlib import Path


@pytest.fixture
def sample_cv_text():
    """Sample CV text for testing."""
    return """
    John Doe
    Senior Software Engineer
    
    Experience:
    - 5 years of Python development
    - 3 years with Django and FastAPI
    - Experience with PostgreSQL and Redis
    - Cloud deployment on AWS
    
    Skills:
    - Python, JavaScript, TypeScript
    - Django, FastAPI, React
    - PostgreSQL, MongoDB, Redis
    - Docker, Kubernetes
    - AWS, CI/CD
    
    Education:
    - BS Computer Science, MIT, 2018
    """


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return """
    Senior Backend Engineer

    Requirements:
    - 5+ years of backend development experience
    - Strong Python skills required
    - Experience with microservices architecture
    - Knowledge of Docker and Kubernetes
    - Cloud platform experience (AWS, GCP, or Azure)
    - Database design and optimization skills
    
    Nice to have:
    - GraphQL experience
    - Experience with Go or Rust
    - Machine learning background
    """


@pytest.fixture
def mock_groq_response():
    """Mock Groq API response."""
    return {
        "overall_score": 75,
        "strengths": [
            "Strong Python experience with 5 years",
            "Hands-on experience with Docker and Kubernetes",
            "Cloud deployment experience with AWS"
        ],
        "missing_skills": [
            "GraphQL experience",
            "No mention of Go or Rust",
            "Machine learning background not evident"
        ],
        "gaps_analysis": "The candidate has a solid foundation in backend development with strong Python skills and DevOps experience. However, the missing GraphQL and additional language experience could be developed.",
        "youtube_search_query": "GraphQL tutorial Python backend"
    }


@pytest.fixture
def mock_serper_response():
    """Mock Serper API response."""
    return {
        "videos": [
            {
                "title": "GraphQL Tutorial - Complete Course",
                "link": "https://youtube.com/watch?v=example1",
                "channel": "TechChannel",
                "duration": "2:30:00",
                "imageUrl": "https://img.youtube.com/vi/example1/0.jpg"
            },
            {
                "title": "Learn GraphQL with Python",
                "link": "https://youtube.com/watch?v=example2",
                "channel": "CodeMaster",
                "duration": "45:00",
                "imageUrl": "https://img.youtube.com/vi/example2/0.jpg"
            }
        ]
    }


@pytest.fixture
def set_test_env_vars():
    """Set test environment variables."""
    os.environ['GROQ_API_KEY'] = 'test_groq_key_12345'
    os.environ['SERPER_API_KEY'] = 'test_serper_key_12345'
    yield
    # Cleanup
    if 'GROQ_API_KEY' in os.environ:
        del os.environ['GROQ_API_KEY']
    if 'SERPER_API_KEY' in os.environ:
        del os.environ['SERPER_API_KEY']