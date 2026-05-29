# 🛡️ PrivateVault
### Professional-Grade Technical Document Intelligence & Reasoning

**PrivateVault** is an enterprise-ready RAG (Retrieval-Augmented Generation) system designed for high-precision reasoning over complex technical documents, scientific papers, and industrial manuals. By combining **Docling's** layout-aware parsing with **Qwen2.5's** advanced reasoning capabilities, PrivateVault transforms static PDFs into interactive, searchable knowledge bases.

---

## 🌟 Key Features

- **High-Fidelity Ingestion**: Powered by `Docling`, PrivateVault recognizes complex document structures including hierarchical headings, tables, formulas, and nested sections.
- **Hierarchical Chunking**: Unlike standard RAG systems, PrivateVault maintains structural context by linking chunks to their parent headings and document metadata.
- **Modern Professional UI**: A polished, high-contrast light theme built with Streamlit, featuring a seamless chat experience and real-time document interaction.
- **Full PDF Preview**: Interactive document viewer with page range selection and visual feedback for skip/process settings.
- **Evidence-Backed Answers**: Every response includes an expandable "Evidence & Sources" section, showing the exact context blocks used by the LLM.
- **Local & Efficient**: Optimized to run on standard hardware using quantized models (Qwen2.5-1.5B) and efficient vector storage (ChromaDB).

---

## 🏗️ Architecture

PrivateVault is built on a robust three-engine modular architecture:

1.  **Ingestion Engine**: Orchestrates the conversion of PDFs into structured Markdown and JSON using `Docling`. It handles OCR, table extraction, and hierarchical chunking.
2.  **Vector Engine**: Manages the embedding generation (via `BGE-v1.5`) and persistent storage in `ChromaDB`. It uses an "augmented context" strategy to bake document structure into the vector space.
3.  **Generation Engine**: A professional RAG pipeline using `Qwen2.5-Instruct`. It leverages tailored system prompts to ensure factual accuracy and high-quality technical reasoning.

---

## 🚀 Installation

Follow these steps to set up PrivateVault on your local machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/PrivateVault.git
   cd PrivateVault
   ```

2. **Create a Virtual Environment**:
   It is highly recommended to use a virtual environment to manage dependencies:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Dashboard**:
   ```bash
   streamlit run app.py
   ```

---

## 💻 Terminal Usage (CLI)

PrivateVault also provides a powerful command-line interface for batch processing and automated queries:

### Ingest and Index a PDF
```bash
python main.py ingest "path/to/your/document.pdf" --collection "my_collection"
```

### Query the Collection
```bash
python main.py query --collection "my_collection" --text "Explain the primary results of this study."
```

---

## 🛠️ Technical Stack

- **UI Framework**: [Streamlit](https://streamlit.io/)
- **Document Parsing**: [Docling](https://github.com/DS4SD/docling) by IBM
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **Embeddings**: [BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
- **Large Language Model**: [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct)
- **PDF Rendering**: `pypdfium2`

---

## 📖 Usage Guide

1.  **Upload**: Drag and drop a technical PDF into the sidebar.
2.  **Configure**: Use the "Advanced Parsing Options" to skip cover pages or appendices if necessary.
3.  **Index**: Click **🚀 EXECUTE INDEXING**. The system will analyze the layout, generate embeddings, and prepare the database.
4.  **Query**: Use the chat tab to ask technical questions. View source context in the "Evidence" expander for full transparency.
5.  **Preview**: Check the "Document Preview" tab to see exactly which pages are being analyzed.

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for more information.

---
*PrivateVault — High-Accuracy Technical Document Reasoning*
"# Zenith-Vault" 
