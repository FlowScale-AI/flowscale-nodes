import os

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
  FUNCTION = "load_model_from_civitai"
  CATEGORY = "Utilities"

  def load_model_from_civitai(self, model_url, path):
      if os.path.isdir(path):
        filename = os.path.basename(model_url)
        full_path = os.path.join(path, filename)
      else:
        full_path = path
      
      print(f"Downloading model from CivitAI: {model_url} into {full_path}")
      command = f"wget -O {full_path} {model_url}"
      result = os.system(command)
      
      if result != 0:
          raise Exception(f"Failed to download model from CivitAI: {model_url}")
      
      return full_path