# config.py

import os

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONTEXT_LENGTH = 1024
# --- LOCAL LLM MODEL (YOUR GEMMA MODEL) ---
MODEL_NAME = "phi-4-Q4_0.gguf"
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_NAME)
#MODEL_TYPE = "phi" # This is critical for the ctransformers library

# --- ON-DEVICE IMAGE MODEL (SD3 - LOCAL PATH) ---
# This points to the local folder you downloaded with 'git clone'.
# This is NOT a single file, but the name of the directory.
IMAGE_MODEL_ID = os.path.join(BASE_DIR, "stable-diffusion-3-medium-diffusers")

# --- LLM GENERATION PARAMETERS ---
# -1 allows the agent to write huge amounts of content without being cut off.
MAX_NEW_TOKENS = -1

# --- HARDWARE ACCELERATION CONFIGURATIONS (for LLM) ---
CPU_CONFIG = {"gpu_layers": 0, "threads": -1}
HYBRID_CONFIG = {"gpu_layers": 25, "threads": 8}
GPU_CONFIG = {"gpu_layers": -1, "threads": 4}