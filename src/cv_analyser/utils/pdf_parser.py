"""
PDF parsing utilities for extracting text from CV files.
"""

import PyPDF2
from typing import Optional
from io import BytesIO
from loguru import logger


class PDFParseError(Exception):
    """Custom exception for PDF parsing errors."""
    pass


class PDFParser:
    """Handler for PDF text extraction."""
    
    @staticmethod
    def extract_text(pdf_file) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_file: File-like object or BytesIO containing PDF data
            
        Returns:
            str: Extracted text from the PDF
            
        Raises:
            PDFParseError: If PDF cannot be parsed or is empty
        """
        try:
            # Reset file pointer if it's a file-like object
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
            
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check if PDF is encrypted
            if pdf_reader.is_encrypted:
                logger.warning("PDF is encrypted, attempting to decrypt...")
                try:
                    pdf_reader.decrypt('')
                except Exception as e:
                    raise PDFParseError(f"Cannot decrypt PDF: {str(e)}")
            
            # Extract text from all pages
            text_content = []
            total_pages = len(pdf_reader.pages)
            
            logger.info(f"Extracting text from {total_pages} pages...")
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                    logger.debug(f"Extracted page {page_num}/{total_pages}")
                except Exception as e:
                    logger.warning(f"Error extracting page {page_num}: {str(e)}")
                    continue
            
            # Combine all text
            full_text = "\n".join(text_content)
            
            # Validate extracted text
            if not full_text.strip():
                raise PDFParseError("No text could be extracted from PDF")
            
            if len(full_text.strip()) < 50:
                raise PDFParseError("Extracted text is too short, PDF may be image-based")
            
            logger.info(f"Successfully extracted {len(full_text)} characters")
            return full_text.strip()
            
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"PDF read error: {str(e)}")
            raise PDFParseError(f"Invalid PDF file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error parsing PDF: {str(e)}")
            raise PDFParseError(f"Failed to parse PDF: {str(e)}")
    
    @staticmethod
    def validate_pdf(pdf_file) -> bool:
        """
        Validate if file is a readable PDF.
        
        Args:
            pdf_file: File-like object
            
        Returns:
            bool: True if valid PDF, False otherwise
        """
        try:
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
            
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Check basic properties
            if len(pdf_reader.pages) == 0:
                logger.warning("PDF has no pages")
                return False
            
            # Reset pointer after validation
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
            
            return True
            
        except Exception as e:
            logger.error(f"PDF validation failed: {str(e)}")
            return False
    
    @staticmethod
    def get_pdf_metadata(pdf_file) -> dict:
        """
        Extract metadata from PDF.
        
        Args:
            pdf_file: File-like object
            
        Returns:
            dict: PDF metadata
        """
        try:
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
            
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            metadata = pdf_reader.metadata
            
            return {
                'pages': len(pdf_reader.pages),
                'author': metadata.get('/Author', 'Unknown') if metadata else 'Unknown',
                'creator': metadata.get('/Creator', 'Unknown') if metadata else 'Unknown',
                'producer': metadata.get('/Producer', 'Unknown') if metadata else 'Unknown',
                'subject': metadata.get('/Subject', 'Unknown') if metadata else 'Unknown',
                'title': metadata.get('/Title', 'Unknown') if metadata else 'Unknown',
            }
        except Exception as e:
            logger.warning(f"Could not extract metadata: {str(e)}")
            return {}