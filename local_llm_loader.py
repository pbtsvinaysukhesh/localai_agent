import os
from langchain_community.llms import CTransformers
from config import (
    MODEL_PATH, MODEL_TYPE, CONTEXT_LENGTH,
    CPU_CONFIG, HYBRID_CONFIG, GPU_CONFIG
)

def load_local_llm(mode: str = "cpu"):
    """
    Loads a local LLM using CTransformers, with a specified context length.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"LLM model not found at {MODEL_PATH}. "
            "Please download a GGUF model and place it in the 'models' directory."
        )

    print(f"Loading LLM in '{mode.upper()}' mode with context length {CONTEXT_LENGTH}...")
    
    config_map = {
        "cpu": CPU_CONFIG,
        "hybrid": HYBRID_CONFIG,
        "gpu": GPU_CONFIG,
    }
    
    config = config_map.get(mode.lower())
    if not config:
        raise ValueError("Invalid mode selected. Choose from 'cpu', 'hybrid', 'gpu'.")

    llm = CTransformers(
        model=MODEL_PATH,
        model_type=MODEL_TYPE,
        # --- CHANGE APPLIED HERE ---
        # We explicitly set the context_length and a default max_new_tokens.
        config={
            **config,
            'context_length': CONTEXT_LENGTH,
            'max_new_tokens': 2048 # A generous default, can be overridden
        }
    )
    
    print("LLM loaded successfully.")
    return llm