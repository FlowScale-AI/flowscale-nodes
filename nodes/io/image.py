import os
import random
import string
import numpy as np
import torch
from PIL import Image
import folder_paths
import requests
from io import BytesIO

class FSLoadImage:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {
            "required": {
                "image": (sorted(files), {"image_upload": True}),
            },
            "optional": {
                "label": ("STRING", {"default": "Input Image"}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    FUNCTION = "load_image"

    CATEGORY = "FlowScale/IO"

    def load_image(self, image, label="Input Image"):
        try:
            if os.path.isabs(image):
                path = image
            else:
                # Otherwise, check in the input directory
                input_dir = folder_paths.get_input_directory()
                path = os.path.join(input_dir, image)
                
                # If not found in input directory, try absolute from cwd
                if not os.path.exists(path):
                    path = os.path.join(os.getcwd(), image)
            
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image not found at path: {path}")
                
            # Load the image with PIL
            img = Image.open(path)
            
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")
                
            # Convert to numpy array and normalize
            img_np = np.array(img).astype(np.float32) / 255.0
            
            # Add batch dimension expected by ComfyUI
            img_tensor = img_np[np.newaxis, ...]
            
            print(f"I/O Label: {label}")
            return (img_tensor,)
        except Exception as e:
            raise ValueError(f"Error loading image: {e}")

class FSLoadImageFromURL:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_url": ("STRING", {"default": ""}),
            },
            "optional": {
                "label": ("STRING", {"default": "Input Image"}),
            }
        }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "load_image_from_url"
    CATEGORY = "FlowScale/IO"
    def load_image_from_url(self, image_url, label="Input Image"):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            img = img.convert("RGB")
            img_np = np.array(img).astype(np.float32) / 255.0
            img_tensor = img_np[np.newaxis, ...]
            print(f"I/O Label: {label}")
            return (img_tensor,)
        except Exception as e:
            raise ValueError(f"Error loading image from URL: {e}")

class FSSaveImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "FlowScale"}),
                "format": (["png", "jpg", "jpeg", "webp"], {"default": "png"})
            },
            "optional": {
                "label": ("STRING", {"default": "Output Image"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "lossless": ("BOOLEAN", {"default": False, "tooltip": "Use lossless compression for webp"})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    
    FUNCTION = "save_image"
    
    CATEGORY = "FlowScale/IO"
    OUTPUT_NODE = True
    
    def save_image(self, images, filename_prefix="FlowScale", format="png", quality=100, lossless=False, label="Output Image"):
        output_dir = folder_paths.get_output_directory()
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        for i, image in enumerate(images):
            # Convert from tensor to numpy if needed
            if isinstance(image, torch.Tensor):
                image = image.cpu().numpy()
            
            # Convert from [0,1] to [0,255]
            img = (image * 255).astype(np.uint8)
            # Convert to PIL Image
            pil_image = Image.fromarray(img)
            
            # Set up the filename
            file_extension = format.lower()
            if format == "jpg":
                file_extension = "jpeg"
                
            random_segment = ''.join(random.choices(string.digits, k=6))
            save_filename = f"{filename_prefix}_{random_segment}.{file_extension}"
            
            # Full save path
            save_path = os.path.join(output_dir, save_filename)
            
            # Save based on format with appropriate options
            if format in ["webp"]:
                pil_image.save(save_path, format=format.upper(), quality=quality, lossless=lossless)
            elif format in ["jpg", "jpeg"]:
                pil_image.save(save_path, format="JPEG", quality=quality)
            else:
                # PNG and others
                pil_image.save(save_path)
                
            results.append(save_path)
        print(f"I/O Label: {label}")
        
        return (results[0] if results else "",)