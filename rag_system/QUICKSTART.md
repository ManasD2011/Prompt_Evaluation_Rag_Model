# 🚀 RAG System - Quick Start Guide

Complete RAG system ready to use! Follow these 5 simple steps to get started.

---

## ✅ What's Included

✅ Complete Python RAG pipeline  
✅ Data preprocessing (Excel → JSON/CSV)  
✅ Embedding generation (384-dim vectors)  
✅ FAISS vector database for similarity search  
✅ Google Gemini LLM integration  
✅ 6-Category evaluation rubric  
✅ Production-ready code with logging  
✅ Comprehensive documentation  

---

## 🎯 5-Minute Quick Start

### Step 1: Setup Environment (2 min)
```bash
cd c:\Users\manas\OneDrive\Desktop\Software\ enhancement\Internship_Rag\rag_system

# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Gemini API (2 min)
```bash
# Copy template
copy .env.example .env

# Edit .env and add your free API key
# Get key at: https://aistudio.google.com/
```

Edit `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

### Step 3: Test Installation (1 min)
```bash
python -c "from src.gemini_integration import test_gemini_setup; print(test_gemini_setup())"
```

### Step 4: Point To Your Dataset (- min)
```bash
# In .env, set:
# TRINETRI_DATASET_DIR=C:\path\to\your\excel_directory
```

### Step 5: Start CLI (-)
```bash
python main.py
# Auto-loads TRINETRI_DATASET_DIR and starts interactive mode
```

---

## 📊 Project Structure

```
rag_system/
├── data/                      # Your datasets
│   ├── raw/                   # Put Excel files here
│   └── processed/             # Auto-generated clean data
├── embeddings/                # Vector embeddings (auto-generated)
├── vector_db/                 # FAISS index (auto-generated)
├── config/
│   └── config.py              # ⚙️ All settings here
├── src/
│   ├── data_preprocessor.py   # Excel → JSON/CSV
│   ├── embedding_generator.py # Text → Vectors
│   ├── vector_db_handler.py   # Similarity search
│   ├── gemini_integration.py  # LLM API
│   ├── evaluation_metrics.py  # 6-Category scoring
│   └── rag_pipeline.py        # Main system
├── logs/                      # Auto-generated logs
├── main.py                    # Run this!
├── requirements.txt           # Dependencies
├── .env                       # ⚙️ Add API key here
├── README.md                  # Full documentation
├── SETUP_GUIDE.md             # Detailed setup
└── API_REFERENCE.md           # Function reference
```

---

## 🔄 Complete Workflow

```
Your Excel File
     ↓
[Preprocessing] → Clean data (JSON/CSV)
     ↓
[Embeddings] → Vector representations (384-dim)
     ↓
[FAISS Index] → Indexed vectors for fast search
     ↓
[User Query] → Encoded as vector
     ↓
[Retrieval] → Find top-5 similar documents
     ↓
[LLM Generation] → Generate answer with context
     ↓
[Evaluation] → Score using 6-category rubric
     ↓
JSON Result with all scores
```

---

## 📈 6-Category Evaluation Rubric

Your answers are scored on these 6 dimensions:

| Category | Weight | Measures |
|----------|--------|----------|
| **C1** Prompt Foundations | **15%** | Semantic understanding |
| **C2** Design & Patterns | **20%** | Answer structure & context use |
| **C3** Iterative Refinement | **20%** | Error correction ability |
| **C4** Domain Application | **20%** | Domain-specific correctness |
| **C5** Ethics & Safety | **15%** | Bias & hallucination detection |
| **C6** Metacognition | **10%** | Confidence & uncertainty |

**Overall Score = Weighted average of all 6 categories**

---

## 🎮 Interactive Commands

Once you run the system:

```
RAG> query Your question here?
     ↓ Returns: Answer, context, confidence

RAG> eval Your answer to the question
     ↓ Returns: Similarity score, accuracy, 6-category breakdown

RAG> status
     ↓ Shows: System info, embeddings count, API status

RAG> report
     ↓ Shows: Evaluation summary and statistics

RAG> exit
     ↓ Exits the system
```

---

## 📁 Your Dataset Format

Excel file should look like this:

```
| question | answer | context |
|----------|--------|---------|
| What is ML? | Machine Learning is... | AI Systems |
| How works? | It works by... | Algorithms |
```

**Column names don't matter** - system auto-detects text columns.

---

## 📊 Sample Output

### After Processing:
```
Processing Summary:
  Initial records: 1000
  Null values removed: 23
  Duplicates removed: 15
  Final clean records: 962
  ✓ Saved to: data/processed/
```

### After RAG Query:
```
Query: What is machine learning?

Answer:
Machine Learning is a subset of AI that enables 
systems to learn from data...

Retrieved: 5 documents
Confidence: 0.89
```

### After Evaluation:
```
Accuracy: CORRECT
Overall Score: 0.768 ⭐⭐⭐

6-Category Breakdown:
  C1 (Prompt Foundations):     0.850 ✓
  C2 (Design & Patterns):      0.720 ✓
  C3 (Iterative Refinement):   0.750 ✓
  C4 (Domain Application):     0.800 ✓
  C5 (Ethics & Safety):        0.880 ✓
  C6 (Metacognition):          0.700 ✓
```

---

## 🐛 Common Issues & Fixes

### "API key not found"
```bash
1. Create .env file
2. Add: GEMINI_API_KEY=your_key
3. Restart Python
```

### "No results retrieved"
```python
# Lower the threshold in config.py:
SIMILARITY_THRESHOLD = 0.2  # From 0.3
```

### "Module not found"
```bash
pip install -r requirements.txt --upgrade
```

### "Memory error (GPU)"
```python
# In config.py, reduce batch size:
BATCH_SIZE_EMBEDDINGS = 16  # From 32
```

---

## 🔗 File Directory Mapping

| Action | File/Folder |
|--------|------------|
| **Setup** | `.env`, `requirements.txt` |
| **Configure** | `config/config.py` |
| **Add Data** | `data/raw/` (put Excel files here) |
| **Main Script** | `main.py` |
| **Source Code** | `src/` (6 modules) |
| **Documentation** | `README.md`, `SETUP_GUIDE.md`, `API_REFERENCE.md` |
| **Logs** | `logs/` (auto-created) |
| **Output** | `data/processed/`, `embeddings/`, `vector_db/` |

---

## ⚡ Performance

| Operation | Time | Resources |
|-----------|------|-----------|
| Load 1000 rows | ~2 sec | 100 MB |
| Preprocess | ~5 sec | 200 MB |
| Generate embeddings | ~30 sec (1000 texts) | 2 GB CPU |
| Query + Retrieve | ~10 ms | 50 MB |
| Generate answer (LLM) | ~5 sec | 500 MB |
| Evaluate | ~2 sec | 200 MB |

---

## 🎓 Learning Path

1. **Start Here** → This file (you are here!)
2. **Setup** → Follow SETUP_GUIDE.md
3. **Set Dataset Path** → Update `TRINETRI_DATASET_DIR` in `.env`
4. **Run CLI** → `python main.py`
5. **Customize** → Edit config/config.py
6. **Deep Dive** → Read API_REFERENCE.md
7. **Full Details** → Read README.md

---

## 📚 Documentation Files

- **README.md** - Complete feature overview and usage
- **SETUP_GUIDE.md** - Step-by-step installation guide
- **API_REFERENCE.md** - All functions and methods
- **This file** - Quick start (5 minutes)

---

## 🔑 API Key Setup (2 minutes)

### Get Free API Key:
1. Visit: https://aistudio.google.com/
2. Sign in with Google account
3. Click "Get API Key"
4. Copy the key
5. Paste into `.env` file

### Free Tier:
- ✅ 60 requests/minute
- ✅ Perfect for testing
- ✅ Full feature access
- 📈 Upgrade if needed

---

## 💡 Pro Tips

1. **Use GPU if available**: Embeddings run 10x faster
2. **Cache embeddings**: Don't regenerate every time
3. **Batch processing**: Process multiple files together
4. **Monitor logs**: Check `logs/` for all details
5. **Tune temperature**: Lower = more factual (in config)
6. **Adjust thresholds**: Find sweet spot for your data

---

## 🚀 Next Steps

### After Setup:
1. ✅ Verify all imports work
2. ✅ Test with sample data (Demo mode)
3. ✅ Add your Excel files to `data/raw/`
4. ✅ Run preprocessing
5. ✅ Query your data
6. ✅ Evaluate answers

### For Production:
1. Set up logging to external service
2. Implement caching layer
3. Add batch processing
4. Monitor API usage
5. Consider load balancing

---

## 📞 Troubleshooting Commands

```bash
# Check Python version
python --version

# Check virtual environment active
where python  # Windows
which python  # Linux/Mac

# Verify imports
python -c "import torch, pandas, faiss; print('✓ OK')"

# Check logs
tail -f logs/rag_system.log

# Test Gemini API
python -c "from src.gemini_integration import test_gemini_setup; print(test_gemini_setup())"
```

---

## 📊 Understanding the Scores

**Overall Score: 0.0 - 1.0**
- 0.9-1.0 = Excellent ⭐⭐⭐⭐⭐
- 0.8-0.9 = Very Good ⭐⭐⭐⭐
- 0.7-0.8 = Good ⭐⭐⭐
- 0.6-0.7 = Fair ⭐⭐
- < 0.6 = Needs Improvement ⭐

**Accuracy:**
- correct = Matches reference answer
- partially_correct = Some elements match
- incorrect = Doesn't match

**Category Scores (0-1 each):**
- Higher is better for all categories
- Each category has specific meaning
- Check API_REFERENCE.md for details

---

## ✨ System Capabilities

✅ Load Excel files (.xls, .xlsx)  
✅ Clean and normalize text data  
✅ Remove duplicates and null values  
✅ Generate semantic embeddings  
✅ Build FAISS vector index  
✅ Retrieve relevant documents  
✅ Generate LLM responses  
✅ Evaluate answer quality  
✅ Score using 6-category rubric  
✅ Save detailed reports  
✅ Monitor with logging  

---

## 🔗 Key Modules

| Module | Purpose | Key Function |
|--------|---------|--------------|
| `data_preprocessor.py` | Clean data | `preprocess_dataset()` |
| `embedding_generator.py` | Text→Vectors | `generate_embeddings_batch()` |
| `vector_db_handler.py` | Search index | `search()` |
| `gemini_integration.py` | LLM API | `generate_rag_response()` |
| `evaluation_metrics.py` | 6-Cat scoring | `evaluate_answer()` |
| `rag_pipeline.py` | Orchestration | `generate_rag_response()` |

---

## 🎯 Your Journey

```
START
  ↓
[Install Deps]
  ↓
[Get API Key]
  ↓
[Run Demo]
  ↓
[Add Your Data]
  ↓
[Process Data]
  ↓
[Query System]
  ↓
[Evaluate Answers]
  ↓
[View Reports]
  ↓
✓ DONE!
```

---

## 📞 Quick Help

**Issue**: ModuleNotFoundError
```bash
pip install -r requirements.txt --upgrade
```

**Issue**: GEMINI_API_KEY not found
```bash
# Check .env file exists and has your key
cat .env
```

**Issue**: "No results retrieved"
```python
# Reduce threshold in config.py
SIMILARITY_THRESHOLD = 0.2
```

---

## 🎉 Ready to Start?

```bash
cd rag_system
venv\Scripts\activate  # Windows
python main.py
```

System auto-loads your configured dataset path and enters `RAG>` interactive mode.

---

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** 2024  

For detailed info, see:
- README.md (full documentation)
- SETUP_GUIDE.md (detailed setup)
- API_REFERENCE.md (all functions)
