"""
Main RAG System Entry Point
Complete workflow for RAG system initialization, processing, and evaluation
"""
import json
import logging
import sys
from pathlib import Path
from typing import Optional

# Ensure Windows console can print Unicode log messages cleanly.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import (
    DATA_RAW_DIR, DATA_PROCESSED_DIR, LOGS_DIR, TRINETRI_DATASET_DIR, TEXT_COLUMNS
)
from src.data_preprocessor import preprocess_dataset
from src.embedding_generator import generate_embeddings_from_data
from src.vector_db_handler import initialize_vector_db
from src.rag_pipeline import RAGPipeline, create_sample_rag_pipeline
from src.gemini_integration import test_gemini_setup
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / "main.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print project banner"""
    banner = """
    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•‘                                                               â•‘
    â•‘     RAG SYSTEM - Retrieval-Augmented Generation Pipeline      â•‘
    â•‘                                                               â•‘
    â•‘     6-Category Rubric Evaluation System                       â•‘
    â•‘     â€¢ C1: Prompt Foundations (15%)                           â•‘
    â•‘     â€¢ C2: Design & Patterns (20%)                            â•‘
    â•‘     â€¢ C3: Iterative Refinement (20%)                         â•‘
    â•‘     â€¢ C4: Domain Application (20%)                           â•‘
    â•‘     â€¢ C5: Ethics & Safety (15%)                              â•‘
    â•‘     â€¢ C6: Metacognition (10%)                                â•‘
    â•‘                                                               â•‘
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    """
    print(banner)


def setup_rag_system(excel_file_path: str) -> RAGPipeline:
    """
    Complete setup pipeline: Load â†’ Process â†’ Embed â†’ Index
    
    Args:
        excel_file_path: Path to Excel dataset
        
    Returns:
        Initialized RAG pipeline
    """
    logger.info("=" * 70)
    logger.info("STARTING RAG SYSTEM SETUP")
    logger.info("=" * 70)
    
    # Step 1: Preprocess data
    logger.info("\n[STEP 1/4] Data Preprocessing...")
    logger.info("-" * 70)
    
    try:
        df_processed, metadata = preprocess_dataset(
            excel_file_path,
            output_json=str(DATA_PROCESSED_DIR / "processed_data.json"),
            output_csv=str(DATA_PROCESSED_DIR / "processed_data.csv")
        )
        
        logger.info(f"[OK] Preprocessing complete: {len(df_processed)} records")
        
    except Exception as e:
        logger.error(f"Preprocessing failed: {str(e)}")
        raise
    
    # Step 2: Extract texts for embedding
    logger.info("\n[STEP 2/4] Extracting Texts for Embedding...")
    logger.info("-" * 70)
    
    # Combine relevant columns into single text
    text_columns = [col for col in TEXT_COLUMNS if col in df_processed.columns]
    if not text_columns:
        # Fallback: all object/string columns
        text_columns = [
            col for col in df_processed.columns
            if df_processed[col].dtype == "object"
        ]
        logger.warning(
            f"No configured text columns found in processed data. "
            f"Falling back to object columns: {text_columns}"
        )

    texts = []
    for _, row in df_processed.iterrows():
        row_texts = []
        for col in text_columns:
            if pd.notna(row[col]):
                value = str(row[col]).strip()
                if value and value.lower() != "nan":
                    row_texts.append(value)

        if row_texts:
            combined_text = " | ".join(row_texts)
            texts.append(combined_text)

    logger.info(f"[OK] Extracted {len(texts)} texts from data")

    if not texts:
        raise ValueError(
            "No valid text content could be extracted for embeddings. "
            f"Checked columns: {text_columns}"
        )
    
    # Step 3: Generate embeddings
    logger.info("\n[STEP 3/4] Generating Embeddings...")
    logger.info("-" * 70)
    
    try:
        embeddings, embeddings_path = generate_embeddings_from_data(texts)
        logger.info(f"[OK] Generated embeddings: {embeddings.shape}")
    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise
    
    # Step 4: Create vector database
    logger.info("\n[STEP 4/4] Creating Vector Database...")
    logger.info("-" * 70)
    
    try:
        # Create metadata
        metadata_list = [{"index": i, "text": text} for i, text in enumerate(texts)]
        
        vector_db = initialize_vector_db(embeddings, texts, metadata_list)
        logger.info(f"[OK] Vector database created with {len(texts)} embeddings")
    except Exception as e:
        logger.error(f"Vector DB creation failed: {str(e)}")
        raise
    
    # Initialize RAG pipeline
    logger.info("\n[FINAL] Initializing RAG Pipeline...")
    logger.info("-" * 70)
    
    pipeline = RAGPipeline(load_from_saved=True)
    
    logger.info("=" * 70)
    logger.info("[OK] RAG SYSTEM SETUP COMPLETE")
    logger.info("=" * 70)
    
    return pipeline


def interactive_rag_session(pipeline: RAGPipeline):
    """
    Interactive RAG query and evaluation session
    
    Args:
        pipeline: Initialized RAG pipeline
    """
    logger.info("\n" + "=" * 70)
    logger.info("STARTING INTERACTIVE RAG SESSION")
    logger.info("=" * 70 + "\n")
    
    print("\n" + "=" * 70)
    print("INTERACTIVE RAG SESSION")
    print("=" * 70)
    print("\nCommands:")
    print("  'query <question>' - Ask a question")
    print("  'eval <user_answer>' - Evaluate your answer")
    print("  'status' - Show system status")
    print("  'report' - Show evaluation report")
    print("  'exit' - Exit session")
    print("=" * 70 + "\n")
    
    last_response = None
    
    while True:
        try:
            user_input = input("RAG> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "exit":
                logger.info("Exiting interactive session")
                break
            
            elif user_input.lower() == "status":
                status = pipeline.get_system_status()
                print(json.dumps(status, indent=2))
            
            elif user_input.lower() == "report":
                summary = pipeline.evaluation_metrics.get_evaluation_summary()
                print(json.dumps(summary, indent=2))
            
            elif user_input.lower().startswith("query "):
                query = user_input[6:]
                response = pipeline.generate_rag_response(query)
                last_response = response
                
                print("\n" + "-" * 70)
                print(f"Query: {response['query']}")
                print(f"\nAnswer:\n{response['answer']}")
                print(f"\nTop Documents Retrieved: {len(response['retrieved_documents'])}")
                if response['similarities']:
                    print(f"Best Match Confidence: {response['similarities'][0]:.3f}")
                if not response.get('used_llm', False):
                    print("Mode: Retrieval-only fallback")
                print("-" * 70 + "\n")
            
            elif user_input.lower().startswith("eval "):
                if last_response is None:
                    print("No query response available. Please ask a query first.")
                    continue
                
                user_answer = user_input[5:]
                evaluation = pipeline.evaluate_user_answer(
                    user_answer=user_answer,
                    query=last_response['query']
                )
                
                print("\n" + "-" * 70)
                print("EVALUATION RESULTS:")
                print(f"Accuracy: {evaluation['accuracy']}")
                print(f"Similarity Score: {evaluation['similarity_score']:.3f}")
                print(f"Overall Score: {evaluation['overall_score']:.3f}")
                print("\n6-Category Rubric Scores:")
                for category, score in evaluation['score_breakdown'].items():
                    print(f"  {category}: {score:.3f}")
                print("-" * 70 + "\n")
            
            else:
                print("Unknown command. Type 'exit' to quit, or see commands above.")
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error in session: {str(e)}")
            print(f"Error: {str(e)}")


def demo_mode():
    """Run demo with sample data"""
    logger.info("\n" + "=" * 70)
    logger.info("RUNNING DEMO MODE WITH SAMPLE DATA")
    logger.info("=" * 70 + "\n")
    
    # Create sample pipeline
    pipeline = create_sample_rag_pipeline()
    
    # Demo queries
    demo_queries = [
        "What is machine learning?",
        "Tell me about deep learning",
        "How does RAG work?"
    ]
    
    print("\n" + "=" * 70)
    print("DEMO: Sample RAG Queries")
    print("=" * 70 + "\n")
    
    for query in demo_queries:
        print(f"Query: {query}")
        response = pipeline.generate_rag_response(query, use_llm=False)
        print(f"Retrieved Documents: {len(response['retrieved_documents'])}")
        if response['similarities']:
            print(f"Best Match Confidence: {response['similarities'][0]:.3f}")
        print("-" * 70 + "\n")
    
    # Demo evaluation
    print("\n" + "=" * 70)
    print("DEMO: Answer Evaluation")
    print("=" * 70 + "\n")
    
    user_answer = "Machine Learning is a type of Artificial Intelligence"
    query = "What is machine learning?"
    
    evaluation = pipeline.evaluate_user_answer(user_answer, query)
    
    print(f"User Answer: {user_answer}")
    print(f"Accuracy: {evaluation['accuracy']}")
    print(f"Overall Score: {evaluation['overall_score']:.3f}")


def main():
    """Main entry point (auto-runs with configured dataset path)."""
    print_banner()

    excel_path = str(TRINETRI_DATASET_DIR)
    logger.info(f"Auto-loading configured dataset path: {excel_path}")

    if not Path(excel_path).exists():
        logger.error(f"Configured dataset path not found: {excel_path}")
        print(f"Error: Configured dataset path not found at {excel_path}")
        return

    try:
        pipeline = setup_rag_system(excel_path)

        # Interactive session
        interactive_rag_session(pipeline)

        # Save evaluation report
        report_path = pipeline.evaluation_metrics.save_evaluation_report()
        print(f"\nEvaluation report saved to: {report_path}")

    except Exception as e:
        logger.error(f"Failed to set up RAG system: {str(e)}")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()

