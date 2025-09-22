# app.py

import streamlit as st
import os
import re
import json
import psutil
from datetime import datetime
from docx import Document
from docx.shared import Inches
from config import OUTPUT_DIR

# --- Helper Function for Saving Documents ---
def save_document(filename: str, title: str, final_content: list, visual_mapping: dict):
    """
    Saves the final content, including text and generated visuals, into a .docx file.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    doc = Document()
    doc.add_heading(title, level=1)
    
    for section in final_content:
        doc.add_heading(section['topic'], level=2)
        
        # Use regex to find all placeholders and text chunks in the section's content
        parts = re.split(r'(\[IMAGE\|.*?\]|\[CHART\|.*?\])', section['content'])
        
        for part in parts:
            if not part.strip():
                continue

            # Handle image placeholders
            if part.startswith('[IMAGE|'):
                if part in visual_mapping and visual_mapping.get(part):
                    try:
                        doc.add_picture(visual_mapping[part], width=Inches(6.0))
                    except Exception as e:
                        doc.add_paragraph(f"[Error adding image: {e}]", style='Comment')
                else:
                    doc.add_paragraph(f"[Visual generation failed for: {part}]", style='Comment')

            # Handle chart placeholders
            elif part.startswith('[CHART|'):
                if part in visual_mapping and visual_mapping.get(part):
                    try:
                        doc.add_picture(visual_mapping[part], width=Inches(6.0))
                    except Exception as e:
                        doc.add_paragraph(f"[Error adding chart: {e}]", style='Comment')
                else:
                    doc.add_paragraph(f"[Visual generation failed for: {part}]", style='Comment')

            # Handle regular text (which might contain markdown tables)
            else:
                if part.strip().startswith('|') and '|' in part:
                    try:
                        lines = [line.strip() for line in part.strip().split('\n')]
                        header = [h.strip() for h in lines[0].strip('|').split('|')]
                        table_data = []
                        for line in lines[2:]:  # Skip header and separator
                            row = [r.strip() for r in line.strip('|').split('|')]
                            table_data.append(row)
                        
                        table = doc.add_table(rows=1, cols=len(header))
                        table.style = 'Table Grid'
                        hdr_cells = table.rows[0].cells
                        for i, h in enumerate(header):
                            hdr_cells[i].text = h
                        for row_data in table_data:
                            row_cells = table.add_row().cells
                            for i, cell_data in enumerate(row_data):
                                row_cells[i].text = cell_data
                    except Exception as e:
                        doc.add_paragraph(f"[Error rendering table: {e}]\n{part}")
                else:
                    doc.add_paragraph(part)
    
    sanitized_filename = filename.replace(" ", "_").lower()
    filepath = os.path.join(OUTPUT_DIR, f"{sanitized_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx")
    doc.save(filepath)
    return filepath

# --- STREAMLIT APP ---
st.set_page_config(layout="wide")
st.title("🎓 PhD-Level Agentic Researcher")
st.write("An advanced agent for drafting, refining, and generating multimodal research documents entirely on-device.")

# --- STATE MANAGEMENT ---
if 'agent' not in st.session_state: st.session_state.agent = None
if 'image_agent' not in st.session_state: st.session_state.image_agent = None
if 'chart_agent' not in st.session_state: st.session_state.chart_agent = None
if 'document_sections' not in st.session_state: st.session_state.document_sections = []
if 'outline' not in st.session_state: st.session_state.outline = ""
if 'doc_title' not in st.session_state: st.session_state.doc_title = ""
if 'metrics' not in st.session_state: st.session_state.metrics = None

# --- SIDEBAR FOR MODEL LOADING ---
with st.sidebar:
    st.header("⚙️ Configuration")
    hardware_mode = st.radio("Select LLM Acceleration:", ("CPU", "Hybrid", "GPU"), help="Choose how to run the language model.")
    
    if st.button("Load All On-Device Models"):
        # Imports are moved here to allow the app to start even if models are missing
        from agent_core import ContentAgent
        from local_llm_loader import load_local_llm
        from image_generator import LocalImageGenerator
        from data_visualizer import DataVisualizer
        try:
            with st.spinner("Loading Language Model..."):
                st.session_state.llm = load_local_llm(mode=hardware_mode.lower())
                st.session_state.agent = ContentAgent(st.session_state.llm)
            st.success("Language Model Loaded!")
            
            with st.spinner("Loading On-Device Image Model..."):
                st.session_state.image_agent = LocalImageGenerator()
            st.success("Image Model Loaded!")

            st.session_state.chart_agent = DataVisualizer()
            st.success("Data Visualizer Ready!")
        except Exception as e:
            st.error(f"A critical error occurred during model loading: {e}", icon="🚨")

# --- MAIN APP WORKFLOW ---

# Stage 1: User Input and Initial Draft Generation
if st.session_state.agent:
    st.header("1. Define Your Research Paper")
    doc_title_input = st.text_input("Paper Title:", "The Synergistic Potential of Quantum Computing and AI")
    user_request = st.text_area("Research Abstract/Request:", "Explore the intersection of quantum computing and artificial intelligence. Discuss how quantum algorithms could revolutionize machine learning models, the current hardware challenges, and the long-term ethical implications of this technological fusion.", height=150)
    
    if st.button("✍️ Generate Initial Draft"):
        st.session_state.doc_title = doc_title_input
        with st.spinner("The agent is conducting its initial research and writing the first draft..."):
            st.session_state.outline, st.session_state.document_sections, st.session_state.metrics = st.session_state.agent.run_initial_draft(user_request, st.session_state.doc_title)
        st.rerun()
else:
    st.warning("Please load the on-device models using the sidebar to begin.")

# Stage 2: Display Performance Metrics (if available)
if st.session_state.metrics:
    st.header("📊 Performance Metrics (Initial Draft)")
    metrics = st.session_state.metrics
    cpu_percent = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Generation Time", f"{metrics['total_time']:.2f} s")
    col2.metric("Outline Time", f"{metrics['outline_time']:.2f} s")
    col3.metric("CPU Usage (End)", f"{cpu_percent}%")
    col4.metric("Memory Usage (End)", f"{memory_info.percent}%")

    st.write(f"**Total Sections Generated:** {metrics['total_sections']}")
    with st.expander("View detailed section generation times"):
        for i, sec_time in enumerate(metrics['section_times']):
            st.write(f"- Section {i+1}: {sec_time:.2f} seconds")

# Stage 3: Review and Refine the Draft
if st.session_state.document_sections:
    st.header("2. Review and Refine the Draft")
    st.info("Review each section below. You can provide feedback and regenerate sections individually.")

    for i, section in enumerate(st.session_state.document_sections):
        with st.container(border=True):
            st.subheader(f"Section: {section['topic']}")
            st.markdown(section['content'])
            
            feedback = st.text_area("Your Feedback for this section:", key=f"feedback_{i}", placeholder="e.g., 'Can you add a bar chart comparing performance?' or 'Elaborate on the ethical concerns.'")
            
            if st.button("🔄 Regenerate Section", key=f"regen_{i}"):
                with st.spinner("The agent is revising this section based on your feedback..."):
                    revised_content = st.session_state.agent.regenerate_section(
                        document_title=st.session_state.doc_title,
                        full_outline=st.session_state.outline,
                        section_topic=section['topic'],
                        original_content=section['content'],
                        user_feedback=feedback
                    )
                    st.session_state.document_sections[i]['content'] = revised_content
                    st.rerun()

# Stage 4: Finalize and Build the Multimodal Document
if st.session_state.document_sections:
    st.header("3. Finalize and Build Document")
    
    if st.button("✅ Finalize and Build .docx File", type="primary"):
        with st.spinner("Finalizing document... This may take a while if visuals are being generated."):
            visual_mapping = {}
            visual_prompts = []
            
            st.write("Parsing document for visual elements...")
            for section in st.session_state.document_sections:
                # Find artistic images: [IMAGE|widthxheight: prompt]
                images = re.findall(r'(\[IMAGE\|(\d+)x(\d+):\s*(.*?)\])', section['content'])
                for full_match, width, height, prompt in images:
                    visual_prompts.append({'type': 'image', 'full_match': full_match, 'prompt': prompt, 'width': int(width), 'height': int(height)})
                
                # Find data charts: [CHART|type: {...}]
                charts = re.findall(r'(\[CHART\|(bar|pie):\s*({.*?})\])', section['content'], re.DOTALL)
                for full_match, chart_type, json_data in charts:
                    visual_prompts.append({'type': 'chart', 'full_match': full_match, 'chart_type': chart_type, 'json_data': json_data})

            st.write(f"Found {len(visual_prompts)} visual elements to generate.")

            if visual_prompts:
                for i, visual in enumerate(visual_prompts):
                    st.write(f"  - ({i+1}/{len(visual_prompts)}) Generating {visual['type']}: {visual['full_match'][:70]}...")
                    
                    filename = f"{st.session_state.doc_title.replace(' ', '_').lower()}_visual_{i+1}"
                    
                    if visual['type'] == 'image' and st.session_state.image_agent:
                        img_path = st.session_state.image_agent.generate(
                            visual['prompt'], filename, visual['width'], visual['height']
                        )
                        visual_mapping[visual['full_match']] = img_path

                    elif visual['type'] == 'chart' and st.session_state.chart_agent:
                        chart_path = st.session_state.chart_agent.generate_chart(
                            visual['chart_type'], visual['json_data'], filename
                        )
                        visual_mapping[visual['full_match']] = chart_path

            st.write("Assembling the final .docx file...")
            filepath = save_document(
                st.session_state.doc_title,
                st.session_state.doc_title,
                st.session_state.document_sections,
                visual_mapping
            )
            st.success(f"Document successfully built and saved! ✨")
            st.markdown(f"**Download from:** `{filepath}`")