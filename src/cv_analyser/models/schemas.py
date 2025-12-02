"""
Data models and schemas for CV Job Analyzer.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional


class CVAnalysis(BaseModel):
    """Analysis result from CV vs Job Description comparison."""
    
    overall_score: int = Field(..., ge=0, le=100, description="Overall match score between 0-100")
    skills_match: int = Field(..., ge=0, le=100, description="Skills match score")
    experience_match: int = Field(..., ge=0, le=100, description="Experience match score")
    education_match: int = Field(..., ge=0, le=100, description="Education match score")
    strengths: List[str] = Field(default_factory=list, description="Matching/strong skills")
    missing_skills: List[str] = Field(default_factory=list, description="Missing/weak skills")
    gaps_analysis: str = Field(default="No analysis available", description="Skill gap analysis summary")
    youtube_search_query: str = Field(default="", description="YouTube search query")
    
    @validator('overall_score', 'skills_match', 'experience_match', 'education_match')
    def validate_score(cls, v):
        """Ensure scores are within valid range."""
        if not 0 <= v <= 100:
            raise ValueError('Score must be between 0 and 100')
        return v
    
    @validator('strengths', 'missing_skills')
    def validate_lists_minimum(cls, v):
        """Ensure lists have at least one item or provide default."""
        if not v:
            return ["Not specified"]
        return v
    
    @validator('gaps_analysis')
    def validate_gaps_analysis(cls, v):
        """Ensure gaps analysis has content."""
        if not v or len(v) < 10:
            return "Analysis not available. Please review the strengths and missing skills above."
        return v
    
    @validator('youtube_search_query')
    def validate_youtube_query(cls, v):
        """Ensure YouTube query has content."""
        if not v or len(v) < 3:
            return "skill improvement tutorial"
        return v


class YouTubeVideo(BaseModel):
    """YouTube video information."""
    
    title: str = Field(..., description="Video title")
    link: str = Field(..., description="Video URL")
    channel: str = Field(..., description="Channel name")
    duration: str = Field(default="N/A", description="Video duration")
    thumbnail: Optional[str] = Field(default=None, description="Thumbnail URL")
    
    @validator('link')
    def validate_youtube_link(cls, v):
        """Ensure link is a valid YouTube URL."""
        if v and not any(domain in v for domain in ['youtube.com', 'youtu.be']):
            raise ValueError('Invalid YouTube URL')
        return v


class AnalysisRequest(BaseModel):
    """Request model for CV analysis."""
    
    cv_text: str = Field(..., min_length=50, description="Extracted CV text")
    job_description: str = Field(..., min_length=50, description="Job description text")
    
    @validator('cv_text', 'job_description')
    def validate_text_content(cls, v):
        """Ensure text has meaningful content."""
        if len(v.strip()) < 50:
            raise ValueError('Text must be at least 50 characters')
        return v.strip()


class AnalysisResponse(BaseModel):
    """Complete response with analysis and video recommendations."""
    
    analysis: CVAnalysis
    videos: List[YouTubeVideo] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "analysis": {
                    "overall_score": 75,
                    "strengths": ["Python programming", "Machine Learning"],
                    "missing_skills": ["Docker", "Kubernetes"],
                    "gaps_analysis": "Candidate shows strong technical foundation...",
                    "youtube_search_query": "Docker Kubernetes tutorial for beginners"
                },
                "videos": [
                    {
                        "title": "Docker Tutorial for Beginners",
                        "link": "https://youtube.com/watch?v=example",
                        "channel": "TechChannel",
                        "duration": "15:30",
                        "thumbnail": "https://img.youtube.com/vi/example/0.jpg"
                    }
                ]
            }
        }