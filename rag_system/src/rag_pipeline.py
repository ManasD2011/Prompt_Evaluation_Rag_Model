"""
Main RAG Pipeline
Orchestrates the complete Retrieval-Augmented Generation system
"""
import logging
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
import sys

sys.path.append(str(Path(__file__).parent.parent))

from config.config import (
    LOGS_DIR, TOP_K_RETRIEVAL, MAX_CONTEXT_LENGTH,
    TEXT_COLUMNS, SIMILARITY_THRESHOLD, LLM_PROVIDER, ALLOW_LLM_NO_CONTEXT_FALLBACK
)
from src.embedding_generator import EmbeddingGenerator
from src.vector_db_handler import FAISSVectorDatabase
from src.gemini_integration import GeminiAPI
from src.openai_integration import OpenAIAPI
from src.evaluation_metrics import EvaluationMetrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "rag_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RAGPipeline:
    """Complete RAG system orchestration"""
    
    def __init__(self, load_from_saved: bool = False, initialize_llm: bool = True):
        """
        Initialize RAG pipeline
        
        Args:
            load_from_saved: Load existing embeddings and index
            initialize_llm: Initialize LLM client during startup
        """
        logger.info("=" * 70)
        logger.info("Initializing RAG Pipeline")
        logger.info("=" * 70)
        
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = FAISSVectorDatabase()
        self.llm_api = None
        self.llm_provider = LLM_PROVIDER
        self.evaluation_metrics = EvaluationMetrics()
        
        if initialize_llm:
            # Try to initialize selected LLM provider (non-critical if fails)
            try:
                if self.llm_provider == "openai":
                    self.llm_api = OpenAIAPI()
                    logger.info("[OK] OpenAI API initialized")
                else:
                    # Default to Gemini for unknown provider values
                    if self.llm_provider != "gemini":
                        logger.warning(
                            f"Unknown LLM_PROVIDER '{self.llm_provider}'. Falling back to 'gemini'."
                        )
                        self.llm_provider = "gemini"
                    self.llm_api = GeminiAPI()
                    logger.info("[OK] Gemini API initialized")
            except Exception as e:
                logger.warning(f"{self.llm_provider} API initialization failed: {str(e)}")
                logger.warning("RAG pipeline will run in retrieval-only mode.")
        else:
            logger.info("LLM initialization skipped. Running retrieval-only mode.")
        
        if load_from_saved:
            self.load_from_disk()
        
        logger.info("[OK] RAG Pipeline ready")
    
    def add_documents(self, texts: List[str], metadata: Optional[List[Dict]] = None) -> np.ndarray:
        """
        Add documents to the RAG system
        
        Args:
            texts: List of document texts
            metadata: Optional metadata for each text
            
        Returns:
            Generated embeddings
        """
        logger.info(f"Adding {len(texts)} documents to RAG system")
        
        # Generate embeddings
        embeddings = self.embedding_generator.generate_embeddings_batch(texts)
        
        # Add to vector database
        self.vector_db.add_embeddings(embeddings, texts, metadata)
        
        logger.info(f"[OK] Added {len(texts)} documents to vector database")
        
        return embeddings
    
    def retrieve_context(self, query: str, top_k: int = TOP_K_RETRIEVAL,
                        threshold: float = SIMILARITY_THRESHOLD) -> Tuple[List[str], List[float]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            threshold: Minimum similarity threshold
            
        Returns:
            Tuple of (documents, similarity scores)
        """
        logger.info(f"Retrieving documents for query: {query[:50]}...")
        
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Search vector database
        similarities, texts, metadata = self.vector_db.search_with_threshold(
            query_embedding, top_k=top_k, threshold=threshold
        )
        
        logger.info(f"Retrieved {len(texts)} documents (threshold={threshold})")
        
        return texts, similarities
    
    def format_context(self, documents: List[str], max_length: int = MAX_CONTEXT_LENGTH) -> str:
        """
        Format retrieved documents into context string
        
        Args:
            documents: List of documents
            max_length: Maximum context length
            
        Returns:
            Formatted context string
        """
        context = "\n---\n".join(documents)
        
        # Truncate if too long
        if len(context) > max_length:
            context = context[:max_length] + "..."
            logger.warning(f"Context truncated to {max_length} characters")
        
        return context
    
    def generate_rag_response(self, query: str, 
                             top_k: int = TOP_K_RETRIEVAL,
                             use_llm: bool = True) -> Dict:
        """
        Generate RAG response to user query
        
        Args:
            query: User query
            top_k: Number of context documents
            use_llm: Use Gemini LLM to generate response
            
        Returns:
            Response dictionary with context and answer
        """
        logger.info("=" * 70)
        logger.info("RAG RESPONSE GENERATION")
        logger.info("=" * 70)
        logger.info(f"Query: {query}")
        
        # Step 1: Retrieve context
        documents, similarities = self.retrieve_context(query, top_k=top_k)
        
        if not documents:
            logger.warning("No documents retrieved. Empty context.")
            if use_llm and self.llm_api and ALLOW_LLM_NO_CONTEXT_FALLBACK:
                try:
                    logger.info("Using no-context LLM fallback response.")
                    fallback_prompt = (
                        f"Answer this question clearly and briefly:\n\n{query}\n\n"
                        "If uncertain, say so."
                    )
                    fallback_answer = self.llm_api.generate_response(fallback_prompt)
                    return {
                        "query": query,
                        "context": "No relevant documents found in knowledge base.",
                        "answer": fallback_answer,
                        "retrieved_documents": [],
                        "similarities": [],
                        "used_llm": True
                    }
                except Exception as e:
                    logger.error(f"No-context LLM fallback failed: {str(e)}")

            return {
                "query": query,
                "context": "No relevant documents found in knowledge base.",
                "answer": "I don't have relevant information about this query in my knowledge base.",
                "retrieved_documents": [],
                "similarities": [],
                "used_llm": False
            }
        
        # Step 2: Format context
        context = self.format_context(documents)
        
        logger.info(f"Context length: {len(context)} characters")
        logger.info(f"Top document similarity: {similarities[0]:.3f}")
        
        # Step 3: Generate response using LLM
        if use_llm and self.llm_api:
            try:
                logger.info(f"Generating response with {self.llm_provider} LLM...")
                answer = self.llm_api.generate_rag_response(query, context)
                logger.info(f"[OK] Generated response: {answer[:100]}...")
                
                response = {
                    "query": query,
                    "context": context,
                    "answer": answer,
                    "retrieved_documents": documents,
                    "similarities": similarities,
                    "used_llm": True
                }
            except Exception as e:
                error_text = str(e)
                logger.error(f"LLM generation failed: {error_text}")

                if "429" in error_text or "quota" in error_text.lower():
                    fallback_answer = (
                        f"LLM response unavailable because {self.llm_provider} API quota/rate limit "
                        "was exceeded. Showing retrieval-only context.\n\n"
                        f"Best matched context (similarity: {similarities[0]:.3f}):\n"
                        f"{documents[0][:600]}"
                    )
                else:
                    fallback_answer = (
                        "LLM response unavailable due to an API/configuration error. "
                        "Showing retrieval-only context.\n\n"
                        f"Best matched context (similarity: {similarities[0]:.3f}):\n"
                        f"{documents[0][:600]}"
                    )

                response = {
                    "query": query,
                    "context": context,
                    "answer": fallback_answer,
                    "retrieved_documents": documents,
                    "similarities": similarities,
                    "used_llm": False,
                    "llm_error": error_text
                }
        else:
            # Return best matching document
            response = {
                "query": query,
                "context": context,
                "answer": f"Most relevant document:\n\n{documents[0]}",
                "retrieved_documents": documents,
                "similarities": similarities,
                "used_llm": False
            }
        
        logger.info("=" * 70 + "\n")
        
        return response
    
    def evaluate_user_answer(self, user_answer: str, 
                            query: str,
                            correct_answer: Optional[str] = None) -> Dict:
        """
        Evaluate user's answer against retrieved correct answer
        
        Args:
            user_answer: User's answer
            query: Original query
            correct_answer: Optional correct answer (if not provided, retrieve one)
            
        Returns:
            Evaluation results
        """
        logger.info("=" * 70)
        logger.info("EVALUATING USER ANSWER")
        logger.info("=" * 70)
        
        # Get correct answer if not provided
        if correct_answer is None:
            documents, _ = self.retrieve_context(query, top_k=1)
            correct_answer = documents[0] if documents else "No reference found"
        
        # Calculate similarity
        similarity = self.embedding_generator.get_similarity_score(user_answer, correct_answer)
        
        logger.info(f"Similarity score: {similarity:.3f}")
        
        # Evaluate using 6-category rubric
        evaluation = self.evaluation_metrics.evaluate_answer(
            similarity_score=similarity,
            retrieved_answer=correct_answer,
            user_answer=user_answer,
            confidence=0.5
        )
        
        return evaluation
    
    def save_to_disk(self, output_dir: Optional[str] = None) -> None:
        """
        Save pipeline state to disk
        
        Args:
            output_dir: Directory to save to
        """
        if output_dir is None:
            from config.config import VECTOR_DB_DIR, EMBEDDINGS_DIR
            output_dir = VECTOR_DB_DIR
        
        logger.info(f"Saving RAG pipeline to {output_dir}")
        
        # Save embeddings
        self.embedding_generator.save_embeddings(f"{output_dir}/embeddings.npy")
        self.embedding_generator.save_metadata(f"{output_dir}/embeddings_metadata.json")
        
        # Save vector database
        self.vector_db.save_index(f"{output_dir}/faiss_index.bin")
        
        logger.info("[OK] RAG pipeline saved to disk")
    
    def load_from_disk(self, input_dir: Optional[str] = None) -> None:
        """
        Load pipeline state from disk
        
        Args:
            input_dir: Directory to load from
        """
        if input_dir is None:
            from config.config import VECTOR_DB_DIR
            input_dir = VECTOR_DB_DIR
        
        logger.info(f"Loading RAG pipeline from {input_dir}")
        
        try:
            # Load vector database
            self.vector_db.load_index(
                f"{input_dir}/faiss_index.bin",
                f"{input_dir}/metadata.json"
            )
            logger.info("[OK] RAG pipeline loaded from disk")
        except Exception as e:
            logger.warning(f"Could not load from disk: {str(e)}")
    
    def get_system_status(self) -> Dict:
        """Get current system status"""
        status = {
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "embedding_dim": self.embedding_generator.embedding_dim,
            "vector_db_size": self.vector_db.index.ntotal if self.vector_db.index else 0,
            "llm_provider": self.llm_provider,
            "llm_api_available": self.llm_api is not None,
            "evaluation_history_count": len(self.evaluation_metrics.evaluation_history)
        }
        
        logger.info(f"System Status: {json.dumps(status, indent=2)}")
        
        return status


def create_sample_rag_pipeline() -> RAGPipeline:
    """Create sample RAG pipeline for testing"""
    logger.info("Creating sample RAG pipeline...")
    
    pipeline = RAGPipeline()
    
    # Sample documents
    sample_docs = [
        "Machine Learning is a subset of AI that enables systems to learn from data.",
        "Deep Learning uses neural networks with multiple layers to process data.",
        "Natural Language Processing helps computers understand human language.",
        "Computer Vision enables machines to analyze visual information from images and videos.",
        "RAG systems combine retrieval and generation for better accuracy."
    ]
    
    # Add documents
    pipeline.add_documents(sample_docs)
    
    logger.info("[OK] Sample pipeline created with 5 documents")
    
    return pipeline


if __name__ == "__main__":
    logger.info("RAG Pipeline Module Ready")

