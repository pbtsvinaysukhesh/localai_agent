import time
import re
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from config import MAX_NEW_TOKENS_PER_SECTION

class ContentAgent:
    def __init__(self, llm):
        self.llm = llm

    def _generate_outline(self, user_request: str, document_title: str) -> str:
        """Step 1 of CoT: Generate the document outline."""
        template = """
        You are a strategic planner. Your job is to create a detailed, bulleted outline for a document.
        The outline should be logical and cover all key aspects of the user's request.
        Do not write the content, only provide the outline points.
        
        USER'S REQUEST: "{user_request}"
        DOCUMENT TITLE: "{document_title}"

        Generate the bulleted outline:
        """
        prompt = PromptTemplate(input_variables=["user_request", "document_title"], template=template)
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        response = chain.invoke({"user_request": user_request, "document_title": document_title})
        return response.get("text", "")

    def _generate_section_content(self, document_title: str, full_outline: str, section_topic: str) -> str:
        """Step 2 of CoT: Generate content for a specific section based on the outline."""
        template = """
        You are an expert writer. You are currently writing one section of a larger document.
        You must focus ONLY on the specific section topic provided. Do not repeat the title or other sections.
        
        OVERALL DOCUMENT TITLE: "{document_title}"
        FULL DOCUMENT OUTLINE:
        {full_outline}

        Now, write a detailed and comprehensive section for the following topic: "{section_topic}"
        SECTION CONTENT:
        """
        prompt = PromptTemplate(input_variables=["document_title", "full_outline", "section_topic"], template=template)
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        # Override the default max_new_tokens for this specific task
        self.llm.client.max_new_tokens = MAX_NEW_TOKENS_PER_SECTION

        response = chain.invoke({
            "document_title": document_title,
            "full_outline": full_outline,
            "section_topic": section_topic
        })
        return response.get("text", "")

    def run(self, user_request: str, document_title: str):
        """
        Executes the full Chain of Thought process and collects performance metrics.
        """
        # --- Metrics Initialization ---
        metrics = {
            "total_time": 0,
            "outline_time": 0,
            "section_times": [],
            "total_sections": 0,
        }
        full_content = []
        
        start_time = time.time()

        # --- STEP 1: GENERATE OUTLINE ---
        print("CoT Step 1: Generating outline...")
        outline_start_time = time.time()
        outline_text = self._generate_outline(user_request, document_title)
        metrics["outline_time"] = time.time() - outline_start_time
        full_content.append(f"# {document_title}\n\n## Outline\n{outline_text}\n\n---")
        
        # Basic parsing of the outline. This can be improved with more complex regex.
        # It looks for lines starting with '*', '-', or a number followed by a period.
        outline_points = [p.strip() for p in re.findall(r'^[*\-0-9]+\.?\s(.+)', outline_text, re.MULTILINE)]
        
        if not outline_points:
            print("Warning: Could not parse outline. Proceeding with the full request as one section.")
            outline_points = [user_request] # Fallback
            
        metrics["total_sections"] = len(outline_points)
        print(f"CoT Step 1 Complete. Found {metrics['total_sections']} sections to generate.")

        # --- STEP 2: GENERATE CONTENT FOR EACH SECTION ---
        for i, section in enumerate(outline_points):
            print(f"CoT Step 2 ({i+1}/{metrics['total_sections']}): Generating content for '{section[:50]}...'")
            section_start_time = time.time()
            
            section_content = self._generate_section_content(document_title, outline_text, section)
            
            section_time = time.time() - section_start_time
            metrics["section_times"].append(section_time)
            
            # Use the original outline point as the heading
            full_content.append(f"## {section}\n\n{section_content.strip()}")
            print(f"Section {i+1} generated in {section_time:.2f} seconds.")

        metrics["total_time"] = time.time() - start_time
        
        final_document = "\n\n".join(full_content)
        return final_document, metrics