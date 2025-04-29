import logging
import os

HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
CIVITAI_API_KEY = os.environ.get("CIVITAI_API_KEY")
COMFYUI_MODELS_DIR = "/comfyui/models"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadModelFromURL:
  """
  Load a model from URL
  """
  
  @classmethod
  def INPUT_TYPES(cls):
    return {
      "required": {
          "model_url": ("STRING", {"multiline": False}),
          "path": ("STRING", {"multiline": False})
      }
    }
    
  RETURN_TYPES = ("STRING",)
  RETURN_NAMES = ("filepath",)
  FUNCTION = "load_model_from_url"
  CATEGORY = "FlowScale/Models/Download"

  def load_model_from_url(self, model_url, path):   
      # Create the target directory if it doesn't exist
      if os.path.isdir(COMFYUI_MODELS_DIR):
          target_dir = os.path.join(COMFYUI_MODELS_DIR, path)
          os.makedirs(target_dir, exist_ok=True)
          
          # Extract filename from URL
          filename = os.path.basename(model_url)
          # If URL ends with query parameters, extract just the filename part
          if '?' in filename:
              filename = filename.split('?')[0]
          
          full_path = os.path.join(target_dir, filename)
      else:
          logger.warning(f"COMFYUI_MODELS_DIR '{COMFYUI_MODELS_DIR}' is not a directory, using provided path as is")
          full_path = path

      logger.info(f"Will save downloaded model to: {full_path}")

      if "huggingface.co" in model_url:
        if not HUGGINGFACE_API_KEY:
            raise Exception("HUGGINGFACE_API_KEY is not set. Please set it in the environment variables.")
        cmd = [
            "wget",
            "--header", f"Authorization: Bearer {HUGGINGFACE_API_KEY}",
            "--progress=dot:mega",
            model_url,
            "-O", full_path
        ]
      elif "civitai.com" in model_url:
        if not CIVITAI_API_KEY:
            raise Exception("CIVITAI_API_KEY is not set. Please set it in the environment variables.")
        modified_download_url = model_url + ("&" if "?" in model_url else "?") + "token=" + CIVITAI_API_KEY
        cmd = [
            "wget",
            "--progress=dot:mega",
            modified_download_url,
            "-O", full_path
        ]
      else:
        cmd = [
            "wget",
            "--progress=dot:mega",
            model_url,
            "--content-disposition",
            "-O", full_path
        ]
          
      logger.info(f"Downloading model from unknown source: {model_url} into {full_path}")
      
      cmd_str = " ".join(cmd)
      result = os.system(cmd_str)
      
      if result != 0:
          raise Exception(f"Failed to download model: {model_url}")
      
      return (full_path,)
