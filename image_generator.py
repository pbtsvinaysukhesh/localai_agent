import os
import random
from PIL import Image
from llama_cpp import Llama
from config import IMAGE_MODEL_PATH, LLAMA_COMMON_CONFIG, IMAGE_GEN_GPU_OFFLOAD, SD_GEN_CONFIG

class LocalImageGenerator:
    def __init__(self, output_dir="output/images"):
        """
        Initializes the image generator using llama-cpp-python to load a GGUF SD model.
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir): os.makedirs(self.output_dir)

        if not os.path.exists(IMAGE_MODEL_PATH):
            raise FileNotFoundError(f"GGUF image model not found at {IMAGE_MODEL_PATH}.")
        
        self.pipeline = None
        print("Initializing On-Device Image Generator with Llama.cpp...")
        try:
            # Load the GGUF Stable Diffusion model using Llama
            self.pipeline = Llama(
                model_path=IMAGE_MODEL_PATH,
                n_gpu_layers=IMAGE_GEN_GPU_OFFLOAD,
                **LLAMA_COMMON_CONFIG
            )
            print("GGUF Image Model loaded successfully.")
        except Exception as e:
            print(f"Failed to load the GGUF image model: {e}")
            self.pipeline = None
            raise e

    def generate(self, prompt: str, filename: str, width: int = None, height: int = None) -> str | None:
        """
        Generates an image using the loaded GGUF model via llama-cpp-python.
        """
        if self.pipeline is None: return None
            
        print(f"Generating image ({width}x{height}) with GGUF model: '{prompt}'")
        try:
            # Use provided dimensions or fall back to defaults
            img_width = width if width else SD_GEN_CONFIG["width"]
            img_height = height if height else SD_GEN_CONFIG["height"]

            # llama-cpp-python's image generation is handled via the __call__ method
            # with specific parameters. The output is a dictionary.
            output = self.pipeline(
                prompt,
                width=img_width,
                height=img_height,
                cfg_scale=SD_GEN_CONFIG["cfg_scale"],
                steps=SD_GEN_CONFIG["n_steps"],
                seed=random.randint(0, 2**32 - 1),
            )
            
            # The image data is in a specific key, often 'image_data' or similar,
            # and needs to be converted to a Pillow Image object.
            # This part is based on typical llama-cpp-python multimodal output.
            # We assume the output contains raw image data that can be loaded.
            # Note: This part is experimental and depends on the exact model's output format.
            # Let's assume the output is the image itself. If it's a dict, we'd access a key.
            # A common pattern is that the raw image bytes are returned.
            # Let's assume `output` is the image object for now.
            # A more robust check might be needed.
            
            # The output of an image model call is often directly the image data
            # which needs to be opened with Pillow. We'll need to know the format.
            # For now, let's assume it returns a Pillow Image object directly if it can.
            # A common output is a dictionary with the image data. Let's assume a key 'image'.
            # If the output itself is an image object
            if isinstance(output, Image.Image):
                 image = output
            else:
                 # Fallback: assume it's raw bytes, needs more info on format
                 raise ValueError("Unexpected output format from GGUF image model.")

            filepath = os.path.join(self.output_dir, f"{filename}.png")
            image.save(filepath)
            print(f"Image saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"An error occurred during GGUF image generation: {e}")
            return None