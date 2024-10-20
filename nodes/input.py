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

class LoadImagesFromDirectoryNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "./input_images"}),
                "file_extension": ("STRING", {"default": "png"}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "load_images"
    CATEGORY = "Custom Nodes"

    def load_images(self, folder_path, file_extension):
        # List all files with the given extension in the directory
        file_list = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(f".{file_extension.lower()}")
        ]

        if not file_list:
            raise FileNotFoundError(f"No files with extension .{file_extension} found in {folder_path}")

        # Load images and convert to tensors
        image_tensors = []
        for file_path in file_list:
            img = Image.open(file_path).convert("RGB")
            img_tensor = torch.from_numpy(np.array(img)).permute(2, 0, 1).float() / 255.0
            image_tensors.append(img_tensor)

        # Stack tensors into a batch
        batch_tensor = torch.stack(image_tensors)

        # Prepare the output in the format expected by ComfyUI
        images = {"samples": batch_tensor}

        return (images,)