import os
import sys
import time
import json
import logging
import streamlit as st
import pypdfium2 as pdfium
from pathlib import Path
from PIL import Image
from io import BytesIO

# Add src to path for imports
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.append(src_path)

from ingestion_engine import IngestionEngine
from vector_engine import VectorEngine
from generation_engine import GenerationEngine

# --- CACHED ENGINES ---
@st.cache_resource
def get_vector_engine():
    return VectorEngine()

@st.cache_resource
def get_generation_engine():
    return GenerationEngine()

@st.cache_data
def render_pdf_previews(pdf_bytes):
    """
    Renders ALL PDF pages to images once and caches them.
    """
    images = []
    try:
        pdf = pdfium.PdfDocument(pdf_bytes)
        num_pages = len(pdf)
        for i in range(num_pages):
            page = pdf[i]
            # scale=0.3 is enough for preview and much faster than 0.5
            bitmap = page.render(scale=0.3)
            images.append(bitmap.to_pil())
        return images, num_pages
    except Exception as e:
        return [], 0

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="ZenithVault | Professional Document Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL LIGHT THEME CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* Main App Background */
    .stApp { 
        background-color: #ffffff; 
        color: #1a1a1a; 
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { 
        background-color: #fcfcfd; 
        border-right: 1px solid #eef0f2; 
        box-shadow: 2px 0 10px rgba(0,0,0,0.02);
    }
    
    /* Headings */
    h1, h2, h3 { 
        color: #111827 !important; 
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* Custom Title */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1a365d 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    /* Buttons */
    .stButton>button { 
        border-radius: 10px; 
        background-color: #2563eb !important; 
        color: #ffffff !important;
        border: none !important;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    .stButton>button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }

    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background-color: #ffffff;
        border: 1px solid #f3f4f6;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    [data-testid="stChatMessage"]:hover {
        transform: translateX(4px);
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #f1f5f9; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        color: #64748b;
        font-weight: 500;
        padding: 1rem 1.5rem;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom-color: #2563eb !important;
        font-weight: 700;
    }

    /* Cards/Containers */
    .preview-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 8px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .preview-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
    }

    /* Chat Input */
    .stChatInputContainer {
        border-radius: 12px !important;
        box-shadow: 0 -4px 12px rgba(0,0,0,0.03);
    }
    
    /* Alert Tweaks */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False
if "current_collection" not in st.session_state:
    st.session_state.current_collection = None

# --- SIDEBAR: CONTROL CENTER ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=60)
    st.markdown("### ZenithVault")
    st.caption("v1.0 Professional Edition")
    st.divider()

    uploaded_file = st.file_uploader("📂 Upload Technical PDF", type="pdf")

    if uploaded_file:
        temp_path = Path("temp_upload.pdf")
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("File Ready for Analysis")
        
        try:
            pdf_bytes = uploaded_file.getvalue()
            pdf = pdfium.PdfDocument(pdf_bytes)
            max_pages = len(pdf)
        except Exception as e:
            st.error(f"Format Error: {e}")
            max_pages = 0

        if max_pages > 0:
            with st.expander("⚙️ Advanced Parsing Options", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    skip_start = st.number_input("Skip Pages (Start)", 0, max_pages-1, 0)
                with col2:
                    skip_end = st.number_input("Skip Pages (End)", 0, max_pages-1, 0)

                start_pg = int(skip_start) + 1
                end_pg = max_pages - int(skip_end)
                
                collection_name = st.text_input("Collection ID", value=uploaded_file.name.split('.')[0][:15])
                
                if start_pg > end_pg:
                    st.warning("⚠️ Invalid range")
                else:
                    st.info(f"Targets: Page {start_pg} to {end_pg}")

            if st.button("🚀 EXECUTE INDEXING"):
                if start_pg > end_pg:
                    st.error("Invalid range configuration.")
                else:
                    with st.status("🛠️ System Initializing...", expanded=True) as status:
                        try:
                            st.write("🔍 Analyzing document layout...")
                            ingestor = IngestionEngine()
                            abs_temp_path = str(temp_path.absolute())
                            chunks_path = ingestor.process_pdf(abs_temp_path, page_range=(start_pg, end_pg))
                            
                            st.write("🧠 Generating vector embeddings...")
                            v_engine = get_vector_engine()
                            v_engine.populate_from_json(chunks_path, collection_name)
                            
                            st.session_state.pdf_processed = True
                            st.session_state.current_collection = collection_name
                            status.update(label="✅ Indexing Complete", state="complete", expanded=False)
                            st.toast("Document Ready!", icon="✅")
                        except Exception as e:
                            status.update(label="❌ Critical Error", state="error")
                            st.error(f"Pipeline Failure: {e}")

# --- MAIN INTERFACE ---
st.markdown('<h1 class="main-title">ZenithVault Intelligence</h1>', unsafe_allow_html=True)
st.caption("Enterprise-grade technical document reasoning powered by Docling & Qwen2.5 (1.5B)")

tab1, tab2 = st.tabs(["💬 Technical Query Chat", "📄 Full Document Preview"])

with tab2:
    if uploaded_file:
        st.subheader(f"Document: {uploaded_file.name}")
        
        # --- RENDER ALL PAGES ---
        with st.spinner("Rendering document preview..."):
            preview_images, total_pgs = render_pdf_previews(uploaded_file.getvalue())
        
        if preview_images:
            st.markdown(f"**Total Pages:** {total_pgs}")
            # Dynamic grid based on total pages
            cols_per_row = 4
            for i in range(0, len(preview_images), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(preview_images):
                        with row_cols[j]:
                            idx = i + j
                            is_active = (idx + 1 >= start_pg and idx + 1 <= end_pg) if 'start_pg' in locals() else True
                            border_color = "#3b82f6" if is_active else "#e2e8f0"
                            opacity = "1" if is_active else "0.5"
                            
                            st.markdown(f"""
                                <div class="preview-card" style="border-color: {border_color}; opacity: {opacity}">
                                    <p style="text-align: center; font-size: 0.8rem; font-weight: 600; margin-bottom: 4px;">Page {idx+1}</p>
                                </div>
                            """, unsafe_allow_html=True)
                            st.image(preview_images[idx], use_container_width=True)
        else:
            st.error("Unable to generate preview.")
    else:
        st.info("Please upload a document to begin.")

with tab1:
    chat_container = st.container(height=550)
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 Hello! Upload a document and index it to start asking technical questions.")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask a technical question..."):
        if not st.session_state.pdf_processed:
            st.warning("⚠️ Action Required: Please process the document first.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    try:
                        v_engine = get_vector_engine()
                        with st.spinner("Retrieving relevant context..."):
                            results = v_engine.query(st.session_state.current_collection, prompt)
                        
                        context_chunks = results['documents'][0]
                        gen_engine = get_generation_engine()
                        
                        with st.spinner("Reasoning with LLM..."):
                            answer = gen_engine.generate_answer(prompt, context_chunks)
                        
                        st.markdown(answer)
                        
                        with st.expander("📚 Evidence & Sources"):
                            for i, meta in enumerate(results['metadatas'][0]):
                                pgs = json.loads(meta['page_numbers'])
                                st.markdown(f"**Source {i+1}** (Page {pgs})")
                                st.code(context_chunks[i], language="markdown")
                                
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Generation Error: {e}")
