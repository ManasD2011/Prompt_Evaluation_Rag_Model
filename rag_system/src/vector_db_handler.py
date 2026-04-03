"""
Vector Database Handler
Using FAISS for efficient similarity search
"""
import json
import numpy as np
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import faiss
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config.config import (
    FAISS_INDEX_PATH, METADATA_PATH, TOP_K_RETRIEVAL,
    SIMILARITY_THRESHOLD, EMBEDDING_DIMENSION, LOGS_DIR
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "vector_db.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FAISSVectorDatabase:
    """FAISS-based vector database for efficient similarity search"""
    
    def __init__(self, embedding_dim: int = EMBEDDING_DIMENSION):
        """
        Initialize FAISS vector database
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedding_dim = embedding_dim
        self.index = None
        self.metadata = []  # Store original texts and metadata
        self.texts = []
        self.ids = []
        
        logger.info(f"Initialized FAISS Vector Database (dim={embedding_dim})")
    
    def create_index(self) -> None:
        """Create FAISS index with L2 distance"""
        # L2 (Euclidean) distance index
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        logger.info("[OK] Created FAISS L2 index")
    
    def create_gpu_index(self) -> None:
        """Create GPU-accelerated FAISS index"""
        try:
            import faiss.contrib.torch_utils
            gpu_index = faiss.index_factory(self.embedding_dim, "Flat", faiss.METRIC_L2)
            gpu_resource = faiss.StandardGpuResources()
            self.index = faiss.index_cpu_to_gpu(gpu_resource, 0, gpu_index)
            logger.info("[OK] Created GPU-accelerated FAISS index")
        except Exception as e:
            logger.warning(f"GPU index creation failed: {str(e)}. Using CPU index.")
            self.create_index()
    
    def add_embeddings(self, embeddings: np.ndarray, 
                      texts: List[str],
                      metadata: Optional[List[Dict]] = None) -> None:
        """
        Add embeddings to index
        
        Args:
            embeddings: Array of embeddings (N, embedding_dim)
            texts: List of original texts
            metadata: List of metadata dicts for each text
        """
        if self.index is None:
            self.create_index()

        if embeddings is None or len(embeddings) == 0:
            raise ValueError("Cannot add empty embeddings to vector index.")

        # Ensure embeddings are float32
        embeddings = embeddings.astype(np.float32)

        if embeddings.ndim != 2:
            raise ValueError(
                f"Embeddings must be 2D (N, D). Got shape {embeddings.shape}."
            )

        if len(texts) != len(embeddings):
            raise ValueError(
                f"Texts count ({len(texts)}) must match embeddings count ({len(embeddings)})."
            )

        if metadata is not None and len(metadata) != len(texts):
            raise ValueError(
                f"Metadata count ({len(metadata)}) must match texts count ({len(texts)})."
            )
        
        logger.info(f"Adding {len(embeddings)} embeddings to index")
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        # Store texts and metadata
        self.texts.extend(texts)
        self.ids.extend(range(len(self.texts) - len(texts), len(self.texts)))
        
        if metadata is None:
            metadata = [{"text": text} for text in texts]
        
        self.metadata.extend(metadata)
        
        logger.info(f"[OK] Total embeddings in index: {self.index.ntotal}")
    
    def search(self, query_embedding: np.ndarray, 
               top_k: int = TOP_K_RETRIEVAL) -> Tuple[List[float], List[str], List[Dict]]:
        """
        Search for similar embeddings
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results
            
        Returns:
            Tuple of (distances, texts, metadata)
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty. No results to retrieve.")
            return [], [], []

        if top_k <= 0:
            logger.warning("top_k must be > 0.")
            return [], [], []
        
        # Ensure query embedding is float32
        query_embedding = query_embedding.reshape(1, -1).astype(np.float32)

        requested_k = min(top_k, self.index.ntotal)

        # Search
        distances, indices = self.index.search(query_embedding, requested_k)

        # Build validated results in case FAISS returns sentinel indices (-1)
        results: List[Tuple[float, str, Dict]] = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.texts):
                continue
            similarity = 1.0 / (1.0 + float(distance))
            result_metadata = self.metadata[idx] if idx < len(self.metadata) else {}
            results.append((similarity, self.texts[idx], result_metadata))

        if not results:
            return [], [], []

        similarities, results_texts, results_metadata = zip(*results)
        return list(similarities), list(results_texts), list(results_metadata)
    
    def search_with_threshold(self, query_embedding: np.ndarray,
                             top_k: int = TOP_K_RETRIEVAL,
                             threshold: float = SIMILARITY_THRESHOLD) -> Tuple[List[float], List[str], List[Dict]]:
        """
        Search with similarity threshold filter
        
        Args:
            query_embedding: Query embedding
            top_k: Number of results
            threshold: Minimum similarity threshold
            
        Returns:
            Filtered results
        """
        similarities, texts, metadata = self.search(query_embedding, top_k)
        
        # Filter by threshold
        filtered_results = [
            (sim, text, meta) for sim, text, meta in zip(similarities, texts, metadata)
            if sim >= threshold
        ]
        
        if not filtered_results:
            logger.warning(f"No results above threshold {threshold}")
            return [], [], []
        
        similarities, texts, metadata = zip(*filtered_results)
        
        return list(similarities), list(texts), list(metadata)
    
    def save_index(self, index_path: Optional[str] = None) -> str:
        """
        Save FAISS index to disk
        
        Args:
            index_path: Path to save index
            
        Returns:
            Path to saved index
        """
        if index_path is None:
            index_path = str(FAISS_INDEX_PATH)
        
        index_path = Path(index_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save index
        faiss.write_index(self.index, str(index_path))
        logger.info(f"[OK] Saved FAISS index to: {index_path}")
        
        # Save metadata
        metadata_path = index_path.parent / "metadata.json"
        metadata_dict = {
            "texts": self.texts,
            "ids": self.ids,
            "metadata": self.metadata,
            "embedding_dim": self.embedding_dim,
            "total_embeddings": self.index.ntotal
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[OK] Saved metadata to: {metadata_path}")
        
        return str(index_path)
    
    def load_index(self, index_path: Optional[str] = None,
                  metadata_path: Optional[str] = None) -> None:
        """
        Load FAISS index from disk
        
        Args:
            index_path: Path to index file
            metadata_path: Path to metadata file
        """
        if index_path is None:
            index_path = str(FAISS_INDEX_PATH)
        if metadata_path is None:
            metadata_path = str(METADATA_PATH)
        
        index_path = Path(index_path)
        metadata_path = Path(metadata_path)
        
        # Load index
        self.index = faiss.read_index(str(index_path))
        logger.info(f"[OK] Loaded FAISS index from: {index_path}")
        logger.info(f"[OK] Index contains {self.index.ntotal} embeddings")
        
        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata_dict = json.load(f)
        
        self.texts = metadata_dict.get("texts", [])
        self.ids = metadata_dict.get("ids", [])
        self.metadata = metadata_dict.get("metadata", [])
        self.embedding_dim = metadata_dict.get("embedding_dim", EMBEDDING_DIMENSION)
        
        logger.info(f"[OK] Loaded metadata with {len(self.texts)} texts")
    
    def reset(self) -> None:
        """Reset the database"""
        self.index = None
        self.metadata = []
        self.texts = []
        self.ids = []
        logger.info("[OK] Vector database reset")
    
    def search_text(self, query_text: str, k: int = TOP_K_RETRIEVAL) -> List[Dict]:
        """
        Search using text query (auto-embeds the query)
        
        Args:
            query_text: Text query
            k: Number of results
            
        Returns:
            List of result dictionaries
        """
        from src.embedding_generator import EmbeddingGenerator
        
        generator = EmbeddingGenerator()
        query_embedding = generator.generate_embedding(query_text)
        
        similarities, texts, metadata = self.search(query_embedding, top_k=k)
        
        results = [
            {"text": text, "similarity": sim, "metadata": meta}
            for text, sim, meta in zip(texts, similarities, metadata)
        ]
        
        return results
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        stats = {
            "total_embeddings": self.index.ntotal if self.index else 0,
            "embedding_dim": self.embedding_dim,
            "num_texts": len(self.texts),
            "num_metadata": len(self.metadata)
        }
        return stats


def initialize_vector_db(embeddings: np.ndarray, 
                        texts: List[str],
                        metadata: Optional[List[Dict]] = None) -> FAISSVectorDatabase:
    """
    Initialize and populate vector database
    
    Args:
        embeddings: Array of embeddings
        texts: List of texts
        metadata: Optional metadata
        
    Returns:
        Initialized database
    """
    db = FAISSVectorDatabase()
    db.add_embeddings(embeddings, texts, metadata)
    db.save_index()
    
    logger.info("[OK] Vector database initialized and saved")
    
    return db


if __name__ == "__main__":
    logger.info("Vector Database Handler Module Ready")

