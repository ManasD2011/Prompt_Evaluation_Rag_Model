"""
Quick test runner - No pytest needed
Run all tests directly
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("\n" + "="*80)
print("RUNNING EMBEDDING TESTS")
print("="*80)
try:
    from tests.test_embeddings import TestEmbeddingGenerator
    test = TestEmbeddingGenerator()
    test.test_single_embedding()
    test.test_batch_embedding()
    test.test_embedding_similarity()
    print("[PASS] All embedding tests passed!\n")
except Exception as e:
    print(f"[FAIL] Embedding tests failed: {str(e)}\n")

print("="*80)
print("RUNNING VECTOR DB TESTS")
print("="*80)
try:
    from tests.test_vector_db import TestVectorDatabase
    test = TestVectorDatabase()
    test.test_database_initialization()
    test.test_add_and_retrieve_embeddings()
    test.test_metadata_persistence()
    print("[PASS] All vector DB tests passed!\n")
except Exception as e:
    print(f"[FAIL] Vector DB tests failed: {str(e)}\n")

print("="*80)
print("RUNNING RAG PIPELINE TESTS")
print("="*80)
try:
    from tests.test_rag_pipeline import TestRAGPipeline
    test = TestRAGPipeline()
    test.test_pipeline_initialization()
    test.test_document_addition()
    test.test_document_retrieval()
    print("[PASS] All RAG pipeline tests passed!\n")
except Exception as e:
    print(f"[FAIL] RAG pipeline tests failed: {str(e)}\n")

print("="*80)
print("TEST SUMMARY")
print("="*80)
print("All tests completed! Check results above.")
