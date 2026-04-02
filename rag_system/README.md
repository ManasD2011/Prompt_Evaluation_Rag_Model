# RAG System - Retrieval-Augmented Generation Pipeline

A production-ready Retrieval-Augmented Generation (RAG) system that combines document retrieval with LLM capabilities to provide accurate, context-grounded answers. Features a comprehensive 6-category evaluation rubric for scoring responses.

## 📋 Table of Contents

1. [Project Structure](#project-structure)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Detailed Workflow](#detailed-workflow)
6. [6-Category Evaluation Rubric](#6-category-evaluation-rubric)
7. [API Setup](#api-setup)
8. [Configuration](#configuration)
9. [Usage Examples](#usage-examples)
10. [Troubleshooting](#troubleshooting)

---

## 📁 Project Structure

```
rag_system/
├── data/
│   ├── raw/                      # Original Excel files
│   └── processed/                # Cleaned JSON/CSV data
├── embeddings/                   # Generated vector embeddings
├── vector_db/                    # FAISS index and metadata
├── models/                       # Pre-trained models storage
├── config/
│   └── config.py                 # Central configuration
├── src/
│   ├── data_preprocessor.py      # Excel→JSON/CSV conversion
│   ├── embedding_generator.py    # Text→Embeddings
│   ├── vector_db_handler.py      # FAISS database
│   ├── gemini_integration.py     # Google Gemini API
│   ├── evaluation_metrics.py     # 6-category scoring
│   └── rag_pipeline.py           # Main orchestration
├── logs/                         # System logs
├── config/                       # Configuration files
├── requirements.txt              # Dependencies
├── .env.example                  # API key template
├── main.py                       # Entry point
└── README.md                     # This file
```

---

## ✨ Features

### 1. **Data Processing**
- ✅ Load data from Excel (.xls/.xlsx)
- ✅ Clean and preprocess text
- ✅ Remove null values and duplicates
- ✅ Export to JSON/CSV formats
- ✅ Preserve metadata

### 2. **Vector Embeddings**
- ✅ Sentence-transformers for embeddings
- ✅ Batch processing with GPU support
- ✅ Configurable embedding dimensions
- ✅ Efficient storage and retrieval

### 3. **Vector Database**
- ✅ FAISS for fast similarity search
- ✅ Cosine similarity metrics
- ✅ Configurable similarity thresholds
- ✅ Metadata management

### 4. **RAG Pipeline**
- ✅ Query encoding and retrieval
- ✅ Context formatting and injection
- ✅ LLM-based response generation
- ✅ Configurable context window

### 5. **Gemini API Integration**
- ✅ Google Gemini LLM integration
- ✅ Free tier support
- ✅ Configurable temperature and parameters
- ✅ Error handling and fallbacks

### 6. **6-Category Evaluation Rubric**
- ✅ C1: Prompt Foundations (15%)
- ✅ C2: Design & Patterns (20%)
- ✅ C3: Iterative Refinement (20%)
- ✅ C4: Domain Application (20%)
- ✅ C5: Ethics & Safety (15%)
- ✅ C6: Metacognition (10%)

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Windows/Linux/Mac
- 4GB+ RAM (8GB+ recommended)
- GPU optional but recommended

### Step 1: Clone/Setup Project
```bash
cd c:\Users\manas\OneDrive\Desktop\Software\ enhancement\Internship_Rag
cd rag_system
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Gemini API
```bash
# Copy template
cp .env.example .env

# Edit .env and add your API key
# GEMINI_API_KEY=your_key_here
```

### Step 5: Verify Installation
```bash
python main.py
# Select option 3 to test Gemini API
```

---

## ⚡ Quick Start

### Option A: Demo Mode (Sample Data)
```bash
python main.py
# Select option 1
```

This runs with 5 sample documents and doesn't require your own dataset.

### Option B: Use Your Excel Data
```bash
python main.py
# Select option 2
# Enter path to Excel file
```

### Option C: Interactive Python Session
```python
from src.rag_pipeline import RAGPipeline

# Initialize
pipeline = RAGPipeline()

# Add documents
pipeline.add_documents([
    "Your document 1",
    "Your document 2",
])

# Query
response = pipeline.generate_rag_response("Your question?")
print(response['answer'])

# Evaluate answer
evaluation = pipeline.evaluate_user_answer(
    user_answer="Your answer",
    query="Your question?"
)
print(evaluation['overall_score'])
```

---

## 📊 Detailed Workflow

### Step 1: Data Preprocessing

**Input:** Excel file (.xls/.xlsx)  
**Process:**
- Load Excel data
- Remove null values
- Detect and remove duplicates
- Normalize text (lowercase, remove noise)
- Validate text quality

**Output:** JSON and CSV files in `data/processed/`

```python
from src.data_preprocessor import preprocess_dataset

df, metadata = preprocess_dataset(
    excel_file_path="data/raw/my_data.xlsx",
    output_json="data/processed/data.json",
    output_csv="data/processed/data.csv"
)
print(f"Processed {metadata['final_records']} records")
```

### Step 2: Generate Embeddings

**Input:** Processed text data  
**Process:**
- Initialize sentence-transformers model
- Generate embeddings for each text
- Batch processing for efficiency
- Save to disk

**Output:** embeddings.npy file in `embeddings/`

```python
from src.embedding_generator import generate_embeddings_from_data

texts = ["text 1", "text 2", ...]
embeddings, path = generate_embeddings_from_data(texts)
print(f"Generated embeddings: {embeddings.shape}")
```

### Step 3: Build Vector Database

**Input:** Embeddings and original texts  
**Process:**
- Initialize FAISS index
- Add embeddings to index
- Create metadata mappings
- Save index to disk

**Output:** FAISS index in `vector_db/`

```python
from src.vector_db_handler import initialize_vector_db

db = initialize_vector_db(embeddings, texts)
print(f"Index contains {db.index.ntotal} vectors")
```

### Step 4: User Query Processing

**Input:** User query  
**Process:**
1. Encode query to embedding
2. Search FAISS index
3. Retrieve top-k similar documents
4. Format context
5. Send to Gemini LLM
6. Generate response

**Output:** Response with context and answer

```python
response = pipeline.generate_rag_response("What is...?")
print(f"Answer: {response['answer']}")
print(f"Context: {response['context']}")
print(f"Confidence: {response['similarities'][0]}")
```

### Step 5: Answer Evaluation

**Input:** User answer and reference answer  
**Process:**
1. Calculate semantic similarity
2. Apply 6-category rubric
3. Generate evaluation scores
4. Determine accuracy

**Output:** Detailed evaluation report

```python
evaluation = pipeline.evaluate_user_answer(
    user_answer="My answer",
    query="The question",
    correct_answer="Expected answer"
)
print(f"Overall Score: {evaluation['overall_score']}")
print(f"Accuracy: {evaluation['accuracy']}")
```

---

## 📈 6-Category Evaluation Rubric

This system evaluates answers using a sophisticated 6-category rubric:

### **C1 - Prompt Foundations (15%)**
- **Focus:** Understanding of mechanics (tokens, context window, temperature)
- **Measures:** Semantic similarity and retrieval quality
- **Score Formula:** 60% semantic similarity + 40% retrieval quality

### **C2 - Design & Patterns (20%)**
- **Focus:** Use of deliberate techniques (few-shot, chain-of-thought, role-playing)
- **Measures:** Answer structure and context usage
- **Score Formula:** 50% structure quality + 50% context effectiveness

### **C3 - Iterative Refinement (20%)**
- **Focus:** Diagnostic capability when prompts fail
- **Measures:** Number of refinement attempts and improvement
- **Score Formula:** 40% refinement attempts + 60% improvement ratio

### **C4 - Domain Application (20%)**
- **Focus:** Adaptation of constraints for specific fields (medical, legal, coding)
- **Measures:** Domain relevance and constraint adherence
- **Score Formula:** 50% domain relevance + 50% constraint adherence

### **C5 - Ethics & Safety (15%)**
- **Focus:** Awareness of bias, manipulation, and regulations (DPDP Act)
- **Measures:** Bias-free responses and hallucination detection
- **Score Formula:** 50% bias absence + 50% factual grounding

### **C6 - Metacognition (10%)**
- **Focus:** Identifying uncertainty and calibrating confidence
- **Measures:** Confidence calibration and uncertainty expression
- **Score Formula:** 50% confidence calibration + 50% uncertainty acknowledgment

### Example Evaluation Output
```json
{
  "overall_score": 0.78,
  "accuracy": "correct",
  "score_breakdown": {
    "C1_Prompt_Foundations_15%": 0.85,
    "C2_Design_Patterns_20%": 0.72,
    "C3_Iterative_Refinement_20%": 0.75,
    "C4_Domain_Application_20%": 0.80,
    "C5_Ethics_Safety_15%": 0.88,
    "C6_Metacognition_10%": 0.70
  }
}
```

---

## 🔑 API Setup

### Getting Gemini API Key

1. **Go to Google AI Studio:**
   - Visit: https://aistudio.google.com/

2. **Create API Key:**
   - Click "Get API Key" button
   - Select "Create API key in new project"
   - Copy your API key

3. **Add to .env:**
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Test Connection:**
   ```bash
   python main.py
   # Select option 3
   ```

### Free Tier Limits
- ✅ Free tier available
- ✅ 60 requests per minute
- ✅ Good for testing and development
- 📈 Upgrade for higher limits

---

## ⚙️ Configuration

Edit `config/config.py` to customize:

### Embedding Settings
```python
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384
BATCH_SIZE_EMBEDDINGS = 32
```

### RAG Settings
```python
TOP_K_RETRIEVAL = 5  # Documents to retrieve
SIMILARITY_THRESHOLD = 0.3  # Minimum score
MAX_CONTEXT_LENGTH = 2000  # Characters
```

### Gemini API Settings
```python
GEMINI_MODEL = "gemini-1.5-flash"
GENERATION_CONFIG = {
    "temperature": 0.3,  # Lower = more factual
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1024,
}
```

### Evaluation Weights
```python
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

## 💡 Usage Examples

### Example 1: Process Dataset and Create RAG
```python
from src.rag_pipeline import RAGPipeline
from src.data_preprocessor import preprocess_dataset
from src.embedding_generator import generate_embeddings_from_data
import pandas as pd

# 1. Preprocess data
df, metadata = preprocess_dataset("data/raw/questions.xlsx")

# 2. Extract texts
texts = df['question'].tolist() + df['answer'].tolist()

# 3. Generate embeddings
embeddings, _ = generate_embeddings_from_data(texts)

# 4. Create RAG pipeline
pipeline = RAGPipeline()
pipeline.add_documents(texts)

# 5. Query
response = pipeline.generate_rag_response("Tell me about RAG systems")
print(response['answer'])
```

### Example 2: Evaluate Multiple Answers
```python
evaluations = []

questions_answers = [
    ("What is ML?", "Machine Learning enables systems to learn from data"),
    ("How does DL work?", "Deep Learning uses neurons and layers"),
]

for question, answer in questions_answers:
    eval_result = pipeline.evaluate_user_answer(answer, question)
    evaluations.append(eval_result)
    
    print(f"Q: {question}")
    print(f"Score: {eval_result['overall_score']:.3f}")
    print(f"Accuracy: {eval_result['accuracy']}\n")

# Generate report
pipeline.evaluation_metrics.save_evaluation_report()
```

### Example 3: Batch Processing
```python
import glob

# Process all Excel files
for excel_file in glob.glob("data/raw/*.xlsx"):
    print(f"Processing {excel_file}...")
    
    df, metadata = preprocess_dataset(excel_file)
    texts = df.dropna().iloc[:, 0].tolist()
    
    embeddings, _ = generate_embeddings_from_data(texts)
    print(f"  ✓ Processed {len(texts)} documents")
```

---

## 🔍 Monitoring and Logs

All system activities are logged to `logs/`:

- `rag_system.log` - Main system logs
- `preprocessing.log` - Data preprocessing details
- `embeddings.log` - Embedding generation logs
- `gemini_api.log` - API call logs
- `evaluation.log` - Evaluation metrics logs

View logs:
```bash
# Real-time monitoring
tail -f logs/rag_system.log

# On Windows
Get-Content logs/rag_system.log -Tail -f
```

---

## 🛠️ Troubleshooting

### Issue: "GEMINI_API_KEY not found"
**Solution:**
1. Create `.env` file in project root
2. Add: `GEMINI_API_KEY=your_key_here`
3. Restart Python application

### Issue: "No results retrieved"
**Solution:**
1. Check similarity threshold: Lower it in config
2. Verify documents are properly embedded
3. Test with simple queries first

### Issue: "GPU memory error"
**Solution:**
1. Reduce `BATCH_SIZE_EMBEDDINGS` in config
2. Use CPU instead: Set `use_gpu=False`
3. Process data in smaller batches

### Issue: "Excel file not found"
**Solution:**
1. Check file path (use absolute path)
2. Verify file exists
3. Check permissions

### Issue: "Import errors"
**Solution:**
```bash
pip install -r requirements.txt --upgrade
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 📊 Expected Output

After running a complete RAG evaluate sequence:

```
EVALUATION RESULTS
==================
Accuracy: correct
Similarity Score: 0.825
Overall Score (Weighted): 0.768

6-CATEGORY RUBRIC SCORES:
  C1 - Prompt Foundations (15%): 0.850
  C2 - Design & Patterns (20%): 0.720
  C3 - Iterative Refinement (20%): 0.750
  C4 - Domain Application (20%): 0.800
  C5 - Ethics & Safety (15%): 0.880
  C6 - Metacognition (10%): 0.700
```

---

## 📝 Dataset Format

### Expected Excel Columns
```
| question        | answer                | category   |
|-----------------|----------------------|-----------|
| What is AI?     | AI is artificial...   | Technical |
| How AI works?   | AI uses algorithms... | Technical |
```

Any column names work - the system auto-detects text columns.

---

## ⚡ Performance Tips

1. **Faster Retrieval:**
   - Use FAISS index for >1000 documents
   - Tune `TOP_K_RETRIEVAL` parameter
   - Use GPU for embeddings

2. **Better Embeddings:**
   - Use larger models for accuracy
   - Fine-tune on domain-specific data
   - Cache embeddings

3. **Scaling:**
   - Use batch processing
   - Implement index optimization
   - Consider distributed setup

---

## 📄 References

- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence-Transformers](https://www.sbert.net/)
- [Google Gemini API](https://ai.google.dev/)
- [RAG Survey Paper](https://arxiv.org/abs/2311.04017)

---

## 📧 Support

For issues or questions:
1. Check `logs/` directory
2. Review troubleshooting section
3. Test with demo mode
4. Check configuration settings

---

## 📄 License

This RAG system is provided as-is for educational and research purposes.

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** ✅ Production Ready
