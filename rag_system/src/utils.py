"""
Utility functions for RAG System
Common helper functions used across modules
"""
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


def ensure_directory_exists(directory: Path) -> Path:
    """
    Ensure a directory exists, create if it doesn't
    
    Args:
        directory: Path to directory
        
    Returns:
        Path object
    """
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_json(data: Dict[str, Any], file_path: Path) -> None:
    """
    Save data to JSON file
    
    Args:
        data: Dictionary to save
        file_path: Output file path
    """
    try:
        ensure_directory_exists(file_path.parent)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save JSON: {str(e)}")
        raise


def load_json(file_path: Path) -> Dict[str, Any]:
    """
    Load data from JSON file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary from JSON file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logger.error(f"Failed to load JSON: {str(e)}")
        raise


def save_embeddings(embeddings: np.ndarray, file_path: Path) -> None:
    """
    Save embeddings to numpy file
    
    Args:
        embeddings: Embedding array
        file_path: Output file path
    """
    try:
        ensure_directory_exists(file_path.parent)
        np.save(str(file_path), embeddings)
        logger.info(f"Saved embeddings to {file_path} (shape: {embeddings.shape})")
    except Exception as e:
        logger.error(f"Failed to save embeddings: {str(e)}")
        raise


def load_embeddings(file_path: Path) -> np.ndarray:
    """
    Load embeddings from numpy file
    
    Args:
        file_path: Path to embeddings file
        
    Returns:
        Embedding array
    """
    try:
        embeddings = np.load(str(file_path))
        logger.info(f"Loaded embeddings from {file_path} (shape: {embeddings.shape})")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to load embeddings: {str(e)}")
        raise


def get_timestamp() -> str:
    """Get current timestamp in format YYYYMMDD_HHMMSS"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text for processing
    
    Args:
        text: Text to sanitize
        max_length: Maximum length to truncate to
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text


def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistics for a list of values
    
    Args:
        values: List of numeric values
        
    Returns:
        Dictionary with statistics
    """
    if not values:
        return {"min": 0, "max": 0, "mean": 0, "std": 0}
    
    arr = np.array(values)
    return {
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
    }


def format_bytes(bytes_val: int) -> str:
    """
    Format bytes to human readable format
    
    Args:
        bytes_val: Number of bytes
        
    Returns:
        Formatted string (B, KB, MB, GB)
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"
