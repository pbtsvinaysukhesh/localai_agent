# local_llm_loader.py

import os
from langchain_community.llms import CTransformers
from config import (
    MODEL_PATH, 
    MODEL_NAME, # We now import MODEL_NAME to determine the type automatically
    CPU_CONFIG, 
    HYBRID_CONFIG, 
    GPU_CONFIG
)

def get_model_type_from_name(model_name: str) -> str:
    """
    Determines the model type from the filename.
    """
    name = model_name.lower()
    if "mistral" in name or "mixtral" in name:
        return "mistral"
    elif "llama" in name:
        return "llama2"
    elif "zephyr" in name:
        return "zephyr"
    else:
        print(f"Warning: Could not determine model type from name '{model_name}'. Falling back to 'mistral'.")
        return "mistral"

def load_local_llm(mode: str = "cpu"):
    """
    Loads a local LLM, automatically detects its model type from the filename,
    and automatically detects its maximum context length.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"LLM model not found at {MODEL_PATH}. "
            "Please download a GGUF model and place it in the 'models' directory."
        )

    model_type = get_model_type_from_name(MODEL_NAME)
    print(f"✅ Model name '{MODEL_NAME}' detected as type: '{model_type}'")

    print(f"Loading LLM in '{mode.upper()}' mode...")
    
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
        model_type=model_type,
        config={
            **config,
            'max_new_tokens': -1 
        }
    )
    
    print("LLM loaded successfully.")

    try:
        detected_context_length = llm.client.context_length
        print(f"✅ Model's maximum context length automatically detected: {detected_context_length} tokens.")
    except Exception as e:
        print(f"Warning: Could not automatically detect context length. Using a default. Error: {e}")
    
    return llm