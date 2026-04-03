#!/usr/bin/env python
"""Test RAG pipeline - No pytest needed"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from tests.test_rag_pipeline import TestRAGPipeline

if __name__ == "__main__":
    print("\n" + "="*80)
    print("RAG PIPELINE TESTS")
    print("="*80 + "\n")
    
    test = TestRAGPipeline()
    
    try:
        test.test_pipeline_initialization()
        print("")
        test.test_document_addition()
        print("")
        test.test_document_retrieval()
        print("\n" + "="*80)
        print("SUCCESS: All RAG pipeline tests passed!")
        print("="*80 + "\n")
    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
