"""
Unit tests for embedding generation
"""
import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.embedding_generator import EmbeddingGenerator
from config.config import EMBEDDING_DIMENSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestEmbeddingGenerator:
    """Test suite for EmbeddingGenerator"""
    
    def test_single_embedding(self):
        """Test generating single embedding"""
        logger.info("Testing single embedding generation...")
        
        generator = EmbeddingGenerator()
        text = "This is a test document for embedding."
        embedding = generator.generate_embedding(text)
        
        assert embedding.shape == (EMBEDDING_DIMENSION,), \
            f"Expected shape ({EMBEDDING_DIMENSION},), got {embedding.shape}"
        logger.info("[OK] Single embedding test passed")
    
    def test_batch_embedding(self):
        """Test generating batch embeddings"""
        logger.info("Testing batch embedding generation...")
        
        generator = EmbeddingGenerator()
        texts = [
            "First document for testing.",
            "Second document for testing.",
            "Third document for testing.",
        ]
        embeddings = generator.generate_embeddings_batch(texts, show_progress=False)
        
        assert embeddings.shape == (len(texts), EMBEDDING_DIMENSION), \
            f"Expected shape ({len(texts)}, {EMBEDDING_DIMENSION}), got {embeddings.shape}"
        logger.info("[OK] Batch embedding test passed")
    
    def test_embedding_similarity(self):
        """Test embedding similarity calculation"""
        logger.info("Testing embedding similarity...")
        
        generator = EmbeddingGenerator()
        text1 = "The cat sat on the mat."
        text3 = "Machine learning is fascinating."

        similarity_identical = generator.get_similarity_score(text1, text1)
        similarity_different = generator.get_similarity_score(text1, text3)

        assert similarity_identical > similarity_different, \
            "Similar texts should have higher similarity than dissimilar texts"
        logger.info(
            "[OK] Similarity test passed "
            f"(identical={similarity_identical:.3f}, different={similarity_different:.3f})"
        )


if __name__ == "__main__":
    test = TestEmbeddingGenerator()
    test.test_single_embedding()
    test.test_batch_embedding()
    test.test_embedding_similarity()
    logger.info("\n[OK] All embedding tests passed!")
