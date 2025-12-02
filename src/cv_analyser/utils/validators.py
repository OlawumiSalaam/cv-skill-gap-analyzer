"""
Validation utilities for input data.
"""

from typing import Optional, Tuple
from loguru import logger


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class Validators:
    """Collection of validation methods."""
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 50, max_length: int = 50000) -> Tuple[bool, Optional[str]]:
        """
        Validate text length.
        
        Args:
            text: Text to validate
            min_length: Minimum required length
            max_length: Maximum allowed length
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "Text cannot be empty"
        
        text_len = len(text.strip())
        
        if text_len < min_length:
            return False, f"Text too short (minimum {min_length} characters, got {text_len})"
        
        if text_len > max_length:
            return False, f"Text too long (maximum {max_length} characters, got {text_len})"
        
        return True, None
    
    @staticmethod
    def validate_api_key(api_key: str, key_name: str = "API Key") -> Tuple[bool, Optional[str]]:
        """
        Validate API key format.
        
        Args:
            api_key: API key to validate
            key_name: Name of the key (for error messages)
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not api_key or not api_key.strip():
            return False, f"{key_name} cannot be empty"
        
        # Basic validation - keys should be alphanumeric with some special chars
        if len(api_key.strip()) < 10:
            return False, f"{key_name} appears too short"
        
        # Check for placeholder values
        placeholder_values = ['your_api_key', 'api_key_here', 'xxx', 'test']
        if any(placeholder in api_key.lower() for placeholder in placeholder_values):
            return False, f"{key_name} appears to be a placeholder"
        
        return True, None
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 10) -> Tuple[bool, Optional[str]]:
        """
        Validate file size.
        
        Args:
            file_size: File size in bytes
            max_size_mb: Maximum allowed size in MB
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            size_mb = file_size / (1024 * 1024)
            return False, f"File too large ({size_mb:.2f}MB, maximum {max_size_mb}MB)"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None
    
    @staticmethod
    def validate_cv_content(text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate CV content has expected elements.
        
        Args:
            text: CV text to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, warning_message)
        """
        text_lower = text.lower()
        
        # Common CV indicators
        cv_keywords = [
            'experience', 'education', 'skills', 'work', 'university',
            'degree', 'job', 'position', 'project', 'achievement'
        ]
        
        keyword_count = sum(1 for keyword in cv_keywords if keyword in text_lower)
        
        if keyword_count < 2:
            return True, "Warning: This doesn't look like a typical CV. Results may be inaccurate."
        
        return True, None
    
    @staticmethod
    def validate_job_description(text: str) -> Tuple[bool, Optional[str]]:
        """
        Validate job description content.
        
        Args:
            text: Job description to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, warning_message)
        """
        text_lower = text.lower()
        
        # Common job description indicators
        jd_keywords = [
            'requirements', 'responsibilities', 'qualifications', 'experience',
            'skills', 'required', 'preferred', 'must have', 'looking for'
        ]
        
        keyword_count = sum(1 for keyword in jd_keywords if keyword in text_lower)
        
        if keyword_count < 2:
            return True, "Warning: This doesn't look like a typical job description. Results may be inaccurate."
        
        return True, None
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Clean and sanitize text input.
        
        Args:
            text: Text to sanitize
            
        Returns:
            str: Sanitized text
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limit consecutive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        return text.strip()