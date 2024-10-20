import os
import torch
from torchvision.utils import save_image

class SaveBatchImagesNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "folder_path": ("STRING", {"default": "./output_images"}),
                "prefix": ("STRING", {"default": "image"}),
                "format": ("STRING", {"default": "png"}),
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    CATEGORY = "Custom Nodes"

    def save_images(self, images, folder_path, prefix, format):
        # Ensure the output folder exists
        os.makedirs(folder_path, exist_ok=True)

        # Extract the image tensor from the input dictionary
        img_samples = images["samples"]  # Tensor of shape [batch_size, C, H, W]

        for i, img_tensor in enumerate(img_samples):
            # Construct the filename
            filename = f"{prefix}_{i}.{format}"
            file_path = os.path.join(folder_path, filename)
            # Save the image directly using torchvision's save_image
            save_image(img_tensor, file_path)
        return ()
