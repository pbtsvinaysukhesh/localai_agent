# agent_core.py

import time
import re

class ContentAgent:
    def __init__(self, llm):
        self.llm = llm
        self.llm.client.max_new_tokens = -1

    def _generate_response(self, prompt: str) -> str:
        """A direct method to call the LLM with the correct chat format for the model."""
        # This format is for Phi-3. If you switch back to Gemma, change it.
        formatted_prompt = f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"
        response = self.llm.invoke(formatted_prompt)
        return response

    def _generate_outline(self, user_request: str, document_title: str) -> str:
        # --- FIX: STRONGER, MORE DIRECT PROMPT ---
        prompt = f"""You are an expert academic researcher. Your task is to create a comprehensive, well-structured outline for a paper.

**CRITICAL REQUIREMENT:** You MUST format the outline as a simple, multi-level bulleted list. Each item MUST start with a hyphen '-'. Do not include any other text, explanations, or introductions. Begin the outline immediately.

USER REQUEST: "{user_request}"
PAPER TITLE: "{document_title}"

Begin the hyphenated bullet-point outline now:"""
        return self._generate_response(prompt)

    def _generate_section_content(self, document_title: str, full_outline: str, section_topic: str) -> str:
        prompt = f"""You are an academic researcher writing a specific section of a scholarly paper. Write with depth and clarity.
**VISUALS SYNTAX (IMPORTANT):**
- For images, use: `[IMAGE|widthxheight: A detailed description]`
- For charts, use: `[CHART|type: {{"title": "Title", "data": {{"key": "value"}}}}]`
DOCUMENT TITLE: "{document_title}"
FULL OUTLINE (for context):
{full_outline}
Your task is to write the content for this specific section topic ONLY: "{section_topic}"
Do NOT repeat the section title in your response. Begin writing the content immediately.
SECTION CONTENT:"""
        return self._generate_response(prompt)

    def generate_full_document(self, user_request: str, document_title: str) -> str:
        """
        A robust fallback method to generate the entire document in a single pass
        if the outline generation or parsing fails.
        """
        print("Executing robust fallback: Generating full document in a single pass.")
        prompt = f"""You are an expert academic researcher. Your task is to write a complete, well-structured paper based on the user's request.

The paper MUST include:
- A clear title.
- An introduction.
- Multiple sections with clear headings to structure the content.
- A conclusion.
- Placeholders for visuals like `[IMAGE|widthxheight: description]` and `[CHART|type: {{...}}]` where they would be most effective.

USER REQUEST: "{user_request}"
PAPER TITLE: "{document_title}"

Now, generate the complete, high-quality, and comprehensive paper from start to finish. Begin with the title.
"""
        return self._generate_response(prompt)

    def regenerate_section(self, document_title: str, full_outline: str, section_topic: str, original_content: str, user_feedback: str) -> str:
        prompt = f"""You are an expert academic editor revising a section based on user feedback.
DOCUMENT TITLE: "{document_title}"
SECTION TOPIC: "{section_topic}"
ORIGINAL DRAFT:\n---\n{original_content}\n---
USER FEEDBACK: "{user_feedback}"
Provide the new, revised version of the section content. Begin writing the revised content directly:
REVISED CONTENT:"""
        return self._generate_response(prompt)

    def run_initial_draft(self, user_request: str, document_title: str):
        metrics = {"total_time": 0, "outline_time": 0, "section_times": [], "total_sections": 0}
        full_start_time = time.time()

        print("CoT Step 1: Generating academic outline...")
        outline_start_time = time.time()
        outline_text = self._generate_outline(user_request, document_title)
        metrics["outline_time"] = time.time() - outline_start_time
        
        outline_points = [p.strip() for p in re.findall(r'^\s*-\s*(.+)', outline_text, re.MULTILINE)]
        
        # --- FIX: SMARTER FALLBACK LOGIC ---
        if not outline_points:
            print("Warning: Outline parsing failed. Executing robust fallback...")
            full_content = self.generate_full_document(user_request, document_title)
            metrics["total_sections"] = 1
            generation_time = time.time() - full_start_time
            metrics["total_time"] = generation_time
            metrics["section_times"].append(generation_time)
            # Package the full document into the expected format for the UI
            document_sections = [{"topic": document_title, "content": full_content.strip(), "feedback": ""}]
            return "Outline generation failed. Full document generated as fallback.", document_sections, metrics
        # ------------------------------------
        
        metrics["total_sections"] = len(outline_points)
        print(f"Outline parsing complete. Found {metrics['total_sections']} sections.")
        document_sections = []
        for i, section_topic in enumerate(outline_points):
            section_start_time = time.time()
            print(f"CoT Step 2 ({i+1}/{metrics['total_sections']}): Generating content for '{section_topic[:50]}...'")
            section_content = self._generate_section_content(document_title, outline_text, section_topic)
            section_time = time.time() - section_start_time
            metrics["section_times"].append(section_time)
            document_sections.append({"topic": section_topic, "content": section_content.strip(), "feedback": ""})
        
        metrics["total_time"] = time.time() - full_start_time
        return outline_text, document_sections, metrics