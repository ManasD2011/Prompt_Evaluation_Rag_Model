"""
Unit tests for vector database operations
"""
import sys
import logging
import numpy as np
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.vector_db_handler import FAISSVectorDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestVectorDatabase:
    """Test suite for FAISSVectorDatabase"""
    
    def test_database_initialization(self):
        """Test vector database initialization"""
        logger.info("Testing database initialization...")
        
        db = FAISSVectorDatabase()
        assert db.index is None, "Vector index should be lazy-initialized"
        assert db.get_stats()["total_embeddings"] == 0
        logger.info("[OK] Database initialization test passed")
    
    def test_add_and_retrieve_embeddings(self):
        """Test adding and retrieving embeddings"""
        logger.info("Testing add and retrieve embeddings...")
        
        db = FAISSVectorDatabase()
        
        # Create sample embeddings
        sample_embeddings = np.random.rand(5, 384).astype(np.float32)
        texts = [f"Document {i}" for i in range(5)]
        metadata = [{"doc_id": i} for i in range(5)]
        
        # Add embeddings
        db.add_embeddings(sample_embeddings, texts, metadata)
        logger.info(f"Added {len(texts)} embeddings")
        
        # Search
        query_embedding = sample_embeddings[0:1]
        similarities, result_texts, result_metadata = db.search(query_embedding, top_k=3)

        assert len(result_texts) > 0, "Should retrieve at least one result"
        assert result_texts[0] == texts[0], "First result should be the query document"
        assert result_metadata[0]["doc_id"] == 0, "Metadata should match query document"
        assert similarities[0] >= similarities[-1], "Results should be sorted by similarity"
        logger.info("[OK] Add and retrieve test passed")
    
    def test_metadata_persistence(self):
        """Test metadata is properly stored"""
        logger.info("Testing metadata persistence...")
        
        db = FAISSVectorDatabase()
        
        sample_embeddings = np.random.rand(3, 384).astype(np.float32)
        texts = ["Text 1", "Text 2", "Text 3"]
        metadata = [
            {"source": "file1", "page": 1},
            {"source": "file2", "page": 2},
            {"source": "file3", "page": 3},
        ]
        
        db.add_embeddings(sample_embeddings, texts, metadata)
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            index_path = Path(tmp_dir) / "faiss_index.bin"
            metadata_path = Path(tmp_dir) / "metadata.json"
            db.save_index(str(index_path))

            db_loaded = FAISSVectorDatabase()
            db_loaded.load_index(str(index_path), str(metadata_path))
            for i, meta in enumerate(db_loaded.metadata):
                assert meta["source"] == f"file{i+1}", f"Metadata mismatch at index {i}"
        
        logger.info("[OK] Metadata persistence test passed")


if __name__ == "__main__":
    test = TestVectorDatabase()
    test.test_database_initialization()
    test.test_add_and_retrieve_embeddings()
    test.test_metadata_persistence()
    logger.info("\n[OK] All vector database tests passed!")
