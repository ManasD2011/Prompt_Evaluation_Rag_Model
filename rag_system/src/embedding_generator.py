"""
Embedding Generation Module
Converts text data to embeddings using sentence-transformers
"""
import json
import numpy as np
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import torch
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config.config import (
    EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION, BATCH_SIZE_EMBEDDINGS,
    EMBEDDINGS_DIR, LOGS_DIR, TEXT_COLUMNS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "embeddings.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for text data"""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME, use_gpu: bool = True):
        """
        Initialize embedding generator
        
        Args:
            model_name: Sentence-transformers model name
            use_gpu: Use GPU if available
        """
        logger.info(f"Initializing embedding model: {model_name}")
        logger.info(f"GPU available: {torch.cuda.is_available()}")
        
        self.device = "cuda" if (use_gpu and torch.cuda.is_available()) else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)
        self.embedding_dim = EMBEDDING_DIMENSION
        self.embeddings = []
        self.texts = []
        
        logger.info(f"[OK] Model loaded on device: {self.device}")
        logger.info(f"[OK] Embedding dimension: {self.embedding_dim}")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if not isinstance(text, str) or len(text.strip()) == 0:
            return np.zeros(self.embedding_dim, dtype=np.float32)
        
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)
    
    def generate_embeddings_batch(self, texts: List[str], 
                                  batch_size: int = BATCH_SIZE_EMBEDDINGS,
                                  show_progress: bool = True) -> np.ndarray:
        """
        Generate embeddings for batch of texts
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            show_progress: Show progress bar
            
        Returns:
            Array of embeddings (N, embedding_dim)
        """
        logger.info(f"Generating embeddings for {len(texts)} texts")
        logger.info(f"Batch size: {batch_size}")

        if not texts:
            empty = np.empty((0, self.embedding_dim), dtype=np.float32)
            self.embeddings = empty
            self.texts = texts
            logger.warning("No texts provided for embedding generation.")
            return empty
        
        embeddings = []
        
        # Use tqdm for progress bar
        iterator = tqdm(range(0, len(texts), batch_size), 
                       desc="Generating embeddings") if show_progress else range(0, len(texts), batch_size)
        
        for i in iterator:
            batch_texts = texts[i:i+batch_size]
            batch_embeddings = self.model.encode(batch_texts, convert_to_numpy=True)
            embeddings.extend(batch_embeddings)
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        logger.info(f"[OK] Generated embeddings shape: {embeddings_array.shape}")
        
        self.embeddings = embeddings_array
        self.texts = texts
        
        return embeddings_array
    
    def save_embeddings(self, output_path: Optional[str] = None) -> str:
        """
        Save embeddings to file
        
        Args:
            output_path: Path to save embeddings
            
        Returns:
            Path to saved file
        """
        if output_path is None:
            output_path = EMBEDDINGS_DIR / "embeddings.npy"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        np.save(output_path, self.embeddings)
        logger.info(f"[OK] Saved embeddings to: {output_path}")
        
        return str(output_path)
    
    def load_embeddings(self, input_path: str) -> np.ndarray:
        """
        Load embeddings from file
        
        Args:
            input_path: Path to embeddings file
            
        Returns:
            Embeddings array
        """
        embeddings = np.load(input_path)
        self.embeddings = embeddings
        logger.info(f"[OK] Loaded embeddings shape: {embeddings.shape}")
        
        return embeddings
    
    def get_similarity_score(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        emb1 = self.generate_embedding(text1)
        emb2 = self.generate_embedding(text2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-8)
        
        return float(similarity)
    
    def find_similar_texts(self, query_text: str, texts: List[str], 
                          top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find most similar texts to query
        
        Args:
            query_text: Query text
            texts: List of candidate texts
            top_k: Number of top results
            
        Returns:
            List of (text, similarity_score) tuples
        """
        query_embedding = self.generate_embedding(query_text)
        
        # Generate embeddings for all texts if not already done
        if len(self.embeddings) == 0:
            text_embeddings = self.generate_embeddings_batch(texts, show_progress=False)
        else:
            text_embeddings = self.embeddings
        
        # Calculate similarities
        similarities = []
        for text_emb in text_embeddings:
            similarity = np.dot(query_embedding, text_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(text_emb) + 1e-8
            )
            similarities.append(float(similarity))
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = [(texts[idx], similarities[idx]) for idx in top_indices]
        
        return results
    
    def save_metadata(self, output_path: Optional[str] = None) -> None:
        """Save metadata about embeddings"""
        if output_path is None:
            output_path = EMBEDDINGS_DIR / "embeddings_metadata.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        metadata = {
            "model_name": EMBEDDING_MODEL_NAME,
            "embedding_dimension": self.embedding_dim,
            "num_embeddings": len(self.embeddings),
            "device": self.device,
            "batch_size": BATCH_SIZE_EMBEDDINGS
        }
        
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"[OK] Saved embeddings metadata to: {output_path}")


def generate_embeddings_from_data(texts: List[str], 
                                 output_dir: Optional[str] = None) -> Tuple[np.ndarray, str]:
    """
    Complete embedding generation pipeline
    
    Args:
        texts: List of texts to embed
        output_dir: Directory to save embeddings
        
    Returns:
        Tuple of (embeddings array, embeddings file path)
    """
    if output_dir is None:
        output_dir = str(EMBEDDINGS_DIR)
    
    generator = EmbeddingGenerator()
    embeddings = generator.generate_embeddings_batch(texts)
    embeddings_path = generator.save_embeddings(Path(output_dir) / "embeddings.npy")
    generator.save_metadata(Path(output_dir) / "embeddings_metadata.json")
    
    return embeddings, embeddings_path


if __name__ == "__main__":
    logger.info("Embedding Generator Module Ready")

