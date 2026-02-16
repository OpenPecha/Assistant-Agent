import logging
from typing import List, Optional
from io import BytesIO
from pypdf import PdfReader
from api.Assistant.assistant_response_model import ContextRequest
from api.upload.S3_utils import download_file_from_s3
from api.config import get


def extract_text_from_pdf(pdf_bytes: BytesIO) -> str:
    try:
        reader = PdfReader(pdf_bytes)
        text = ""
        
        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text()
            if page_text:
                text += f"\n--- Page {page_num} ---\n{page_text}\n"
        
        return text.strip()
    except Exception as e:
        logging.error(f"Failed to extract text from PDF: {e}")
        raise


def extract_text_from_txt(file_bytes: BytesIO) -> str:
    try:
        return file_bytes.read().decode('utf-8')
    except Exception as e:
        logging.error(f"Failed to read text file: {e}")
        raise


def process_file_context(file_url: str) -> str:
    bucket_name = get("AWS_BUCKET_NAME")
    
    logging.info(f"Processing file context: {file_url}")
    
    file_bytes = download_file_from_s3(bucket_name, file_url)
    
    if file_url.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_bytes)
    elif file_url.lower().endswith(('.txt', '.text')):
        text = extract_text_from_txt(file_bytes)
        
    elif file_url.lower().endswith(('.doc', '.docx')):
        logging.warning(f"Word document support not implemented yet: {file_url}")
        return f"[Word document: {file_url}]"
        
    else:
        raise ValueError(f"Unsupported file type: {file_url}")
    
    logging.info(f"Extracted {len(text)} characters from {file_url}")
    
    return text


def process_contexts(contexts: List[ContextRequest]) -> Optional[List[str]]:
    if not contexts:
        return None
    
    processed_contexts = []
    
    for idx, ctx in enumerate(contexts, 1):
        try:
            if ctx.content:
                processed_contexts.append(ctx.content)
            
            elif ctx.file_url:
                file_text = process_file_context(ctx.file_url)
                processed_contexts.append(file_text)
            
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
    
    logging.info(f"Processed {len(processed_contexts)} contexts")
    
    return processed_contexts
