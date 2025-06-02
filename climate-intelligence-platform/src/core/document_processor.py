"""Advanced document processing for RAG system"""

import os
import logging
import hashlib
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import re

try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = None
    np = None

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
except ImportError:
    RecursiveCharacterTextSplitter = None
    Document = None

try:
    import pypdf
    from pypdf import PdfReader
except ImportError:
    pypdf = None
    PdfReader = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

import markdown

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Advanced document processor with multiple format support"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if RecursiveCharacterTextSplitter:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
        else:
            self.text_splitter = None
            logger.warning("LangChain not available, using basic text splitting")
    
    def process_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Process a file and return chunks with metadata"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract text based on file type
        text = self._extract_text(file_path)
        
        if not text.strip():
            logger.warning(f"No text extracted from {file_path}")
            return []
        
        # Create chunks
        chunks = self._create_chunks(text, file_path)
        
        logger.info(f"Processed {file_path}: {len(chunks)} chunks created")
        return chunks
    
    def process_text(self, text: str, source: str = "text_input") -> List[Dict[str, Any]]:
        """Process raw text and return chunks"""
        if not text.strip():
            return []
        
        chunks = self._create_chunks(text, source)
        logger.info(f"Processed text input: {len(chunks)} chunks created")
        return chunks
    
    def process_readme(self, readme_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Specialized processing for README files"""
        readme_path = Path(readme_path)
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse markdown structure
        sections = self._parse_markdown_sections(content)
        
        chunks = []
        for section in sections:
            section_chunks = self._create_chunks(
                section['content'], 
                readme_path,
                additional_metadata={
                    'section_title': section['title'],
                    'section_level': section['level'],
                    'section_type': section['type']
                }
            )
            chunks.extend(section_chunks)
        
        logger.info(f"Processed README {readme_path}: {len(chunks)} chunks created")
        return chunks
    
    def _extract_text(self, file_path: Path) -> str:
        """Extract text from various file formats"""
        suffix = file_path.suffix.lower()
        
        try:
            if suffix == '.txt':
                return self._extract_from_txt(file_path)
            elif suffix == '.md':
                return self._extract_from_markdown(file_path)
            elif suffix == '.pdf':
                return self._extract_from_pdf(file_path)
            elif suffix in ['.docx', '.doc']:
                return self._extract_from_docx(file_path)
            elif suffix == '.html':
                return self._extract_from_html(file_path)
            elif suffix in ['.csv', '.xlsx']:
                return self._extract_from_spreadsheet(file_path)
            else:
                # Try as plain text
                return self._extract_from_txt(file_path)
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def _extract_from_txt(self, file_path: Path) -> str:
        """Extract text from plain text file"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _extract_from_markdown(self, file_path: Path) -> str:
        """Extract text from markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML then extract text
        html = markdown.markdown(md_content)
        if BeautifulSoup:
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
        else:
            # Basic markdown processing
            return re.sub(r'[#*`_\[\]()]', '', md_content)
    
    def _extract_from_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file"""
        if not PdfReader:
            logger.error("pypdf not available for PDF processing")
            return ""
        
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return ""
    
    def _extract_from_docx(self, file_path: Path) -> str:
        """Extract text from DOCX file"""
        if not DocxDocument:
            logger.error("python-docx not available for DOCX processing")
            return ""
        
        try:
            doc = DocxDocument(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {e}")
            return ""
    
    def _extract_from_html(self, file_path: Path) -> str:
        """Extract text from HTML file"""
        if not BeautifulSoup:
            logger.error("BeautifulSoup not available for HTML processing")
            return ""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
        except Exception as e:
            logger.error(f"Error reading HTML {file_path}: {e}")
            return ""
    
    def _extract_from_spreadsheet(self, file_path: Path) -> str:
        """Extract text from CSV/Excel files"""
        if not pd:
            logger.error("pandas not available for spreadsheet processing")
            return ""
        
        try:
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Convert dataframe to text representation
            return df.to_string()
        except Exception as e:
            logger.error(f"Error reading spreadsheet {file_path}: {e}")
            return ""
    
    def _create_chunks(
        self, 
        text: str, 
        source: Union[str, Path],
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Create chunks from text with metadata"""
        
        if self.text_splitter and Document:
            # Use LangChain text splitter
            docs = self.text_splitter.create_documents([text])
            chunks = []
            
            for i, doc in enumerate(docs):
                metadata = {
                    'source': str(source),
                    'chunk_id': i,
                    'chunk_size': len(doc.page_content),
                    'file_hash': self._get_file_hash(str(source)),
                }
                
                if additional_metadata:
                    metadata.update(additional_metadata)
                
                chunks.append({
                    'content': doc.page_content,
                    'metadata': metadata
                })
        else:
            # Basic text splitting
            chunks = []
            words = text.split()
            
            for i in range(0, len(words), self.chunk_size):
                chunk_words = words[i:i + self.chunk_size]
                chunk_content = ' '.join(chunk_words)
                
                metadata = {
                    'source': str(source),
                    'chunk_id': i // self.chunk_size,
                    'chunk_size': len(chunk_content),
                    'file_hash': self._get_file_hash(str(source)),
                }
                
                if additional_metadata:
                    metadata.update(additional_metadata)
                
                chunks.append({
                    'content': chunk_content,
                    'metadata': metadata
                })
        
        return chunks
    
    def _parse_markdown_sections(self, content: str) -> List[Dict[str, Any]]:
        """Parse markdown content into sections"""
        sections = []
        lines = content.split('\n')
        current_section = {'title': 'Introduction', 'level': 0, 'content': '', 'type': 'content'}
        
        for line in lines:
            # Check for headers
            if line.startswith('#'):
                # Save previous section
                if current_section['content'].strip():
                    sections.append(current_section.copy())
                
                # Start new section
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                
                current_section = {
                    'title': title,
                    'level': level,
                    'content': '',
                    'type': self._classify_section_type(title)
                }
            else:
                current_section['content'] += line + '\n'
        
        # Add final section
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _classify_section_type(self, title: str) -> str:
        """Classify section type based on title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['install', 'setup', 'getting started']):
            return 'installation'
        elif any(word in title_lower for word in ['usage', 'example', 'tutorial']):
            return 'usage'
        elif any(word in title_lower for word in ['api', 'reference', 'documentation']):
            return 'reference'
        elif any(word in title_lower for word in ['feature', 'capability', 'functionality']):
            return 'features'
        elif any(word in title_lower for word in ['architecture', 'design', 'structure']):
            return 'architecture'
        else:
            return 'content'
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate hash for file identification"""
        return hashlib.md5(file_path.encode()).hexdigest()[:8]
    
    def get_processing_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed chunks"""
        if not chunks:
            return {}
        
        total_chunks = len(chunks)
        total_chars = sum(len(chunk['content']) for chunk in chunks)
        avg_chunk_size = total_chars / total_chunks if total_chunks > 0 else 0
        
        # Section type distribution
        section_types = {}
        for chunk in chunks:
            section_type = chunk['metadata'].get('section_type', 'unknown')
            section_types[section_type] = section_types.get(section_type, 0) + 1
        
        return {
            'total_chunks': total_chunks,
            'total_characters': total_chars,
            'average_chunk_size': avg_chunk_size,
            'section_type_distribution': section_types,
            'sources': list(set(chunk['metadata']['source'] for chunk in chunks))
        }