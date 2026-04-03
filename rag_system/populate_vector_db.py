"""
Populate Vector Database with Embeddings
Script to generate and store embeddings from processed data
"""
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
import json

sys.path.append(str(Path(__file__).parent.parent))

from config.config import (
    DATA_PROCESSED_DIR, EMBEDDINGS_DIR, VECTOR_DB_DIR,
    TEXT_COLUMNS, EMBEDDING_DIMENSION
)
from src.embedding_generator import EmbeddingGenerator
from src.vector_db_handler import FAISSVectorDatabase
from src.utils import get_timestamp, save_json, save_embeddings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_processed_data(file_path: Path = DATA_PROCESSED_DIR / "processed_data.csv") -> pd.DataFrame:
    """Load processed data from CSV"""
    try:
        df = pd.read_csv(file_path)
        logger.info(f"✓ Loaded data: {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Failed to load data: {str(e)}")
        raise


def extract_text_for_embedding(row: pd.Series, columns: Optional[List[str]] = None) -> str:
    """Extract combined text from row for embedding"""
    if columns is None:
        columns = TEXT_COLUMNS
    
    texts = []
    for col in columns:
        if col in row.index and pd.notna(row[col]):
            value = str(row[col]).strip()
            if value:
                texts.append(value)
    
    return " | ".join(texts) if texts else ""


def prepare_metadata(row: pd.Series, idx: int) -> Dict:
    """Prepare metadata for each document"""
    return {
        "doc_id": idx,
        "prompt_id": row.get("prompt_id", f"doc_{idx}"),
        "skill_level": row.get("skill_level", "unknown"),
        "domain": row.get("domain", "unknown"),
        "source_type": row.get("source_type", "unknown"),
        "final_score": float(row.get("final_score", 0)),
        "timestamp": get_timestamp(),
    }


def populate_vector_db(
    data_file: Path = DATA_PROCESSED_DIR / "processed_data.csv",
    batch_size: int = 16,
    force_rebuild: bool = False
) -> Dict:
    """
    Main function to populate vector database
    
    Args:
        data_file: Path to processed data CSV
        batch_size: Batch size for embedding generation
        force_rebuild: Force rebuild even if index exists
        
    Returns:
        Statistics dictionary
    """
    logger.info("=" * 80)
    logger.info("VECTOR DATABASE POPULATION")
    logger.info("=" * 80)
    
    # Load data
    df = load_processed_data(data_file)
    logger.info(f"\nProcessing {len(df)} documents...")
    
    # Initialize components
    embedding_generator = EmbeddingGenerator()
    vector_db = FAISSVectorDatabase()
    
    # Check if index already exists
    if vector_db.index is not None and vector_db.index.ntotal > 0 and not force_rebuild:
        logger.warning(f"Vector DB already has {vector_db.index.ntotal} entries. Use force_rebuild=True to regenerate.")
        return {
            "status": "skipped",
            "reason": "Index already populated",
            "existing_entries": vector_db.index.ntotal
        }
    
    # Prepare texts and metadata
    texts = []
    metadata_list = []
    valid_count = 0
    
    for idx, (_, row) in enumerate(df.iterrows()):
        text = extract_text_for_embedding(row)
        if text and len(text) > 5:  # Skip very short texts
            texts.append(text)
            metadata_list.append(prepare_metadata(row, valid_count))
            valid_count += 1
    
    logger.info(f"✓ Extracted {len(texts)} valid texts for embedding")
    
    if not texts:
        logger.error("No valid texts found!")
        return {"status": "failed", "reason": "No valid texts"}
    
    # Generate embeddings in batches
    logger.info(f"\nGenerating embeddings (batch_size={batch_size})...")
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_embeddings = embedding_generator.generate_embeddings_batch(batch_texts)
        all_embeddings.append(batch_embeddings)
        
        progress = min(i + batch_size, len(texts))
        logger.info(f"  {progress}/{len(texts)} embeddings generated")
    
    # Concatenate all embeddings
    embeddings = np.vstack(all_embeddings)
    logger.info(f"✓ Generated embeddings shape: {embeddings.shape}")
    
    # Add to vector database
    logger.info("\nAdding embeddings to vector database...")
    vector_db.add_embeddings(embeddings, texts, metadata_list)
    logger.info(f"✓ Added {len(texts)} embeddings to FAISS index")
    
    # Save embeddings for reference
    logger.info("\nSaving embeddings and metadata...")
    embeddings_path = EMBEDDINGS_DIR / f"embeddings_{get_timestamp()}.npy"
    save_embeddings(embeddings, embeddings_path)
    
    # Update vector DB metadata
    vector_db.save_index()
    logger.info("✓ Vector DB index saved")
    
    # Generate statistics
    stats = {
        "status": "success",
        "total_documents": len(df),
        "embedded_documents": len(texts),
        "embedding_dimension": embeddings.shape[1],
        "total_embeddings": embeddings.shape[0],
        "batch_size": batch_size,
        "timestamp": get_timestamp(),
        "vector_db_path": str(VECTOR_DB_DIR),
    }
    
    logger.info("\n" + "=" * 80)
    logger.info("POPULATION COMPLETE")
    logger.info("=" * 80)
    logger.info(f"Total documents: {stats['total_documents']}")
    logger.info(f"Embedded documents: {stats['embedded_documents']}")
    logger.info(f"Embedding dimension: {stats['embedding_dimension']}")
    logger.info(f"Vector DB entries: {stats['total_embeddings']}")
    logger.info("=" * 80)
    
    return stats


def verify_vector_db() -> Dict:
    """Verify vector database is properly populated"""
    try:
        vector_db = FAISSVectorDatabase()
        # Load the saved index from disk
        vector_db.load_index()
        
        if vector_db.index is None or vector_db.index.ntotal == 0:
            logger.warning("Vector DB is empty!")
            return {"status": "empty", "entries": 0}
        
        # Test search
        test_query = "data structures algorithm"
        results = vector_db.search_text(test_query, k=3)
        
        logger.info(f"[OK] Vector DB verified!")
        logger.info(f"  Total entries: {vector_db.index.ntotal}")
        logger.info(f"  Dimension: {vector_db.index.d}")
        logger.info(f"  Sample search results: {len(results)} retrieved")
        
        return {
            "status": "verified",
            "entries": vector_db.index.ntotal,
            "dimension": vector_db.index.d,
            "sample_search_results": len(results)
        }
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        return {"status": "error", "reason": str(e)}


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate Vector Database")
    parser.add_argument("--data", type=str, default=str(DATA_PROCESSED_DIR / "processed_data.csv"),
                        help="Path to processed data CSV")
    parser.add_argument("--batch-size", type=int, default=16,
                        help="Batch size for embedding generation")
    parser.add_argument("--force-rebuild", action="store_true",
                        help="Force rebuild even if index exists")
    parser.add_argument("--verify-only", action="store_true",
                        help="Only verify existing vector DB")
    
    args = parser.parse_args()
    
    if args.verify_only:
        logger.info("Verifying Vector Database...")
        result = verify_vector_db()
        print(json.dumps(result, indent=2))
    else:
        # Populate vector DB
        stats = populate_vector_db(
            data_file=Path(args.data),
            batch_size=args.batch_size,
            force_rebuild=args.force_rebuild
        )
        
        # Verify it worked
        logger.info("\nVerifying population...")
        verify_result = verify_vector_db()
        stats.update(verify_result)
        
        # Print summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        for key, value in stats.items():
            print(f"{key}: {value}")
        print("=" * 80)
