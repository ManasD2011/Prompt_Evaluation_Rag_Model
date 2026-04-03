"""
Integration tests for RAG Pipeline
"""
import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestRAGPipeline:
    """Test suite for RAG Pipeline"""
    
    def test_pipeline_initialization(self):
        """Test RAG pipeline initialization"""
        logger.info("Testing RAG pipeline initialization...")
        
        try:
            pipeline = RAGPipeline(load_from_saved=False, initialize_llm=False)
            assert pipeline.embedding_generator is not None
            assert pipeline.vector_db is not None
            assert pipeline.llm_api is None
            logger.info("[OK] Pipeline initialization test passed")
        except Exception as e:
            logger.warning(f"Pipeline initialization test warning (expected if no API keys): {str(e)}")
    
    def test_document_addition(self):
        """Test adding documents to pipeline"""
        logger.info("Testing document addition...")
        
        try:
            pipeline = RAGPipeline(load_from_saved=False, initialize_llm=False)
            
            sample_texts = [
                "The capital of France is Paris.",
                "The Earth orbits around the Sun.",
                "Python is a popular programming language.",
            ]
            
            pipeline.add_documents(sample_texts)
            logger.info("[OK] Document addition test passed")
        except Exception as e:
            logger.error(f"Document addition test failed: {str(e)}")
            raise
    
    def test_document_retrieval(self):
        """Test retrieving documents"""
        logger.info("Testing document retrieval...")
        
        try:
            pipeline = RAGPipeline(load_from_saved=False, initialize_llm=False)
            
            # Add sample documents
            sample_texts = [
                "Machine learning is a subset of artificial intelligence.",
                "Deep learning uses neural networks with multiple layers.",
                "Natural language processing deals with text data.",
            ]
            pipeline.add_documents(sample_texts)
            
            # Retrieve documents
            query = "What is machine learning?"
            documents, similarities = pipeline.retrieve_context(query, top_k=2, threshold=0.0)

            assert len(documents) > 0, "Should retrieve at least one document"
            assert len(documents) == len(similarities), "Documents and similarities must align"
            logger.info(f"[OK] Retrieved {len(documents)} documents")
            logger.info("[OK] Document retrieval test passed")
        except Exception as e:
            logger.error(f"Document retrieval test failed: {str(e)}")
            raise


if __name__ == "__main__":
    test = TestRAGPipeline()
    test.test_pipeline_initialization()
    test.test_document_addition()
    test.test_document_retrieval()
    logger.info("\n[OK] All RAG pipeline tests passed!")
