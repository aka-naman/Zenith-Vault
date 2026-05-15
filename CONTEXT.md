# 🛡️ ZenithVault -> Document Parser Context

This file serves as a comprehensive reference for the setup and migration of the **Document Parser** (formerly ZenithVault) RAG system into an air-gapped environment.

## 📋 Project Overview
- **Core Functionality**: Layout-aware PDF parsing (Docling), Vector storage (ChromaDB), and Technical Reasoning (Qwen2.5-1.5B).
- **Primary Tech Stack**: Python 3.11, Conda, Streamlit, PyTorch, Transformers.

## ⚙️ Environment Configuration
- **Python Version**: 3.11
- **Primary Working Directory**: `F:\FINAL REPORTS\New folder\rag\Zenith-Vault`
- **Target Storage Directory**: `F:\FINAL REPORTS\New folder\rag\zipssss`
- **Reasoning for F: Drive**: Lack of space on C: drive; all environments and AI caches are redirected to F:.

---

## 🚀 Air-Gapped Deployment Strategy

### Phase 1: Online PC Setup (F: Drive)
1. **Redirect Caches**:
   ```powershell
   setx HF_HOME "F:\FINAL REPORTS\New folder\rag\zipssss\AI_Cache\huggingface"
   setx DOCLING_MODELS_CACHE "F:\FINAL REPORTS\New folder\rag\zipssss\AI_Cache\docling"
   setx EASYOCR_MODULE_PATH "F:\FINAL REPORTS\New folder\rag\zipssss\AI_Cache\easyocr"
   ```
   *(Requires terminal restart after execution)*

2. **Conda Environment**:
   ```powershell
   conda create -p "F:\FINAL REPORTS\New folder\rag\zipssss\doc_parser_env" python=3.11 -y
   conda activate "F:\FINAL REPORTS\New folder\rag\zipssss\doc_parser_env"
   ```

3. **Installations**:
   ```powershell
   pip install -r requirements.txt
   conda install -c conda-forge conda-pack -y
   ```

4. **Model Download (Granular Steps)**:
   - **Docling**: `python -c "from docling.document_converter import DocumentConverter; DocumentConverter()"`
   - **Embeddings**: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')"`
   - **LLM**: `python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; AutoTokenizer.from_pretrained('Qwen/Qwen2.5-1.5B-Instruct'); AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-1.5B-Instruct')"`

5. **Packaging**:
   ```powershell
   conda pack -p "F:\FINAL REPORTS\New folder\rag\zipssss\doc_parser_env" -o "F:\FINAL REPORTS\New folder\rag\zipssss\doc_parser_env.tar.gz"
   ```

### Phase 2: Offline PC Transfer
**Required Files (USB):**
- `doc_parser_env.tar.gz`
- `AI_Cache/` (The full folder)
- `Zenith-Vault/` (The source code)

### Phase 3: Offline PC Execution
1. **Extraction**: `tar -xzf E:\doc_parser_env.tar.gz -C C:\doc_parser_env`
2. **Environment Variables**:
   ```powershell
   set HF_HOME="E:\AI_Cache\huggingface"
   set DOCLING_MODELS_CACHE="E:\AI_Cache\docling"
   set EASYOCR_MODULE_PATH="E:\AI_Cache\easyocr"
   ```
3. **Run**:
   ```powershell
   C:\doc_parser_env\Scripts\activate.bat
   streamlit run app.py --browser.gatherUsageStats False
   ```

---

## ⚠️ Issues & Resolutions Encountered

### 1. UI Rendering Bug (Streamlit Versioning)
- **Problem**: `st.image()` crashed with `TypeError: got an unexpected keyword argument 'use_container_width'`.
- **Solution**: Changed keyword to `use_column_width` in `app.py` for backward compatibility with older Streamlit versions often found in local environments.

### 2. HuggingFace Hub Offline Mode
- **Problem**: HF Hub attempts to check for updates online by default, causing connection errors in air-gapped zones.
- **Solution**: Explicitly set `os.environ["HF_HUB_OFFLINE"] = "1"` in `generation_engine.py` and `vector_engine.py`.

### 3. Disk Write Bottlenecks
- **Observation**: Downloads appeared "stuck" (e.g., at 45%).
- **Cause**: High internet speed (147MB/s) exceeding the write speed of the F: drive (HDD).
- **Resolution**: Implemented granular (one-by-one) download steps to prevent buffer overflows and allow disk write cycles.

### 4. Windows Path Limits & Symlinks
- **Observation**: Warning regarding `Symlinks` not supported on Windows without Developer Mode.
- **Impact**: Cached files take more space and download slightly slower, but functionality is preserved.
- **Resolution**: Use `tar.gz` for environment packing to safely handle long file paths during offline extraction.

---
**Status**: Ready for Offline Migration.
