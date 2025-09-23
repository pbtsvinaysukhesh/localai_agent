
import os
import torch
from diffusers import StableDiffusion3Pipeline
from config import IMAGE_MODEL_ID

class LocalImageGenerator:
    def __init__(self, output_dir="output/images"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir): os.makedirs(self.output_dir)
        if not os.path.isdir(IMAGE_MODEL_ID):
             raise FileNotFoundError(f"The local SD3 model directory was not found at: {IMAGE_MODEL_ID}.")

        # --- CHANGES FOR CPU ---
        # 1. REMOVE the CUDA check
        # if not torch.cuda.is_available():
        #     raise RuntimeError("Image generation with SD3 requires a CUDA-enabled GPU.")

        self.pipeline = None
        print(f"Initializing Diffusers Image Generator on CPU: {IMAGE_MODEL_ID}")
        
        try:
            self.pipeline = StableDiffusion3Pipeline.from_pretrained(
                IMAGE_MODEL_ID,
                # 2. CHANGE torch_dtype to float32, as float16 is poorly supported on CPU
                torch_dtype=torch.float32 
            )
            # 3. DO NOT move the pipeline to "cuda"
            # self.pipeline.to("cuda") 
            print("Image Generator pipeline loaded to CPU successfully.")
        except Exception as e:
            print(f"Failed to load the diffusers model: {e}"); raise e

    def generate(self, prompt: str, filename: str, width: int = 512, height: int = 512) -> str | None:
        # Reduced default size for CPU       if self.pipeline is None: return None
        print(f"Generating image on GPU for prompt: '{prompt}'")
        try:
            image = self.pipeline(
                prompt, num_inference_steps=28, guidance_scale=7.0,
                width=width, height=height
            ).images[0]
            
            filepath = os.path.join(self.output_dir, f"{filename}.png")
            image.save(filepath)
            print(f"Image saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"An error occurred during image generation: {e}"); return None