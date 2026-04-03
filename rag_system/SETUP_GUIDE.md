# RAG System - Complete Setup and Implementation Guide

## 🎯 Overview

This guide walks you through every step to set up and deploy the RAG (Retrieval-Augmented Generation) system with your datasets.

---

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Windows/Linux/Mac
- Internet connection (for downloading models)
- At least 4GB RAM (8GB+ recommended)
- GPU optional but recommended (NVIDIA CUDA for acceleration)

---

## 🚀 Complete Setup Steps

### Phase 1: Environment Setup (10 minutes)

#### Step 1.1: Clone/Navigate to Project
```bash
cd c:\Users\manas\OneDrive\Desktop\Software\ enhancement\Internship_Rag
cd rag_system
```

#### Step 1.2: Create Virtual Environment
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal.

#### Step 1.3: Verify Python Version
```bash
python --version  # Should be 3.8+
```

#### Step 1.4: Upgrade pip
```bash
python -m pip install --upgrade pip
```

---

### Phase 2: Install Dependencies (5-10 minutes)

#### Step 2.1: Install Requirements
```bash
pip install -r requirements.txt
```

This installs:
- **pandas** - Data manipulation
- **openpyxl** - Excel file handling
- **torch** - Machine learning framework
- **sentence-transformers** - Embedding generation
- **faiss-cpu** - Vector similarity search
- **google-generativeai** - Gemini LLM API
- **python-dotenv** - Environment variables
- And more...

#### Step 2.2: Verify Installation
```bash
python -c "import torch; import pandas; import faiss; print('✓ All imports successful')"
```

---

### Phase 3: Gemini API Setup (5 minutes)

#### Step 3.1: Get Free API Key
1. Open: https://aistudio.google.com/
2. Sign in with Google account
3. Click "Get API Key" button
4. Choose "Create API key in new project"
5. Copy the key

#### Step 3.2: Create .env File
**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Windows (CMD):**
```cmd
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

#### Step 3.3: Add Your API Key
Edit the `.env` file:
```
GEMINI_API_KEY=your_actual_api_key_here
```

#### Step 3.4: Test API Connection
```bash
python -c "from src.gemini_integration import test_gemini_setup; print(test_gemini_setup())"
```

Expected output:
```
✓ Gemini API Setup: SUCCESS
Model: Gemini 1.5 Flash
Input limit: 1000000 tokens
Output limit: 4096 tokens
```

---

### Phase 4: Prepare Your Dataset (10-15 minutes)

#### Step 4.1: Locate Your Excel Files
Path for Trinetri datasets:
```
C:\Users\manas\OneDrive\Desktop\Trinetri Datsets
```

#### Step 4.2: Verify Dataset Format
Your Excel file should have columns like:
- `question` / `queries`
- `answer` / `solutions`
- `context` / `description`
- `category` / `label`

**Example format:**
| Question | Answer | Context |
|----------|--------|---------|
| What is ML? | Machine Learning is... | AI Systems |
| How does... | ... | ... |

#### Step 4.3: Check Data Quality
```bash
python
>>> import pandas as pd
>>> df = pd.read_excel('C:/Users/manas/OneDrive/Desktop/Trinetri Datsets/yourfile.xlsx')
>>> print(df.shape)  # (rows, columns)
>>> print(df.columns)  # Column names
>>> print(df.head())  # First 5 rows
```

---

### Phase 5: Data Processing Pipeline (15-20 minutes)

#### Step 5.1: Run Data Preprocessing
```bash
python main.py
# Ensure .env has:
# TRINETRI_DATASET_DIR=C:\Users\manas\OneDrive\Desktop\Trinetri Datsets
```

**What happens:**
1. ✅ Loads Excel file
2. ✅ Removes null/duplicate values
3. ✅ Normalizes text (lowercase, remove special chars)
4. ✅ Saves to `data/processed/processed_data.json`
5. ✅ Saves to `data/processed/processed_data.csv`

**Output example:**
```
Loading Excel file: ...
Removed X rows with null values
Removed Y duplicate rows
Saved 234 records to JSON
```

#### Step 5.2: Verify Processed Data
```bash
# Check processed files
ls -la data/processed/

# View first few records
python
>>> import json
>>> with open('data/processed/processed_data.json') as f:
>>>     data = json.load(f)
>>> print(len(data))  # Number of records
>>> print(data[0])    # First record
```

---

### Phase 6: Generate Embeddings (20-30 minutes)

#### Step 6.1: Create Embeddings
This happens automatically when you select the processing option, but you can also run separately:

```python
from src.data_preprocessor import preprocess_dataset
from src.embedding_generator import generate_embeddings_from_data
import pandas as pd

# Load processed data
df = pd.read_csv('data/processed/processed_data.csv')

# Combine text columns
texts = (df.iloc[:, 0].astype(str)).tolist()

# Generate embeddings
embeddings, path = generate_embeddings_from_data(texts)

print(f"Generated embeddings shape: {embeddings.shape}")
print(f"Saved to: {path}")
```

**Expected output:**
```
Initializing embedding model: sentence-transformers/all-MiniLM-L6-v2
✓ Model loaded on device: cpu  # or cuda
✓ Embedding dimension: 384
Generating embeddings for 234 texts
✓ Generated embeddings shape: (234, 384)
```

---

### Phase 7: Build Vector Database (5-10 minutes)

#### Step 7.1: Create FAISS Index
```python
from src.embedding_generator import generate_embeddings_from_data
from src.vector_db_handler import initialize_vector_db
import pandas as pd

# Load data
df = pd.read_csv('data/processed/processed_data.csv')
texts = df.iloc[:, 0].astype(str).tolist()

# Generate embeddings
embeddings, _ = generate_embeddings_from_data(texts)

# Create and save FAISS index
db = initialize_vector_db(embeddings, texts)
```

**Output files created:**
- `vector_db/faiss_index.bin` - FAISS index
- `vector_db/metadata.json` - Metadata mapping

#### Step 7.2: Test Retrieval
```python
# Search your database
test_query = "What is your question?"
documents, similarities = db.search(embedded_query, top_k=5)

for i, (doc, sim) in enumerate(zip(documents, similarities)):
    print(f"{i+1}. {doc[:100]}... (similarity: {sim:.3f})")
```

---

### Phase 8: Interactive RAG Session (Ongoing)

#### Step 8.1: Launch Interactive Mode
```bash
python main.py
# Auto-loads configured dataset path and opens RAG> prompt
```

#### Step 8.2: Try Commands
```
RAG> query What does machine learning mean?
RAG> eval My answer about machine learning

RAG> status
RAG> report
RAG> exit
```

---

### Phase 9: Evaluate Answers Using 6-Category Rubric

#### Step 9.1: Automatic Evaluation
```python
evaluation = pipeline.evaluate_user_answer(
    user_answer="Your answer here",
    query="The question"
)

print(f"Overall Score: {evaluation['overall_score']:.3f}")
print(f"Category Scores:")
for category, score in evaluation['score_breakdown'].items():
    print(f"  {category}: {score:.3f}")
```

#### Step 9.2: Interpret Scores

**Overall Score:**
- 0.9-1.0 = Excellent ⭐⭐⭐
- 0.8-0.9 = Very Good ⭐⭐
- 0.6-0.8 = Good ⭐
- 0.3-0.6 = Fair ⚠️
- 0.0-0.3 = Poor ❌

**Category Breakdown:**
- **C1 (15%)** - Semantic understanding
- **C2 (20%)** - Answer structure and context use
- **C3 (20%)** - Refinement capabilities
- **C4 (20%)** - Domain-specific correctness
- **C5 (15%)** - Safety and ethics
- **C6 (10%)** - Confidence calibration

---

## 📊 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ 1. DATA PREPARATION                                      │
│ - Load Excel file (.xlsx)                               │
│ - Clean: Remove nulls, duplicates, normalize text       │
│ - Export: JSON + CSV format                             │
│ Output: data/processed/processed_data.json              │
└──────────────┬──────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────┐
│ 2. EMBEDDING GENERATION                                  │
│ - Initialize sentence-transformers model               │
│ - Convert each text to 384-dim vector                   │
│ - Batch processing for efficiency                       │
│ Output: embeddings/embeddings.npy                       │
└──────────────┬──────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────┐
│ 3. VECTOR DATABASE                                       │
│ - Create FAISS index from embeddings                    │
│ - Store metadata and mappings                           │
│ - Enable fast similarity search                         │
│ Output: vector_db/faiss_index.bin                       │
└──────────────┬──────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────┐
│ 4. USER QUERY PROCESSING                                 │
│ - Encode query to embedding                             │
│ - Search FAISS index (find top-k similar)               │
│ - Retrieve matching documents                           │
└──────────────┬──────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────┐
│ 5. CONTEXT FORMATTING                                    │
│ - Format retrieved documents as context                 │
│ - Chunk context to max_length                           │
│ - Prepare for LLM input                                 │
└──────────────┬──────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────┐
│ 6. LLM GENERATION                                        │
│ - Use Gemini API with context + question                │
│ - Generate factual, grounded response                   │
│ - Include system prompt for safety                      │
└──────────────┬──────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────┐
│ 7. RESPONSE GENERATION                                   │
│ Output: { answer, context, confidence, documents }     │
└──────────────┬──────────────────────────────────────────┘
               ↓
┌─────────────────────────────────────────────────────────┐
│ 8. ANSWER EVALUATION                                     │
│ - Calculate semantic similarity                         │
│ - Apply 6-category rubric                               │
│ - Generate detailed evaluation                          │
│ Output: { score, accuracy, category_scores }            │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure After Setup

```
rag_system/
├── data/
│   ├── raw/
│   │   └── your_dataset.xlsx          ← Your input file
│   └── processed/
│       ├── processed_data.json        ← Cleaned data
│       ├── processed_data.csv         ← CSV format
│       └── preprocessing_metadata.json
├── embeddings/
│   ├── embeddings.npy                 ← Vector embeddings
│   └── embeddings_metadata.json
├── vector_db/
│   ├── faiss_index.bin                ← FAISS index
│   └── metadata.json                  ← Metadata
├── logs/
│   ├── rag_system.log
│   ├── preprocessing.log
│   ├── embeddings.log
│   ├── gemini_api.log
│   ├── evaluation.log
│   └── evaluation_report_*.json       ← Reports
├── config/
│   └── config.py                      ← Configuration
├── src/
│   ├── data_preprocessor.py
│   ├── embedding_generator.py
│   ├── vector_db_handler.py
│   ├── gemini_integration.py
│   ├── evaluation_metrics.py
│   └── rag_pipeline.py
├── requirements.txt
├── .env                               ← API key here
├── .env.example
├── main.py
└── README.md
```

---

## ⚡ Quick Command Reference

```bash
# Activate environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install packages
pip install -r requirements.txt

# Run main application
python main.py

# Run tests
python -m pytest tests/

# View logs
tail -f logs/rag_system.log

# Check GPU
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 🎯 Performance Benchmarks

| Component | Time | Resources |
|-----------|------|-----------|
| Load 1000 Excel rows | ~2s | 100MB |
| Preprocessing | ~5s | 200MB |
| Generate embeddings (1000 texts) | ~30s | 2GB (CPU) / 500MB (GPU) |
| Build FAISS index | ~2s | 200MB |
| Query retrieval | ~10ms | 50MB |
| LLM response generation | ~5s | 500MB |
| Answer evaluation | ~2s | 200MB |

---

## 📊 Expected Output Examples

### Preprocessing Output
```
=======================================================
Preprocessing Summary:
  Initial records: 1000
  Null values removed: 23
  Duplicates removed: 15
  Normalized records: 962
  Final records: 962
=======================================================
✓ Saved 962 records to JSON: data/processed/processed_data.json
✓ Saved 962 records to CSV: data/processed/processed_data.csv
```

### RAG Query Output
```
=======================================================
RAG RESPONSE GENERATION
=======================================================
Query: What is machine learning?

Answer:
Machine Learning is a subset of Artificial Intelligence that 
enables computer systems to learn and improve from experience 
without being explicitly programmed...

Retrieved Documents: 5
Top Confidence: 0.875
=======================================================
```

### Evaluation Output
```
=======================================================
EVALUATION RESULTS
=======================================================
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
=======================================================
```

---

## 🔧 Troubleshooting During Setup

### Issue: "Python not found"
```bash
# Install Python 3.8+ from python.org
# Add to PATH
# Verify: python --version
```

### Issue: "Permission denied" (Linux/Mac)
```bash
chmod +x main.py
python main.py
```

### Issue: "pip: command not found"
```bash
python -m pip install --upgrade pip
```

### Issue: "ModuleNotFoundError"
```bash
# Reinstall requirements
pip uninstall -r requirements.txt -y
pip install -r requirements.txt --upgrade
```

### Issue: "CUDA not found" (GPU)
```bash
# It's okay - CPU works fine, just slower
# To use GPU later: conda install pytorch::pytorch -c pytorch
```

---

## ✅ Verification Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Gemini API key obtained
- [ ] `.env` file created with API key
- [ ] API connection tested (`test_gemini_setup`)
- [ ] Excel dataset located and verified
- [ ] Data preprocessing complete
- [ ] Embeddings generated
- [ ] FAISS index created
- [ ] Interactive session working
- [ ] Sample query working
- [ ] Evaluation working
- [ ] Report generated

---

## 🎓 Next Steps

1. **Customize Configuration**
   - Edit `config/config.py`
   - Adjust model, temperature, thresholds

2. **Add More Data**
   - Place Excel files in `data/raw/`
   - Run preprocessing and embedding generation

3. **Fine-tune Evaluation**
   - Review 6-category rubric weights
   - Adjust based on your use case

4. **Deploy to Production**
   - Set up logging and monitoring
   - Implement caching layer
   - Consider API wrapper

5. **Optimization**
   - Test different embedding models
   - Implement query caching
   - Add batch inference

---

## 📚 Additional Resources

- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [FAISS Tutorial](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- [Sentence Transformers](https://www.sbert.net/)
- [Gemini API Docs](https://ai.google.dev/docs)

---

**Last Updated:** 2024  
**Status:** ✅ Production Ready
