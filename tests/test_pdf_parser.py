"""
Tests for PDF parser utility.
"""

import pytest
from io import BytesIO
import PyPDF2
from PyPDF2 import PdfWriter, PdfReader

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from CV_analyser.utils.pdf_parser import PDFParser, PDFParseError


class TestPDFParser:
    """Test cases for PDFParser class."""
    
    @pytest.fixture
    def sample_pdf(self):
        """Create a sample PDF for testing."""
        # Create a simple PDF with text
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, "Sample CV Document")
        c.drawString(100, 730, "Name: John Doe")
        c.drawString(100, 710, "Experience: 5 years in Python development")
        c.drawString(100, 690, "Skills: Python, Django, FastAPI, PostgreSQL")
        c.drawString(100, 670, "Education: BS Computer Science")
        c.save()
        
        buffer.seek(0)
        return buffer
    
    def test_extract_text_success(self, sample_pdf):
        """Test successful text extraction from PDF."""
        parser = PDFParser()
        text = parser.extract_text(sample_pdf)
        
        assert text is not None
        assert len(text) > 0
        assert "John Doe" in text
        assert "Python" in text
    
    def test_extract_text_empty_pdf(self):
        """Test extraction from empty PDF."""
        # Create empty PDF
        buffer = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        writer.write(buffer)
        buffer.seek(0)
        
        parser = PDFParser()
        with pytest.raises(PDFParseError, match="No text could be extracted"):
            parser.extract_text(buffer)
    
    def test_validate_pdf_success(self, sample_pdf):
        """Test PDF validation with valid PDF."""
        parser = PDFParser()
        assert parser.validate_pdf(sample_pdf) is True
    
    def test_validate_pdf_invalid(self):
        """Test PDF validation with invalid file."""
        invalid_file = BytesIO(b"This is not a PDF")
        parser = PDFParser()
        assert parser.validate_pdf(invalid_file) is False
    
    def test_get_pdf_metadata(self, sample_pdf):
        """Test metadata extraction."""
        parser = PDFParser()
        metadata = parser.get_pdf_metadata(sample_pdf)
        
        assert isinstance(metadata, dict)
        assert 'pages' in metadata
        assert metadata['pages'] > 0