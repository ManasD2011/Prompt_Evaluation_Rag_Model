# Models and Vector Database Documentation

## Vector Database Location

The vector database is located in: `rag_system/vector_db/`

### Files in Vector DB Directory:
- **faiss_index.bin** - FAISS index containing the embedded vectors
- **metadata.json** - Metadata for indexed documents (source, chunk info, etc.)

## Embedding Models

### Current Model Configuration
- **Model Name**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384
- **Type**: Sentence Transformers (HuggingFace)
- **Performance**: Fast and lightweight, suitable for CPU inference

### Model Location
Models are automatically downloaded and cached from HuggingFace on first use.

## Available Models

The system supports multiple embedding models. Available options:

1. **Fast & Light** (default)
   - Name: `sentence-transformers/all-MiniLM-L6-v2`
   - Dimension: 384
   - Speed: ⚡⚡⚡
   - Quality: ⭐⭐⭐

2. **Balanced**
   - Name: `sentence-transformers/all-mpnet-base-v2`
   - Dimension: 768
   - Speed: ⚡⚡
   - Quality: ⭐⭐⭐⭐

3. **High Quality**
   - Name: `sentence-transformers/all-roberta-large-v1`
   - Dimension: 1024
   - Speed: ⚡
   - Quality: ⭐⭐⭐⭐⭐

## Model Loader Usage

```python
from src.models.model_loader import ModelLoader

# Load embedding model
loader = ModelLoader()
model = loader.get_embedding_model()

# Get model info
info = loader.get_model_info()

# List available models
models = loader.list_available_models()
```

## LLM Models

The system integrates with two LLM providers:

### Gemini (Default)
- Model: `gemini-2.0-flash` (configurable)
- Provider: Google
- Configuration: `GEMINI_API_KEY` in `.env`

### OpenAI
- Model: `gpt-4o-mini` (configurable)
- Provider: OpenAI
- Configuration: `OPENAI_API_KEY` in `.env`

## Vector DB Structure

### Index Information
```python
{
    "index_type": "FAISS (Facebook AI Similarity Search)",
    "distance_metric": "L2 Euclidean",
    "dimension": 384,
    "entries": variable,
}
```

### Metadata Format
```json
{
    "0": {
        "text": "Document text content...",
        "source": "filename.csv",
        "doc_id": 0,
        "chunk_index": 0,
        "timestamp": "2026-04-02T20:30:58"
    }
}
```

## Managing Models

### Downloading Models
Models are automatically downloaded on first use. To pre-download:

```python
from src.models.model_loader import ModelLoader

loader = ModelLoader()
# This will download if not already present
model = loader.get_embedding_model("sentence-transformers/all-MiniLM-L6-v2")
```

### Changing Embedding Model
1. Update in `config/config.py`:
   ```python
   EMBEDDING_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
   EMBEDDING_DIMENSION = 768
   ```

2. Regenerate embeddings:
   ```bash
   python main.py --regenerate-embeddings
   ```

### Switching LLM Provider
Update in `.env`:
```env
LLM_PROVIDER=openai
```

## Model Performance Notes

- **GPU Support**: Models support CUDA/GPU acceleration when available
- **Memory Usage**: Models are cached in memory for performance
- **Batch Processing**: Supports batch generation for efficiency

## Directory Structure

```
rag_system/
├── models/
│   ├── __init__.py
│   └── model_loader.py         # Model management utilities
├── vector_db/
│   ├── faiss_index.bin         # FAISS vector index
│   └── metadata.json           # Document metadata
├── embeddings/
│   ├── embeddings.npy          # Generated embeddings
│   └── embeddings_metadata.json # Embedding metadata
└── config/
    └── config.py               # Configuration (EMBEDDING_MODEL_NAME, etc.)
```
