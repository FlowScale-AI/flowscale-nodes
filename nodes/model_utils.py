import logging
import os

HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
CIVITAI_API_KEY = os.environ.get("CIVITAI_API_KEY")
COMFYUI_MODELS_DIR = "/comfyui/models"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadModelFromURL:
  """
  Load a model from CivitAI
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
  FUNCTION = "load_model_from_civitai"
  CATEGORY = "FlowScale/Models/Download"

  def load_model_from_civitai(self, model_url, path):   
      if os.path.isdir(path):
        filename = os.path.basename(model_url)
        full_path = os.path.join(COMFYUI_MODELS_DIR, path, filename)
      else:
        full_path = path

      if ".huggingface.co" in model_url:
        if not HUGGINGFACE_API_KEY:
            raise Exception("HUGGINGFACE_API_KEY is not set. Please set it in the environment variables.")
        cmd = [
            "wget",
            "--header", f"Authorization: Bearer {HUGGINGFACE_API_KEY}",
            "--progress=dot:mega",
            model_url,
            "--content-disposition",
            "-O", full_path
        ]
      elif ".civitai.com" in model_url:
        if not CIVITAI_API_KEY:
            raise Exception("CIVITAI_API_KEY is not set. Please set it in the environment variables.")
        modified_download_url = model_url + ("&" if "?" in model_url else "?") + "token=" + CIVITAI_API_KEY
        cmd = [
            "wget",
            "--progress=dot:mega",
            modified_download_url,
            "--content-disposition",
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