#!/usr/bin/env python
"""Test embedding generator - No pytest needed"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from tests.test_embeddings import TestEmbeddingGenerator

if __name__ == "__main__":
    print("\n" + "="*80)
    print("EMBEDDING GENERATOR TESTS")
    print("="*80 + "\n")
    
    test = TestEmbeddingGenerator()
    
    try:
        test.test_single_embedding()
        print("")
        test.test_batch_embedding()
        print("")
        test.test_embedding_similarity()
        print("\n" + "="*80)
        print("SUCCESS: All embedding tests passed!")
        print("="*80 + "\n")
    except Exception as e:
        print(f"\nERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
