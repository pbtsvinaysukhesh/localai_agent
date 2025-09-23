import streamlit as st
import os
import psutil
from datetime import datetime
from docx import Document
from agent_core import ContentAgent
from local_llm_loader import load_local_llm
from config import OUTPUT_DIR

# --- Helper Function for Saving Documents ---
def save_document(filename: str, title: str, content: str) -> str:
    """Saves the generated content as a .docx file, handling basic markdown."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    doc = Document()
    
    # We don't add the main title here as the content itself contains it.
    # The content starts with "# Title", which will be handled below.
    
    for paragraph in content.strip().split('\n'):
        if paragraph.strip():
            # Basic Markdown to DocX conversion
            if paragraph.startswith('# '):
                # We handle multiple levels of headings now
                heading_level = paragraph.count('#')
                doc.add_heading(paragraph.lstrip('# ').strip(), level=min(heading_level, 4))
            elif paragraph.startswith('## '):
                doc.add_heading(paragraph.lstrip('# ').strip(), level=2)
            elif paragraph.startswith('### '):
                doc.add_heading(paragraph.lstrip('# ').strip(), level=3)
            else:
                doc.add_paragraph(paragraph)
    
    sanitized_filename = filename.replace(" ", "_").lower()
    filepath = os.path.join(OUTPUT_DIR, f"{sanitized_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx")
    try:
        doc.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error saving document: {e}")
        return None

st.set_page_config(layout="wide")
st.title("📄 Advanced Local Content Agent (with Chain of Thought)")
st.write("This agent uses a multi-step process to generate long-form documents and reports its performance.")

if 'agent' not in st.session_state: st.session_state.agent = None
if 'llm' not in st.session_state: st.session_state.llm = None
if 'hardware_mode' not in st.session_state: st.session_state.hardware_mode = None

with st.sidebar:
    st.header("⚙️ Configuration")
    hardware_mode = st.radio("Select Hardware Acceleration:", ("CPU", "Hybrid", "GPU"))
    if st.button("Load LLM"):
        if st.session_state.hardware_mode != hardware_mode or st.session_state.llm is None:
            with st.spinner(f"Loading LLM in {hardware_mode} mode..."):
                try:
                    st.session_state.llm = load_local_llm(mode=hardware_mode.lower())
                    st.session_state.agent = ContentAgent(st.session_state.llm)
                    st.session_state.hardware_mode = hardware_mode
                    st.success("LLM and Agent loaded successfully!")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
        else:
            st.info("LLM is already loaded.")

st.header("📝 Create a New Document")

if st.session_state.agent:
    st.info(f"✅ Agent is ready (Mode: **{st.session_state.hardware_mode}**)")
    doc_title = st.text_input("Document Title:", "The Future of Decentralized AI")
    user_request = st.text_area("Content Request:", "Write a comprehensive report on decentralized AI. Cover the core concepts, benefits like censorship resistance, challenges such as scalability, and potential future applications.", height=150)

    if st.button("🚀 Generate Document with CoT"):
        if not doc_title.strip() or not user_request.strip():
            st.warning("Please provide both a title and a content request.")
        else:
            # --- FIX APPLIED HERE: Corrected try/except block structure ---
            try:
                with st.status("Agent is thinking...", expanded=True) as status:
                    status.update(label="Step 1: Generating Outline...")
                    generated_content, metrics = st.session_state.agent.run(user_request, doc_title)
                    
                    status.update(label="Step 2: Compiling document and saving...")
                    filepath = save_document(doc_title, doc_title, generated_content)
                    
                    status.update(label="Generation Complete!", state="complete")

                st.success("Document generation and saving complete!")
                st.markdown(f"**📄 Document saved to:** `{filepath}`")

                # --- Display Performance Metrics ---
                st.header("📊 Performance Metrics")
                
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Time", f"{metrics['total_time']:.2f} s")
                col2.metric("Outline Time", f"{metrics['outline_time']:.2f} s")
                col3.metric("CPU Usage (End)", f"{cpu_percent}%")
                col4.metric("Memory Usage (End)", f"{memory_info.percent}%")

                st.write(f"**Sections Generated:** {metrics['total_sections']}")
                with st.expander("View detailed section generation times"):
                    for i, sec_time in enumerate(metrics['section_times']):
                        st.write(f"- Section {i+1}: {sec_time:.2f} seconds")

                # --- Display Generated Content Preview ---
                with st.expander("Show Generated Content Preview", expanded=True):
                    st.markdown(generated_content)

            except Exception as e:
                # This 'except' now correctly corresponds to the 'try' block above
                st.error(f"A critical error occurred: {e}")
                # Also log to console for more details
                import traceback
                traceback.print_exc()

else:
    st.warning("Please load the LLM using the sidebar to begin.")