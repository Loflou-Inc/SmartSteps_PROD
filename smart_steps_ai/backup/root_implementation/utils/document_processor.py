"""
Document processing utilities for the Smart Steps AI module.

This module provides functionality for processing different document formats,
including PDF, TXT, and other text-based formats for use in the
enhanced persona system.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path

class DocumentProcessor:
    """
    Document processor for converting and extracting text from various formats.
    
    This class provides methods to handle different document formats and extract
    their content for use in the knowledge store.
    """
    
    def __init__(self):
        """Initialize the document processor."""
        self.supported_formats = {
            ".txt": self._process_text,
            ".pdf": self._process_pdf,
            ".md": self._process_markdown,
            ".json": self._process_json
        }
    
    def process_document(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process a document file and extract its content and metadata.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Tuple of (content, metadata)
            
        Raises:
            ValueError: If the file format is not supported
            FileNotFoundError: If the file does not exist
        """
        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")
        
        # Get file extension
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()
        
        # Check if format is supported
        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported document format: {extension}")
        
        # Process the document
        return self.supported_formats[extension](file_path)
    
    def _process_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process a plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract basic metadata
            metadata = {
                "format": "text",
                "filename": os.path.basename(file_path),
                "size": os.path.getsize(file_path)
            }
            
            # Try to extract a title from the first line
            lines = content.split('\n')
            if lines and lines[0].strip():
                metadata["title"] = lines[0].strip()
            
            return content, metadata
        
        except UnicodeDecodeError:
            # Try with a different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
            
            metadata = {
                "format": "text",
                "filename": os.path.basename(file_path),
                "size": os.path.getsize(file_path),
                "encoding": "latin-1"
            }
            
            # Try to extract a title from the first line
            lines = content.split('\n')
            if lines and lines[0].strip():
                metadata["title"] = lines[0].strip()
            
            return content, metadata
    
    def _process_markdown(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process a Markdown file."""
        # Markdown is essentially plain text, so we use the same processing
        content, metadata = self._process_text(file_path)
        
        # Update format in metadata
        metadata["format"] = "markdown"
        
        # Try to extract more structured metadata
        lines = content.split('\n')
        
        # Check for frontmatter
        if lines and lines[0].strip() == '---':
            frontmatter_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    frontmatter_end = i
                    break
            
            if frontmatter_end > 0:
                frontmatter_text = '\n'.join(lines[1:frontmatter_end])
                try:
                    frontmatter = {}
                    for line in frontmatter_text.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            frontmatter[key.strip()] = value.strip()
                    
                    # Add frontmatter to metadata
                    metadata["frontmatter"] = frontmatter
                    
                    # Use title from frontmatter if available
                    if "title" in frontmatter:
                        metadata["title"] = frontmatter["title"]
                except Exception:
                    pass
        
        # Extract headings
        headings = []
        for line in lines:
            if line.startswith('#'):
                # Count the number of # characters
                level = 0
                for char in line:
                    if char == '#':
                        level += 1
                    else:
                        break
                
                # Extract the heading text
                heading_text = line[level:].strip()
                headings.append({
                    "level": level,
                    "text": heading_text
                })
        
        if headings:
            metadata["headings"] = headings
            
            # Use first heading as title if no title is set
            if "title" not in metadata and headings:
                metadata["title"] = headings[0]["text"]
        
        return content, metadata
    
    def _process_json(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Process a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert JSON to text
            if isinstance(data, dict):
                # Format as key-value pairs
                content_parts = []
                
                def _format_dict(d, prefix=""):
                    for key, value in d.items():
                        if isinstance(value, dict):
                            _format_dict(value, prefix=f"{prefix}{key}.")
                        elif isinstance(value, list):
                            content_parts.append(f"{prefix}{key}:")
                            for i, item in enumerate(value):
                                if isinstance(item, dict):
                                    _format_dict(item, prefix=f"{prefix}{key}[{i}].")
                                else:
                                    content_parts.append(f"{prefix}{key}[{i}]: {item}")
                        else:
                            content_parts.append(f"{prefix}{key}: {value}")
                
                _format_dict(data)
                content = '\n'.join(content_parts)
            else:
                # Use json.dumps for other types
                content = json.dumps(data, indent=2)
            
            # Extract metadata
            metadata = {
                "format": "json",
                "filename": os.path.basename(file_path),
                "size": os.path.getsize(file_path)
            }
            
            # Use top-level keys as metadata
            if isinstance(data, dict):
                # Use 'title' or 'name' as document title if available
                if "title" in data:
                    metadata["title"] = data["title"]
                elif "name" in data:
                    metadata["title"] = data["name"]
                
                # Extract other common metadata fields
                for meta_field in ["author", "description", "date", "version"]:
                    if meta_field in data:
                        metadata[meta_field] = data[meta_field]
            
            return content, metadata
        
        except json.JSONDecodeError:
            # If the file is not valid JSON, process it as text
            return self._process_text(file_path)
    
    def _process_pdf(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process a PDF file.
        
        Note: This method requires external libraries for PDF processing.
        If they are not available, it will extract text using a fallback method.
        """
        try:
            # Try using PyPDF2
            from PyPDF2 import PdfReader
            
            reader = PdfReader(file_path)
            content_parts = []
            
            # Extract metadata
            metadata = {
                "format": "pdf",
                "filename": os.path.basename(file_path),
                "size": os.path.getsize(file_path),
                "pages": len(reader.pages)
            }
            
            # Extract document info
            info = reader.metadata
            if info:
                if info.title:
                    metadata["title"] = info.title
                if info.author:
                    metadata["author"] = info.author
                if info.subject:
                    metadata["subject"] = info.subject
                if info.creator:
                    metadata["creator"] = info.creator
            
            # Extract text from each page
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    content_parts.append(f"Page {i+1}:\n{page_text}")
            
            # Join all page texts
            content = "\n\n".join(content_parts)
            
            # If no title in metadata, try to extract from first page
            if "title" not in metadata and content_parts:
                first_page = content_parts[0]
                first_lines = first_page.split('\n', 5)
                if len(first_lines) >= 2:
                    # Assume the first non-empty line is the title
                    for line in first_lines:
                        if line.strip() and "Page" not in line:
                            metadata["title"] = line.strip()
                            break
            
            return content, metadata
        
        except ImportError:
            # Try using pdfplumber
            try:
                import pdfplumber
                
                with pdfplumber.open(file_path) as pdf:
                    content_parts = []
                    
                    # Extract metadata
                    metadata = {
                        "format": "pdf",
                        "filename": os.path.basename(file_path),
                        "size": os.path.getsize(file_path),
                        "pages": len(pdf.pages)
                    }
                    
                    # Extract document info
                    if pdf.metadata:
                        if 'Title' in pdf.metadata:
                            metadata["title"] = pdf.metadata['Title']
                        if 'Author' in pdf.metadata:
                            metadata["author"] = pdf.metadata['Author']
                        if 'Subject' in pdf.metadata:
                            metadata["subject"] = pdf.metadata['Subject']
                        if 'Creator' in pdf.metadata:
                            metadata["creator"] = pdf.metadata['Creator']
                    
                    # Extract text from each page
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            content_parts.append(f"Page {i+1}:\n{page_text}")
                    
                    # Join all page texts
                    content = "\n\n".join(content_parts)
                    
                    # If no title in metadata, try to extract from first page
                    if "title" not in metadata and content_parts:
                        first_page = content_parts[0]
                        first_lines = first_page.split('\n', 5)
                        if len(first_lines) >= 2:
                            # Assume the first non-empty line is the title
                            for line in first_lines:
                                if line.strip() and "Page" not in line:
                                    metadata["title"] = line.strip()
                                    break
                    
                    return content, metadata
            
            except ImportError:
                # If both PDF libraries are unavailable, use a text extraction fallback
                try:
                    # Try using textract as a fallback
                    import textract
                    text = textract.process(file_path, encoding='utf-8').decode('utf-8')
                    
                    metadata = {
                        "format": "pdf",
                        "filename": os.path.basename(file_path),
                        "size": os.path.getsize(file_path),
                        "extraction_method": "textract"
                    }
                    
                    # Try to extract a title from the first line
                    lines = text.split('\n')
                    if lines and lines[0].strip():
                        metadata["title"] = lines[0].strip()
                    
                    return text, metadata
                
                except ImportError:
                    # If all libraries are unavailable, raise an error
                    raise ImportError(
                        "PDF processing requires one of the following libraries: "
                        "PyPDF2, pdfplumber, or textract. "
                        "Please install one of these libraries to process PDF files."
                    )
                
                except Exception as e:
                    # If textract fails, return an error message as content
                    content = f"Failed to extract text from PDF: {str(e)}"
                    metadata = {
                        "format": "pdf",
                        "filename": os.path.basename(file_path),
                        "size": os.path.getsize(file_path),
                        "error": str(e)
                    }
                    
                    return content, metadata
        
        except Exception as e:
            # If PDF processing fails, return an error message as content
            content = f"Failed to extract text from PDF: {str(e)}"
            metadata = {
                "format": "pdf",
                "filename": os.path.basename(file_path),
                "size": os.path.getsize(file_path),
                "error": str(e)
            }
            
            return content, metadata
    
    def extract_citations(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract citations from document content.
        
        Args:
            content: Document content
            
        Returns:
            List of citation dictionaries
        """
        citations = []
        
        # Match numbered citations like [1], [2], etc.
        numbered_pattern = r'\[(\d+)\]'
        for match in re.finditer(numbered_pattern, content):
            citation_number = match.group(1)
            
            # Try to find the citation text in reference section
            reference_pattern = rf'\[{citation_number}\] (.*?)(?:\[|$)'
            reference_match = re.search(reference_pattern, content)
            
            if reference_match:
                citation_text = reference_match.group(1).strip()
                citations.append({
                    "id": f"citation-{citation_number}",
                    "number": citation_number,
                    "text": citation_text
                })
            else:
                # Just store the citation number
                citations.append({
                    "id": f"citation-{citation_number}",
                    "number": citation_number,
                    "text": f"Citation {citation_number}"
                })
        
        # Match author-year citations like (Smith, 2020)
        author_year_pattern = r'\(([A-Za-z\s]+),\s*(\d{4})\)'
        for match in re.finditer(author_year_pattern, content):
            author = match.group(1)
            year = match.group(2)
            
            # Create citation ID
            citation_id = f"citation-{author.lower().replace(' ', '-')}-{year}"
            
            # Check if this citation is already in the list
            if not any(c["id"] == citation_id for c in citations):
                citations.append({
                    "id": citation_id,
                    "author": author,
                    "year": year,
                    "text": f"{author} ({year})"
                })
        
        return citations

    def generate_document_id(self, file_path: str, content: str = None, metadata: Dict = None) -> str:
        """
        Generate a unique ID for a document based on its path and content.
        
        Args:
            file_path: Path to the document file
            content: Document content (optional)
            metadata: Document metadata (optional)
            
        Returns:
            Document ID string
        """
        # Start with the base filename
        base_name = os.path.basename(file_path)
        file_name, _ = os.path.splitext(base_name)
        
        # Clean up the filename to create a valid ID
        doc_id = file_name.lower()
        doc_id = re.sub(r'[^\w\s-]', '', doc_id)  # Remove special characters
        doc_id = re.sub(r'\s+', '_', doc_id)  # Replace spaces with underscores
        
        return doc_id


class PdfProcessor:
    """
    PDF-specific processor with advanced features.
    
    This class provides methods for extracting text, tables, and images
    from PDF documents, with more advanced options than the basic
    DocumentProcessor.
    """
    
    def __init__(self):
        """Initialize the PDF processor."""
        pass
    
    def extract_text(self, file_path: str, pages: Optional[List[int]] = None) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            pages: List of page numbers to extract (0-based, optional)
            
        Returns:
            Extracted text
            
        Raises:
            ImportError: If required libraries are not available
            FileNotFoundError: If the file does not exist
        """
        try:
            # Try using PyPDF2
            from PyPDF2 import PdfReader
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            reader = PdfReader(file_path)
            content_parts = []
            
            # Determine pages to extract
            if pages is None:
                pages = range(len(reader.pages))
            else:
                # Filter out invalid page numbers
                pages = [p for p in pages if 0 <= p < len(reader.pages)]
            
            # Extract text from each page
            for i in pages:
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    content_parts.append(text)
            
            return "\n\n".join(content_parts)
        
        except ImportError:
            # Try using pdfplumber
            try:
                import pdfplumber
                
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"PDF file not found: {file_path}")
                
                with pdfplumber.open(file_path) as pdf:
                    content_parts = []
                    
                    # Determine pages to extract
                    if pages is None:
                        pages = range(len(pdf.pages))
                    else:
                        # Filter out invalid page numbers
                        pages = [p for p in pages if 0 <= p < len(pdf.pages)]
                    
                    # Extract text from each page
                    for i in pages:
                        page = pdf.pages[i]
                        text = page.extract_text()
                        if text:
                            content_parts.append(text)
                    
                    return "\n\n".join(content_parts)
            
            except ImportError:
                # If both libraries are unavailable, raise an error
                raise ImportError(
                    "PDF processing requires either PyPDF2 or pdfplumber. "
                    "Please install one of these libraries to process PDF files."
                )
    
    def extract_tables(self, file_path: str, pages: Optional[List[int]] = None) -> List[Dict]:
        """
        Extract tables from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            pages: List of page numbers to extract (0-based, optional)
            
        Returns:
            List of extracted tables as dictionaries
            
        Raises:
            ImportError: If required libraries are not available
            FileNotFoundError: If the file does not exist
        """
        try:
            import pdfplumber
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            with pdfplumber.open(file_path) as pdf:
                tables = []
                
                # Determine pages to extract
                if pages is None:
                    pages = range(len(pdf.pages))
                else:
                    # Filter out invalid page numbers
                    pages = [p for p in pages if 0 <= p < len(pdf.pages)]
                
                # Extract tables from each page
                for i in pages:
                    page = pdf.pages[i]
                    page_tables = page.extract_tables()
                    
                    for j, table_data in enumerate(page_tables):
                        # Convert table to dictionary format
                        if table_data:
                            headers = table_data[0]
                            rows = table_data[1:]
                            
                            processed_table = {
                                "page": i,
                                "index": j,
                                "headers": headers,
                                "rows": rows
                            }
                            
                            tables.append(processed_table)
                
                return tables
        
        except ImportError:
            # If pdfplumber is not available, raise an error
            raise ImportError(
                "Table extraction requires pdfplumber. "
                "Please install pdfplumber to extract tables from PDF files."
            )
    
    def get_structure(self, file_path: str) -> Dict:
        """
        Get the structure of a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with PDF structure information
            
        Raises:
            ImportError: If required libraries are not available
            FileNotFoundError: If the file does not exist
        """
        try:
            # Try using PyPDF2
            from PyPDF2 import PdfReader
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            reader = PdfReader(file_path)
            
            # Extract document info
            info = reader.metadata
            metadata = {}
            
            if info:
                if info.title:
                    metadata["title"] = info.title
                if info.author:
                    metadata["author"] = info.author
                if info.subject:
                    metadata["subject"] = info.subject
                if info.creator:
                    metadata["creator"] = info.creator
                if info.producer:
                    metadata["producer"] = info.producer
            
            # Get page information
            pages = []
            for i, page in enumerate(reader.pages):
                page_info = {
                    "page_number": i + 1,
                    "rotation": page.get('/Rotate', 0),
                    "size": {
                        "width": float(page.mediabox.width),
                        "height": float(page.mediabox.height)
                    }
                }
                
                # Check if page has text
                text = page.extract_text()
                page_info["has_text"] = bool(text)
                if text:
                    # Count approximate words
                    words = re.findall(r'\b\w+\b', text)
                    page_info["word_count"] = len(words)
                
                pages.append(page_info)
            
            # Get outline (bookmarks)
            outlines = []
            
            # Some PDFs don't have outlines
            if hasattr(reader, 'outline') and reader.outline:
                def process_outline_item(item, level=0):
                    if isinstance(item, list):
                        items = []
                        for subitem in item:
                            items.extend(process_outline_item(subitem, level))
                        return items
                    elif isinstance(item, dict):
                        processed = {
                            "title": item.get('/Title', 'Unknown'),
                            "level": level
                        }
                        if '/Next' in item:
                            return [processed] + process_outline_item(item['/Next'], level)
                        return [processed]
                    else:
                        return []
                
                outlines = process_outline_item(reader.outline)
            
            # Build the structure
            structure = {
                "metadata": metadata,
                "pages": len(pages),
                "page_info": pages,
                "outlines": outlines
            }
            
            return structure
        
        except ImportError:
            # Try using pdfplumber
            try:
                import pdfplumber
                
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"PDF file not found: {file_path}")
                
                with pdfplumber.open(file_path) as pdf:
                    # Extract document info
                    metadata = {}
                    if pdf.metadata:
                        for key, value in pdf.metadata.items():
                            if value:
                                metadata[key] = value
                    
                    # Get page information
                    pages = []
                    for i, page in enumerate(pdf.pages):
                        page_info = {
                            "page_number": i + 1,
                            "size": {
                                "width": float(page.width),
                                "height": float(page.height)
                            }
                        }
                        
                        # Check if page has text
                        text = page.extract_text()
                        page_info["has_text"] = bool(text)
                        if text:
                            # Count approximate words
                            words = re.findall(r'\b\w+\b', text)
                            page_info["word_count"] = len(words)
                        
                        # Check if page has tables
                        tables = page.extract_tables()
                        page_info["has_tables"] = bool(tables)
                        if tables:
                            page_info["table_count"] = len(tables)
                        
                        pages.append(page_info)
                    
                    # Build the structure
                    structure = {
                        "metadata": metadata,
                        "pages": len(pages),
                        "page_info": pages
                    }
                    
                    return structure
            
            except ImportError:
                # If both libraries are unavailable, raise an error
                raise ImportError(
                    "PDF structure analysis requires either PyPDF2 or pdfplumber. "
                    "Please install one of these libraries to analyze PDF files."
                )


# Example usage
if __name__ == "__main__":
    # Example document processing
    processor = DocumentProcessor()
    
    # Process a text file
    file_path = "example.txt"
    if os.path.exists(file_path):
        content, metadata = processor.process_document(file_path)
        print(f"Text file metadata: {metadata}")
        print(f"Content preview: {content[:100]}...")
    
    # Process a PDF file
    pdf_path = "example.pdf"
    if os.path.exists(pdf_path):
        # Try the PDF processor
        pdf_processor = PdfProcessor()
        try:
            pdf_structure = pdf_processor.get_structure(pdf_path)
            print(f"PDF structure: {pdf_structure}")
        except ImportError:
            print("PDF processor requires PyPDF2 or pdfplumber.")
