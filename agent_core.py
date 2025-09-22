# agent_core.py

import time
import re
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config import MAX_NEW_TOKENS_PER_SECTION # This is now -1, which LangChain understands

class ContentAgent:
    def __init__(self, llm):
        self.llm = llm
        # Set the max_new_tokens for the entire session. 
        # -1 means unlimited generation until the model naturally stops.
        self.llm.client.max_new_tokens = MAX_NEW_TOKENS_PER_SECTION

    def _generate_outline(self, user_request: str, document_title: str) -> str:
        """Step 1 of CoT: Generate an academic outline."""
        template = """
        You are an esteemed academic researcher with a PhD in the relevant field.
        Your task is to create a comprehensive, well-structured, and detailed outline for a scholarly paper.
        The outline should follow a logical progression, suitable for a deep-dive analysis.
        Think about including sections for introduction, methodology (if applicable), core arguments, counter-arguments, case studies, future implications, and conclusion.
        
        USER'S REQUEST: "{user_request}"
        PAPER TITLE: "{document_title}"

        Generate the detailed, multi-level bulleted outline:
        """
        prompt = PromptTemplate(input_variables=["user_request", "document_title"], template=template)
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.invoke({"user_request": user_request, "document_title": document_title})
        return response.get("text", "")

    def _generate_section_content(self, document_title: str, full_outline: str, section_topic: str) -> str:
        """Step 2 of CoT: Generate content with placeholders for advanced visuals."""
        template = """
        You are an academic researcher writing a scholarly paper. Write with depth and an analytical tone.

        **CRITICAL INSTRUCTIONS FOR VISUALS:**
        To enhance the paper, you MUST embed placeholders for visuals where they would be most effective. You have two types of visuals at your disposal:

        1.  **ARTISTIC IMAGES:** For conceptual illustrations. Use this format:
            `[IMAGE|widthxheight: A descriptive prompt for an image generator. Be detailed.]`
            - `width` and `height` must be multiples of 64.
            - Choose an aspect ratio that fits the subject (e.g., `768x512` for landscape, `512x768` for portrait).

        2.  **DATA CHARTS:** To illustrate data or comparisons. Use this format:
            `[CHART|type: {{a valid JSON object with chart data and labels}}]`

        - `type` can be `bar` or `pie`.
        - The JSON MUST contain "title", "data" (as a dictionary of key:value pairs), and can contain "x_label" and "y_label".
        - Example for a bar chart: `[CHART|bar: {{"title": "Model Performance Comparison", "x_label": "Model", "y_label": "Accuracy (%)", "data": {{"GPT-3": 85, "Mistral-7B": 78, "LLaMA-2-13B": 82}}}}]`

        ---
        PAPER TITLE: "{document_title}"
        FULL OUTLINE:
        {full_outline}
        
        Now, write a comprehensive section for the following topic ONLY: "{section_topic}"
        SECTION CONTENT:
        """
        prompt = PromptTemplate(input_variables=["document_title", "full_outline", "section_topic"], template=template)
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.invoke({"document_title": document_title, "full_outline": full_outline, "section_topic": section_topic})
        return response.get("text", "")

    def regenerate_section(self, document_title: str, full_outline: str, section_topic: str, original_content: str, user_feedback: str) -> str:
        """CoT Refinement Step: Regenerates a section based on user feedback."""
        template = """
        You are an academic editor revising a draft. You have received feedback on a specific section.
        Your task is to rewrite the section, incorporating the user's suggestions while maintaining a scholarly tone.

        PAPER TITLE: "{document_title}"
        FULL OUTLINE:
        {full_outline}
        
        SECTION TOPIC: "{section_topic}"
        
        ORIGINAL DRAFT OF THE SECTION:
        ---
        {original_content}
        ---

        USER'S FEEDBACK FOR REVISION: "{user_feedback}"

        Now, provide the new, revised version of the section content based on the feedback:
        REVISED SECTION CONTENT:
        """
        prompt = PromptTemplate(input_variables=["document_title", "full_outline", "section_topic", "original_content", "user_feedback"], template=template)
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.invoke({
            "document_title": document_title,
            "full_outline": full_outline,
            "section_topic": section_topic,
            "original_content": original_content,
            "user_feedback": user_feedback
        })
        return response.get("text", "")

    def run_initial_draft(self, user_request: str, document_title: str):
        """Runs the initial draft generation (outline + sections)."""
        print("CoT Step 1: Generating academic outline...")
        outline_text = self._generate_outline(user_request, document_title)
        
        outline_points = [p.strip() for p in re.findall(r'^[*\-0-9]+\.?\s(.+)', outline_text, re.MULTILINE)]
        if not outline_points:
            outline_points = [user_request]
        
        print(f"Outline generated with {len(outline_points)} sections.")

        document_sections = []
        for i, section_topic in enumerate(outline_points):
            print(f"CoT Step 2 ({i+1}/{len(outline_points)}): Generating content for '{section_topic[:50]}...'")
            section_content = self._generate_section_content(document_title, outline_text, section_topic)
            document_sections.append({
                "topic": section_topic,
                "content": section_content.strip(),
                "feedback": "" 
            })
        
        return outline_text, document_sections