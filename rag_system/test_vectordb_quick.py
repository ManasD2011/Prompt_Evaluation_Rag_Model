#!/usr/bin/env python
"""Test vector database - No pytest needed"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from tests.test_vector_db import TestVectorDatabase

if __name__ == "__main__":
    print("\n" + "="*80)
    print("VECTOR DATABASE TESTS")
    print("="*80 + "\n")
    
    test = TestVectorDatabase()
    
    try:
        test.test_database_initialization()
        print("")
        test.test_add_and_retrieve_embeddings()
        print("")
        test.test_metadata_persistence()
        print("\n" + "="*80)
        print("SUCCESS: All vector DB tests passed!")
        print("="*80 + "\n")
    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
