import os
import numpy as np
from PIL import Image
import folder_paths

class FSLoadImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image_path": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    FUNCTION = "load_image"

    CATEGORY = "IO"

    def load_image(self, image_path):
        try:
            # If path is absolute, use it directly
            if os.path.isabs(image_path):
                path = image_path
            else:
                # Otherwise, check in the input directory
                input_dir = folder_paths.get_input_directory()
                path = os.path.join(input_dir, image_path)
                
                # If not found in input directory, try absolute from cwd
                if not os.path.exists(path):
                    path = os.path.join(os.getcwd(), image_path)
            
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
            
            return (img_tensor,)
        except Exception as e:
            print(f"Error loading image: {e}")
            # Return a small red placeholder image on error 
            error_img = np.ones((1, 64, 64, 3), dtype=np.float32)
            error_img[..., 1:] = 0  # Set green and blue channels to 0 (making it red)
            return (error_img,)


class FSSaveImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename": ("STRING", {"default": "output"}),
                "format": (["png", "jpg", "jpeg", "webp"], {"default": "png"})
            },
            "optional": {
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "lossless": ("BOOLEAN", {"default": False}),  # For webp format
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    
    FUNCTION = "save_image"
    
    CATEGORY = "IO"
    OUTPUT_NODE = True
    
    def save_image(self, images, filename, format="png", quality=95, lossless=False):
        output_dir = folder_paths.get_output_directory()
        filename_prefix = filename
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        
        for i, image in enumerate(images):
            # Convert from [0,1] to [0,255]
            img = (image * 255).astype(np.uint8)
            # Convert to PIL Image
            pil_image = Image.fromarray(img)
            
            # Set up the filename
            file_extension = format.lower()
            if format == "jpg":
                file_extension = "jpeg"
                
            # Add index to filename if we're saving multiple images
            if images.shape[0] > 1:
                save_filename = f"{filename_prefix}_{i:05d}.{file_extension}"
            else:
                save_filename = f"{filename_prefix}.{file_extension}"
                
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
        
        return (results[0] if results else "",)