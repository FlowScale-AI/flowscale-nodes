import logging
import os
import random
import shutil
import string

import folder_paths  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of supported 3D file extensions
THREED_EXTENSIONS = ["glb", "gltf", "obj", "stl", "fbx", "ply", "usdz"]


class FSLoad3D:
    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [
            f
            for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
            and f.rsplit(".", 1)[-1].lower() in THREED_EXTENSIONS
        ]
        return {
            "required": {
                "model_file": (sorted(files),),
            },
            "optional": {
                "label": ("STRING", {"default": "Input 3D Model"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_path",)
    FUNCTION = "load_3d"
    CATEGORY = "FlowScale/Media/3D"

    def load_3d(self, model_file, label="Input 3D Model"):
        try:
            if os.path.isabs(model_file):
                path = model_file
            else:
                input_dir = folder_paths.get_input_directory()
                path = os.path.join(input_dir, model_file)

                if not os.path.exists(path):
                    path = os.path.join(os.getcwd(), model_file)

            if not os.path.exists(path):
                raise FileNotFoundError(f"3D model not found at path: {path}")

            logger.info(f"I/O Label: {label}")
            logger.info(f"Loaded 3D model: {path}")
            return (path,)
        except Exception as e:
            raise ValueError(f"Error loading 3D model: {e}") from e

    @classmethod
    def IS_CHANGED(cls, model_file, **kwargs):
        if os.path.isabs(model_file):
            path = model_file
        else:
            input_dir = folder_paths.get_input_directory()
            path = os.path.join(input_dir, model_file)
        if os.path.exists(path):
            return os.path.getmtime(path)
        return float("nan")

    @classmethod
    def VALIDATE_INPUTS(cls, model_file, **kwargs):
        if not model_file:
            return "No 3D model file specified"
        return True


class FSSave3D:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"forceInput": True}),
                "filename_prefix": ("STRING", {"default": "FlowScale_3D"}),
            },
            "optional": {
                "label": ("STRING", {"default": "Output 3D Model"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    FUNCTION = "save_3d"
    CATEGORY = "FlowScale/Media/3D"
    OUTPUT_NODE = True

    def save_3d(self, file_path, filename_prefix="FlowScale_3D", label="Output 3D Model"):
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"3D model file not found: {file_path}")

            output_dir = folder_paths.get_output_directory()
            os.makedirs(output_dir, exist_ok=True)

            # Get the file extension from the source
            _, ext = os.path.splitext(file_path)
            if not ext:
                ext = ".glb"

            random_segment = "".join(random.choices(string.digits, k=6))
            save_filename = f"{filename_prefix}_{random_segment}{ext}"
            save_path = os.path.join(output_dir, save_filename)

            # Copy the file to the output directory
            shutil.copy2(file_path, save_path)

            logger.info(f"I/O Label: {label}")
            logger.info(f"3D model saved to: {save_path}")

            return {"ui": {"text": [save_filename]}, "result": (save_path,)}
        except Exception as e:
            logger.error(f"Error saving 3D model: {e}")
            raise ValueError(f"Error saving 3D model: {e}") from e
