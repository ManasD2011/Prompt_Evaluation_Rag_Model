# RAG System - API Documentation

Complete API reference for all modules and functions in the RAG system.

---

## 📦 Module Overview

```
rag_system/
├── src/
│   ├── data_preprocessor.py       # Data cleaning and formatting
│   ├── embedding_generator.py     # Text to vector conversion
│   ├── vector_db_handler.py       # Similarity search and indexing
│   ├── gemini_integration.py      # LLM API integration
│   ├── evaluation_metrics.py      # 6-category scoring system
│   ├── rag_pipeline.py            # Main orchestration
│   └── __init__.py
└── config/
    └── config.py                   # Global configuration
```

---

## 🔧 Core Modules

### 1. Data Preprocessor (`data_preprocessor.py`)

Handles Excel file loading, cleaning, and normalization.

#### Class: `DataPreprocessor`

```python
from src.data_preprocessor import DataPreprocessor

preprocessor = DataPreprocessor()
```

##### Methods

**`load_excel(file_path: str, sheet_name: int = 0) -> DataFrame`**
- Load Excel file
- Returns: pandas DataFrame
```python
df = preprocessor.load_excel("data.xlsx")
print(df.shape)  # (234, 5)
```

**`remove_null_values(df: DataFrame, subset: List[str] = None) -> DataFrame`**
- Remove rows with null values
- Returns: Cleaned DataFrame
```python
df_clean = preprocessor.remove_null_values(df)
```

**`normalize_text(text: str) -> str`**
- Normalize single text: lowercase, remove special chars
- Returns: Normalized text string
```python
text = preprocessor.normalize_text("  Hello WORLD!!! ")
# Returns: "hello world"
```

**`deduplicate(df: DataFrame, subset: List[str] = None) -> DataFrame`**
- Remove duplicate rows
- Returns: DataFrame with unique rows
```python
df_unique = preprocessor.deduplicate(df)
```

**`process_dataframe(df: DataFrame, identify_text_columns: bool = True) -> DataFrame`**
- Complete preprocessing pipeline
- Returns: Fully processed DataFrame
```python
df_processed = preprocessor.process_dataframe(df)
```

**`to_json(df: DataFrame, output_path: str) -> None`**
- Save DataFrame to JSON
```python
preprocessor.to_json(df, "output.json")
```

**`to_csv(df: DataFrame, output_path: str) -> None`**
- Save DataFrame to CSV
```python
preprocessor.to_csv(df, "output.csv")
```

#### Function: `preprocess_dataset()`

```python
from src.data_preprocessor import preprocess_dataset

df, metadata = preprocess_dataset(
    excel_file_path="data/raw/input.xlsx",
    output_json="data/processed/data.json",
    output_csv="data/processed/data.csv"
)

print(f"Processed {metadata['final_records']} records")
```

---

### 2. Embedding Generator (`embedding_generator.py`)

Convert text to fixed-size vectors for similarity search.

#### Class: `EmbeddingGenerator`

```python
from src.embedding_generator import EmbeddingGenerator

generator = EmbeddingGenerator(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    use_gpu=True
)
```

##### Methods

**`generate_embedding(text: str) -> np.ndarray`**
- Generate single embedding
- Returns: 384-dimensional vector
```python
embedding = generator.generate_embedding("What is ML?")
print(embedding.shape)  # (384,)
```

**`generate_embeddings_batch(texts: List[str], batch_size: int = 32, show_progress: bool = True) -> np.ndarray`**
- Generate embeddings for multiple texts
- Returns: Array of shape (N, 384)
```python
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = generator.generate_embeddings_batch(texts)
print(embeddings.shape)  # (3, 384)
```

**`save_embeddings(output_path: str = None) -> str`**
- Save embeddings to disk
- Returns: Path to saved file
```python
path = generator.save_embeddings("embeddings/vectors.npy")
```

**`load_embeddings(input_path: str) -> np.ndarray`**
- Load embeddings from disk
```python
embeddings = generator.load_embeddings("embeddings/vectors.npy")
```

**`get_similarity_score(text1: str, text2: str) -> float`**
- Calculate cosine similarity between two texts
- Returns: Score 0-1
```python
score = generator.get_similarity_score("Hello", "Hi there")
print(score)  # 0.85
```

**`find_similar_texts(query_text: str, texts: List[str], top_k: int = 5) -> List[Tuple[str, float]]`**
- Find top-k similar texts to query
- Returns: List of (text, similarity_score)
```python
results = generator.find_similar_texts(
    "What is AI?",
    ["Machine Learning...", "Deep Learning..."],
    top_k=2
)
for text, score in results:
    print(f"{text} - {score:.3f}")
```

#### Function: `generate_embeddings_from_data()`

```python
from src.embedding_generator import generate_embeddings_from_data

texts = ["Text 1", "Text 2"]
embeddings, path = generate_embeddings_from_data(texts)
print(f"Shape: {embeddings.shape}, Saved to: {path}")
```

---

### 3. Vector Database Handler (`vector_db_handler.py`)

FAISS-based similarity search engine.

#### Class: `FAISSVectorDatabase`

```python
from src.vector_db_handler import FAISSVectorDatabase

db = FAISSVectorDatabase(embedding_dim=384)
```

##### Methods

**`create_index() -> None`**
- Create L2 distance index
```python
db.create_index()
```

**`add_embeddings(embeddings: np.ndarray, texts: List[str], metadata: List[Dict] = None) -> None`**
- Add embeddings to index
```python
embeddings = np.random.rand(10, 384).astype(np.float32)
texts = ["text1", "text2", ...]
db.add_embeddings(embeddings, texts)
print(f"Index size: {db.index.ntotal}")  # 10
```

**`search(query_embedding: np.ndarray, top_k: int = 5) -> Tuple[List, List, List]`**
- Search for similar embeddings
- Returns: (similarities, texts, metadata)
```python
query_emb = np.random.rand(384).astype(np.float32)
sims, texts, metadata = db.search(query_emb, top_k=5)

for sim, text in zip(sims, texts):
    print(f"{text} - {sim:.3f}")
```

**`search_with_threshold(query_embedding, top_k: int = 5, threshold: float = 0.3) -> Tuple[List, List, List]`**
- Search with minimum similarity threshold
```python
sims, texts, metadata = db.search_with_threshold(
    query_emb,
    top_k=5,
    threshold=0.5  # Only results >= 0.5
)
```

**`save_index(index_path: str = None) -> str`**
- Save index to disk
```python
path = db.save_index("vector_db/faiss_index.bin")
```

**`load_index(index_path: str = None, metadata_path: str = None) -> None`**
- Load index from disk
```python
db.load_index(
    "vector_db/faiss_index.bin",
    "vector_db/metadata.json"
)
```

**`get_stats() -> Dict`**
- Get database statistics
```python
stats = db.get_stats()
print(f"Total embeddings: {stats['total_embeddings']}")
```

#### Function: `initialize_vector_db()`

```python
from src.vector_db_handler import initialize_vector_db

embeddings = np.random.rand(100, 384).astype(np.float32)
texts = ["text1", ..., "text100"]

db = initialize_vector_db(embeddings, texts)
```

---

### 4. Gemini API Integration (`gemini_integration.py`)

Interface to Google's Gemini LLM.

#### Class: `GeminiAPI`

```python
from src.gemini_integration import GeminiAPI

api = GeminiAPI(api_key="your_key_here")
```

##### Methods

**`generate_response(prompt: str, system_instruction: str = None) -> str`**
- Generate LLM response
- Returns: Generated text
```python
response = api.generate_response(
    "Explain machine learning in simple terms"
)
print(response)
```

**`generate_rag_response(question: str, context: str) -> str`**
- Generate RAG response using context
```python
context = "Machine Learning is a subset of AI..."
question = "What is machine learning?"

response = api.generate_rag_response(question, context)
print(response)
```

**`evaluate_answer(user_answer: str, retrieved_answer: str) -> Dict`**
- Evaluate user answer against reference
- Returns: Evaluation result dictionary
```python
result = api.evaluate_answer(
    user_answer="ML uses algorithms to learn",
    retrieved_answer="ML is a subset of AI that..."
)
print(result)  # {similarity_score, correctness, confidence, explanation}
```

**`test_connection() -> bool`**
- Test API connection
```python
if api.test_connection():
    print("✓ API working")
else:
    print("✗ API failed")
```

**`get_model_info() -> Dict`**
- Get model information
```python
info = api.get_model_info()
print(f"Model: {info['display_name']}")
print(f"Max tokens: {info['output_token_limit']}")
```

#### Function: `test_gemini_setup()`

```python
from src.gemini_integration import test_gemini_setup

if test_gemini_setup(api_key="your_key"):
    print("Setup successful")
```

---

### 5. Evaluation Metrics (`evaluation_metrics.py`)

6-Category Rubric-based evaluation system.

#### Class: `EvaluationMetrics`

```python
from src.evaluation_metrics import EvaluationMetrics

evaluator = EvaluationMetrics()
```

##### Methods

**`calculate_c1_prompt_foundations(similarity_score: float, retrieval_quality: float) -> float`**
- C1: Prompt Foundations (15%)
- Returns: Score 0-1
```python
c1_score = evaluator.calculate_c1_prompt_foundations(0.85, 0.80)
```

**`calculate_c2_design_patterns(answer_structure: float, context_usage: float) -> float`**
- C2: Design & Patterns (20%)
```python
c2_score = evaluator.calculate_c2_design_patterns(0.75, 0.80)
```

**`calculate_c3_iterative_refinement(refine_attempts: int, improvement_ratio: float) -> float`**
- C3: Iterative Refinement (20%)
```python
c3_score = evaluator.calculate_c3_iterative_refinement(2, 0.70)
```

**`calculate_c4_domain_application(domain_relevance: float, constraint_adherence: float) -> float`**
- C4: Domain Application (20%)
```python
c4_score = evaluator.calculate_c4_domain_application(0.85, 0.90)
```

**`calculate_c5_ethics_safety(bias_detection: float, hallucination_check: float) -> float`**
- C5: Ethics & Safety (15%)
```python
c5_score = evaluator.calculate_c5_ethics_safety(0.95, 0.85)
```

**`calculate_c6_metacognition(confidence_calibration: float, uncertainty_expression: float) -> float`**
- C6: Metacognition (10%)
```python
c6_score = evaluator.calculate_c6_metacognition(0.80, 0.75)
```

**`compute_overall_score(category_scores: Dict[str, float]) -> float`**
- Compute weighted overall score
- Returns: Score 0-1
```python
scores = {
    "C1_prompt_foundations": 0.85,
    "C2_design_patterns": 0.72,
    # ... all 6 categories
}
overall = evaluator.compute_overall_score(scores)
print(f"Overall: {overall:.3f}")
```

**`evaluate_answer(similarity_score: float, retrieved_answer: str, user_answer: str, confidence: float = 0.5) -> Dict`**
- Complete evaluation using 6-category rubric
- Returns: Complete evaluation result
```python
result = evaluator.evaluate_answer(
    similarity_score=0.85,
    retrieved_answer="ML is a subset of AI...",
    user_answer="Machine Learning is AI...",
    confidence=0.9
)

print(result["overall_score"])        # 0.768
print(result["category_scores"])      # {C1: ..., C2: ..., ...}
print(result["accuracy"])             # "correct"
```

**`get_evaluation_summary() -> Dict`**
- Get summary of all evaluations
```python
summary = evaluator.get_evaluation_summary()
print(f"Average score: {summary['average_score']:.3f}")
print(f"Total evaluations: {summary['total_evaluations']}")
```

**`save_evaluation_report(output_path: str = None) -> str`**
- Save report to JSON
- Returns: File path
```python
path = evaluator.save_evaluation_report()
print(f"Report saved: {path}")
```

---

### 6. RAG Pipeline (`rag_pipeline.py`)

Main orchestration engine combining all components.

#### Class: `RAGPipeline`

```python
from src.rag_pipeline import RAGPipeline

pipeline = RAGPipeline(load_from_saved=False)
```

##### Methods

**`add_documents(texts: List[str], metadata: List[Dict] = None) -> np.ndarray`**
- Add documents to system
- Returns: Generated embeddings
```python
texts = ["Document 1", "Document 2", ...]
embeddings = pipeline.add_documents(texts)
print(f"Added {len(texts)} documents")
```

**`retrieve_context(query: str, top_k: int = 5, threshold: float = 0.3) -> Tuple[List[str], List[float]]`**
- Retrieve relevant documents
- Returns: (documents, similarity_scores)
```python
docs, scores = pipeline.retrieve_context(
    "What is machine learning?",
    top_k=5
)
for doc, score in zip(docs, scores):
    print(f"{doc[:50]}... ({score:.3f})")
```

**`format_context(documents: List[str], max_length: int = 2000) -> str`**
- Format documents into context string
- Returns: Formatted context
```python
context = pipeline.format_context(docs)
```

**`generate_rag_response(query: str, top_k: int = 5, use_llm: bool = True) -> Dict`**
- Generate complete RAG response
- Returns: Response dictionary
```python
response = pipeline.generate_rag_response(
    "What is artificial intelligence?",
    top_k=5,
    use_llm=True
)

print(response["answer"])              # Generated answer
print(response["context"])             # Retrieved context
print(response["similarities"])        # Confidence scores
print(response["retrieved_documents"]) # Source documents
```

**`evaluate_user_answer(user_answer: str, query: str, correct_answer: str = None) -> Dict`**
- Evaluate user's answer
- Returns: Complete evaluation
```python
evaluation = pipeline.evaluate_user_answer(
    user_answer="My answer",
    query="The question",
    correct_answer="Expected answer"
)

print(f"Score: {evaluation['overall_score']}")
print(f"Accuracy: {evaluation['accuracy']}")
print(f"C1 Score: {evaluation['score_breakdown']['C1_Prompt_Foundations_15%']}")
```

**`save_to_disk(output_dir: str = None) -> None`**
- Save pipeline to disk
```python
pipeline.save_to_disk("vector_db/")
```

**`load_from_disk(input_dir: str = None) -> None`**
- Load pipeline from disk
```python
pipeline.load_from_disk("vector_db/")
```

**`get_system_status() -> Dict`**
- Get system status
```python
status = pipeline.get_system_status()
print(f"Vector DB size: {status['vector_db_size']}")
print(f"Gemini available: {status['gemini_api_available']}")
```

#### Function: `create_sample_rag_pipeline()`

```python
from src.rag_pipeline import create_sample_rag_pipeline

pipeline = create_sample_rag_pipeline()
```

---

## ⚙️ Configuration (`config/config.py`)

Global configuration settings.

```python
from config.config import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DIMENSION,
    TOP_K_RETRIEVAL,
    SIMILARITY_THRESHOLD,
    MAX_CONTEXT_LENGTH,
    GEMINI_MODEL,
    GENERATION_CONFIG,
    EVALUATION_METRICS,
    DATA_RAW_DIR,
    DATA_PROCESSED_DIR,
    VECTOR_DB_DIR,
    EMBEDDINGS_DIR,
    LOGS_DIR
)
```

### Key Configuration Variables

```python
# Paths
DATA_RAW_DIR = "data/raw"
DATA_PROCESSED_DIR = "data/processed"
EMBEDDINGS_DIR = "embeddings"
VECTOR_DB_DIR = "vector_db"
LOGS_DIR = "logs"

# Model Settings
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Retrieval Settings
TOP_K_RETRIEVAL = 5
SIMILARITY_THRESHOLD = 0.3
MAX_CONTEXT_LENGTH = 2000

# API Settings
GEMINI_MODEL = "gemini-1.5-flash"
GENERATION_CONFIG = {
    "temperature": 0.3,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024,
}

# Evaluation Weights (6-Category Rubric)
EVALUATION_METRICS = {
    "C1_prompt_foundations": 0.15,
    "C2_design_patterns": 0.20,
    "C3_iterative_refinement": 0.20,
    "C4_domain_application": 0.20,
    "C5_ethics_safety": 0.15,
    "C6_metacognition": 0.10,
}
```

---

## 🔗 Complete Workflow Example

```python
import pandas as pd
from src.rag_pipeline import RAGPipeline
from src.data_preprocessor import preprocess_dataset

# 1. Load and preprocess data
print("Step 1: Preprocessing data...")
df, metadata = preprocess_dataset("data/raw/questions.xlsx")

# 2. Extract texts
texts = df.iloc[:, 0].to list()

# 3. Create RAG pipeline
print("Step 2: Initializing RAG pipeline...")
pipeline = RAGPipeline()
pipeline.add_documents(texts)

# 4. Query the system
print("Step 3: Querying...")
response = pipeline.generate_rag_response("What is ML?")
print(f"Answer: {response['answer']}")
print(f"Confidence: {response['similarities'][0]:.3f}")

# 5. Evaluate answer
print("Step 4: Evaluating...")
evaluation = pipeline.evaluate_user_answer(
    user_answer="Machine learning is AI",
    query="What is ML?",
    correct_answer="ML is a subset of AI that..."
)

print(f"Overall Score: {evaluation['overall_score']:.3f}")
print(f"Category Scores:")
for cat, score in evaluation['score_breakdown'].items():
    print(f"  {cat}: {score:.3f}")

# 6. Save results
print("Step 5: Saving...")
pipeline.save_to_disk()
report_path = pipeline.evaluation_metrics.save_evaluation_report()
print(f"Report saved to: {report_path}")
```

---

## 📊 Response Data Structures

### RAG Response

```python
{
    "query": "What is machine learning?",
    "context": "Machine Learning is a subset of AI...",
    "answer": "Generated response from LLM...",
    "retrieved_documents": ["doc1", "doc2", ...],
    "similarities": [0.95, 0.87, ...],
    "used_llm": True
}
```

### Evaluation Result

```python
{
    "timestamp": "2024-01-15T10:30:45",
    "user_answer": "ML is AI...",
    "retrieved_answer": "ML is a subset of AI...",
    "similarity_score": 0.825,
    "accuracy": "correct",
    "confidence": 0.9,
    "category_scores": {
        "C1_prompt_foundations": 0.85,
        "C2_design_patterns": 0.72,
        "C3_iterative_refinement": 0.75,
        "C4_domain_application": 0.80,
        "C5_ethics_safety": 0.88,
        "C6_metacognition": 0.70
    },
    "overall_score": 0.768,
    "score_breakdown": {
        "C1_Prompt_Foundations_15%": 0.850,
        "C2_Design_Patterns_20%": 0.720,
        ...
    }
}
```

---

## 🚀 Performance Tips

1. **Batch Processing**: Use batch methods for multiple items
2. **Caching**: Store embeddings to avoid regeneration
3. **GPU Acceleration**: Use CUDA for embeddings
4. **Index Optimization**: Regularly rebuild FAISS index
5. **Context Limiting**: Keep context within limits

---

## 📚 See Also

- [README.md](README.md) - Project overview
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Installation steps
- [config/config.py](config/config.py) - All settings

---

**Version:** 1.0.0  
**Last Updated:** 2024
