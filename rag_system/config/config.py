"""
Configuration module for RAG System
Centralized configuration management for all components
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============= PROJECT PATHS =============
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TRINETRI_DATASET_DIR = Path(
    os.getenv(
        "TRINETRI_DATASET_DIR",
        str(PROJECT_ROOT.parent / "Trinetri Datsets")
    )
)
EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
MODELS_DIR = PROJECT_ROOT / "models"
CONFIG_DIR = PROJECT_ROOT / "config"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for directory in [DATA_RAW_DIR, DATA_PROCESSED_DIR, EMBEDDINGS_DIR, VECTOR_DB_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============= EMBEDDING CONFIG =============
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # Fast & efficient
EMBEDDING_DIMENSION = 384
BATCH_SIZE_EMBEDDINGS = 32

# ============= VECTOR DB CONFIG =============
FAISS_INDEX_PATH = VECTOR_DB_DIR / "faiss_index.bin"
METADATA_PATH = VECTOR_DB_DIR / "metadata.json"
USE_FAISS = True  # Change to ChromaDB if needed

# ============= RAG CONFIG =============
TOP_K_RETRIEVAL = 5 # Number of documents to retrieve for context
SIMILARITY_THRESHOLD = 0.45  # Minimum similarity score for retrieval
MAX_CONTEXT_LENGTH = 2000  # Max characters for context in prompt
ALLOW_LLM_NO_CONTEXT_FALLBACK = os.getenv("ALLOW_LLM_NO_CONTEXT_FALLBACK", "false").strip().lower() == "true"

# ============= GEMINI API CONFIG =============
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ============= OPENAI API CONFIG =============
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# ============= LLM PROVIDER CONFIG =============
# Supported values: "gemini", "openai"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
GENERATION_CONFIG = {
    "temperature": 0.3,  # Lower for factual consistency
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# ============= DATA PROCESSING CONFIG =============
TEXT_COLUMNS = [
    "question",
    "answer",
    "context",
    "text",
    "content",
    "description",
    "prompt_text",
    "justification",
    "strengths",
    "gaps",
    "subtopic",
]  # Columns to embed
CLEAN_TEXT = True
REMOVE_DUPLICATES = True
NORMALIZE_TEXT = True
MIN_TEXT_LENGTH = 10  # Minimum length for valid text

# ============= EVALUATION METRICS CONFIG (Based on 6-Category Rubric) =============
EVALUATION_METRICS = {
    "C1_prompt_foundations": 0.15,      # 15%: Understanding of mechanics
    "C2_design_patterns": 0.20,          # 20%: Use of deliberate techniques
    "C3_iterative_refinement": 0.20,     # 20%: Diagnostic capability
    "C4_domain_application": 0.20,       # 20%: Adaptation of constraints
    "C5_ethics_safety": 0.15,            # 15%: Awareness of bias/regulations
    "C6_metacognition": 0.10,            # 10%: Identifying uncertainty
}

# ============= LOGGING CONFIG =============
LOG_LEVEL = "INFO"
LOG_FILE = LOGS_DIR / "rag_system.log"

# ============= PREPROCESSING CONFIG =============
EXCEL_SHEET_NAME = 0  # Sheet index or name to read from Excel
EXCEL_ENCODING = "utf-8"

# ============= DATABASE INDEXES =============
VECTOR_DB_INDEXES = {
    "qa_pairs": "qa_pairs_index",
    "documents": "documents_index",
}

# ============= SYSTEM PROMPTS =============
SYSTEM_PROMPT = """You are a helpful AI assistant with access to a curated knowledge base.

INSTRUCTIONS:
1. ANSWER STRICTLY BASED ON RETRIEVED CONTEXT - only use the information provided
2. If the answer is not in the context, respond: "I don't have relevant information about this in my knowledge base."
3. Be clear, concise, and factual
4. Cite the context when possible
5. Avoid speculation or hallucination
6. If uncertain, express your uncertainty explicitly

RETRIEVED CONTEXT:
{context}

USER QUESTION:
{question}

RESPONSE:"""

# ============= EVALUATION PROMPT =============
EVALUATION_PROMPT = """Evaluate the user's answer against the retrieved correct answer.

USER ANSWER: {user_answer}
RETRIEVED ANSWER: {retrieved_answer}

Provide:
1. Similarity Score (0-1): How similar are the answers in meaning?
2. Correctness Assessment: Is the user answer correct/partially correct/incorrect?
3. Confidence Level (0-1): How confident are you in this assessment?
4. Brief explanation of the differences (if any)

Format your response as JSON."""

print(f"[OK] Configuration loaded from {PROJECT_ROOT}")

