# image_generator.py

import os
import random
from stable_diffusion_cpp import StableDiffusion
from config import IMAGE_MODEL_PATH, SD_CONFIG

class LocalImageGenerator:
    def __init__(self, output_dir="output/images"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir): os.makedirs(self.output_dir)

        if not os.path.exists(IMAGE_MODEL_PATH):
            raise FileNotFoundError(
                f"On-device image model not found at {IMAGE_MODEL_PATH}. "
                f"Please ensure '{IMAGE_MODEL_NAME}' is in the 'models' directory."
            )
        
        self.pipeline = None
        print("Initializing On-Device Image Generator...")
        try:
            self.pipeline = StableDiffusion(
                model_path=IMAGE_MODEL_PATH,
                wtype=SD_CONFIG["wtype"],
                n_threads=SD_CONFIG["n_threads"],
            )
            print("Image Model loaded successfully via stable-diffusion.cpp.")
        except Exception as e:
            print(f"Failed to load the image generation model: {e}")
            self.pipeline = None
            raise e

    def generate(self, prompt: str, filename: str, width: int = None, height: int = None) -> str | None:
        if self.pipeline is None: return None
        print(f"Generating image ({width}x{height}) for prompt: '{prompt}'")
        try:
            img_width = width if width else SD_CONFIG["width"]
            img_height = height if height else SD_CONFIG["height"]
            images = self.pipeline.predict(
                prompt=prompt,
                seed=random.randint(0, 2**32 - 1),
                n_steps=SD_CONFIG["n_steps"],
                cfg_scale=SD_CONFIG["cfg_scale"],
                width=img_width,
                height=img_height,
            )
            image = images[0]
            filepath = os.path.join(self.output_dir, f"{filename}.png")
            image.save(filepath)
            print(f"Image saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"An error occurred during image generation: {e}")
            return None