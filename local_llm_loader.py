# local_llm_loader.py

import os
from langchain_community.llms import LlamaCpp
from config import MODEL_PATH, MODEL_NAME, MAX_NEW_TOKENS, CPU_CONFIG, HYBRID_CONFIG, GPU_CONFIG

def load_local_llm(mode: str = "cpu"):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"LLM model not found at {MODEL_PATH}.")

    print(f"Loading LLM '{MODEL_NAME}' with llama-cpp-python in '{mode.upper()}' mode...")
    
    config_map = {
        "cpu": CPU_CONFIG,
        "hybrid": HYBRID_CONFIG,
        "gpu": GPU_CONFIG,
    }
    
    config = config_map.get(mode.lower())
    if not config: raise ValueError("Invalid mode selected.")

    # We use the LlamaCpp wrapper from LangChain to make it compatible
    # with the rest of our code (e.g., the .invoke method).
    llm = LlamaCpp(
        model_path=MODEL_PATH,
        max_tokens=MAX_NEW_TOKENS,
        n_batch=512,
        n_ctx=4096, # It's good practice to set a context size
        verbose=True,
        **config # This unpacks n_gpu_layers
    )
    
    print("LLM loaded successfully via llama-cpp-python.")
    return llm