
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# --- LOCAL LLM MODEL (for Text Generation) ---
MODEL_NAME = "capybarahermes-2.5-mistral-7b.Q4_K_M.gguf"
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_NAME)

# --- ON-DEVICE IMAGE MODEL (GGUF Format) ---
# This now points to your desired GGUF image model
IMAGE_MODEL_NAME = "sd3.5_large-Q4_0.gguf" # <-- YOUR CHOSEN MODEL
IMAGE_MODEL_PATH = os.path.join(MODELS_DIR, IMAGE_MODEL_NAME)
MAX_NEW_TOKENS_PER_SECTION = -1


# --- COMMON LLAMA.CPP CONFIGURATION ---
LLAMA_COMMON_CONFIG = {
    "n_ctx": 4096,  # Context length
    "n_batch": 512, # Batch size for prompt processing
    "verbose": True # Set to True to see llama.cpp output
}

# --- GPU OFFLOAD CONFIGURATION ---
# Number of layers to offload to the GPU. -1 means all possible layers.
# Adjust this based on your VRAM.
TEXT_GEN_GPU_OFFLOAD = -1  # For LLM
IMAGE_GEN_GPU_OFFLOAD = -1 # For Stable Diffusion model

# --- IMAGE GENERATION PARAMETERS (for llama-cpp-python) ---
SD_GEN_CONFIG = {
    "n_steps": 28,
    "cfg_scale": 7.0,
    "width": 512,
    "height": 512,
}

# --- HARDWARE ACCELERATION CONFIGURATIONS (for LLM) ---
CPU_CONFIG = {"gpu_layers": 0, "threads": -1}
HYBRID_CONFIG = {"gpu_layers": 25, "threads": 8}
GPU_CONFIG = {"gpu_layers": -1, "threads": 4}