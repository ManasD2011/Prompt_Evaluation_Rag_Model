"""
RAG System - Retrieval-Augmented Generation Pipeline
Complete system for document retrieval, embedding, and GPT-enhanced responses
"""

__version__ = "1.0.0"
__author__ = "RAG Team"

from src.data_preprocessor import DataPreprocessor, preprocess_dataset
from src.embedding_generator import EmbeddingGenerator, generate_embeddings_from_data
from src.vector_db_handler import FAISSVectorDatabase, initialize_vector_db
from src.gemini_integration import GeminiAPI, test_gemini_setup
from src.openai_integration import OpenAIAPI, test_openai_setup
from src.evaluation_metrics import EvaluationMetrics
from src.rag_pipeline import RAGPipeline, create_sample_rag_pipeline

__all__ = [
    "DataPreprocessor",
    "preprocess_dataset",
    "EmbeddingGenerator",
    "generate_embeddings_from_data",
    "FAISSVectorDatabase",
    "initialize_vector_db",
    "GeminiAPI",
    "test_gemini_setup",
    "OpenAIAPI",
    "test_openai_setup",
    "EvaluationMetrics",
    "RAGPipeline",
    "create_sample_rag_pipeline"
]
