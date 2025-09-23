
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# --- LOCAL LLM MODEL (for Text Generation) ---
MODEL_NAME = "capybarahermes-2.5-mistral-7b.Q4_K_M.gguf"
MODEL_TYPE = "mistral" # ctransformers needs this
MODEL_PATH = os.path.join(MODELS_DIR, MODEL_NAME)

# --- ON-DEVICE IMAGE MODEL (GGUF Format) ---
# This now points to your desired GGUF image model
IMAGE_MODEL_NAME = "sd3.5_large-Q4_0.gguf" # <-- YOUR CHOSEN MODEL
IMAGE_MODEL_PATH = os.path.join(MODELS_DIR, IMAGE_MODEL_NAME)
MAX_NEW_TOKENS_PER_SECTION = 8192



CONTEXT_LENGTH = 1024

SD_CONFIG = {
    "n_threads": -1,
    "wtype": "f16",
    "n_steps": 20,
    "cfg_scale": 7.0,
    "width": 512,
    "height": 512,
}

# --- HARDWARE ACCELERATION CONFIGURATIONS (for LLM) ---
CPU_CONFIG = {"gpu_layers": 0, "threads": -1}
HYBRID_CONFIG = {"gpu_layers": 25, "threads": 8}
GPU_CONFIG = {"gpu_layers": -1, "threads": 4}