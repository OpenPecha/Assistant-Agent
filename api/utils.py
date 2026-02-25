import logging
import os
from typing import List, Optional, Union
from io import BytesIO
import hashlib
from pypdf import PdfReader
from docx import Document
from api.Assistant.assistant_response_model import ContextRequest
from api.config import get, get_int


class Utils:
    ALLOWED_FILE_EXTENSIONS = get("ALLOWED_EXTENSIONS")
    MAX_FILE_SIZE_MB = get_int("MAX_FILE_SIZE_MB")
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

    @staticmethod
    def generate_hash_key(payload: List[Union[str, int]]) -> str:
        params_str = "".join(str(param) for param in payload)
        hash_value = hashlib.sha256(params_str.encode()).hexdigest()
        return hash_value

    @staticmethod
    def extract_text_from_pdf(pdf_bytes: BytesIO) -> str:
        try:
            reader = PdfReader(pdf_bytes)
            pages = []

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pages.append(page_text.strip())

            return "\n\n".join(pages).strip()
        except Exception as e:
            logging.error(f"Failed to extract text from PDF: {e}")
            raise

    @staticmethod
    def extract_text_from_txt(file_bytes: BytesIO) -> str:
        try:
            return file_bytes.read().decode('utf-8')
        except Exception as e:
            logging.error(f"Failed to read text file: {e}")
            raise

    @staticmethod
    def extract_text_from_docx(file_bytes: BytesIO) -> str:
        try:
            doc = Document(file_bytes)
            paragraphs = []
            
            for para in doc.paragraphs:
                para_text = para.text.strip()
                if para_text:
                    paragraphs.append(para_text)
            
            return "\n\n".join(paragraphs).strip()
        except Exception as e:
            logging.error(f"Failed to extract text from DOCX: {e}")
            raise

    @staticmethod
    def validate_file(filename: str, file_size: int) -> None:
        ext = os.path.splitext(filename.lower())[1]
        if ext not in Utils.ALLOWED_FILE_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}. Allowed types: {', '.join(Utils.ALLOWED_FILE_EXTENSIONS)}")
        
        if file_size > Utils.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File size exceeds {Utils.MAX_FILE_SIZE_MB}MB limit")

    @staticmethod
    def extract_content_from_file(file_bytes: bytes, filename: str) -> str:
        file_stream = BytesIO(file_bytes)
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return Utils.extract_text_from_pdf(file_stream)
        elif filename_lower.endswith(('.txt', '.text')):
            return Utils.extract_text_from_txt(file_stream)
        elif filename_lower.endswith('.docx'):
            return Utils.extract_text_from_docx(file_stream)
        else:
            raise ValueError(f"Unsupported file type: {filename}")

    @staticmethod
    def process_contexts(contexts: List[ContextRequest]) -> Optional[List[str]]:
        if not contexts:
            return None
        
        processed_contexts = []
        
        for idx, ctx in enumerate(contexts, 1):
            try:
                if ctx.content:
                    processed_contexts.append(ctx.content)
                
                elif ctx.pecha_title and ctx.pecha_text_id:
                    pecha_context = f"[Pecha: {ctx.pecha_title}, ID: {ctx.pecha_text_id}]"
                    processed_contexts.append(pecha_context)
                
                else:
                    logging.warning(f"Empty context #{idx}, skipping")
                    
            except Exception as e:
                error_msg = f"Failed to process context #{idx}: {str(e)}"
                logging.error(error_msg)
        
        if not processed_contexts:
            return None    
        return processed_contexts