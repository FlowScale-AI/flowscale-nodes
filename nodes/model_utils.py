import os

CIVITAI_API_KEY = os.environ.get("CIVITAI_API_KEY")

class LoadModelFromCivitAI:
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
      env = os.environ.copy()
      print(env)
    
      if not CIVITAI_API_KEY:
          raise Exception("CivitAI API key not set")
        
      if os.path.isdir(path):
        filename = os.path.basename(model_url)
        full_path = os.path.join(path, filename)
      else:
        full_path = path
      
      modified_download_url = model_url + ("&" if "?" in model_url else "?") + "token=" + CIVITAI_API_KEY
      print(f"Downloading model from CivitAI: {model_url} into {full_path}")
      command = f"wget -O {full_path} {modified_download_url}"
      result = os.system(command)
      
      if result != 0:
          raise Exception(f"Failed to download model from CivitAI: {model_url}")
      
      return (full_path,)