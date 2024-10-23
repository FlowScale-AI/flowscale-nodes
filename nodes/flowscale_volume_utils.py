import json
import os
import httpx

VOLUME_ID = os.environ.get("FLOWSCALE_VOLUME_ID")
CONTAINER_ID = os.environ.get("CONTAINER_ID")
ACCESS_TOKEN = os.environ.get("FLOWSCALE_ACCESS_TOKEN")
TEAM_ID = os.environ.get("FLOWSCALE_TEAM_ID")
API_URL = os.environ.get("FLOWSCALE_API_URL")

class SaveModelToFlowscaleVolume:
  """ 
  Save a model to a Flowscale volume.
  """
  
  @classmethod
  def INPUT_TYPES(cls):
    return {
      "required": {
          "model_type": (["lora", "controlnet", "vae", "unet", "other"],),
          "path_in_volume": ("STRING", {"multiline": False, "placeholder": "path/to/model, e.g. loras/my_model"})
      },
      "optional": {
          "huggingface_url": ("STRING", {"multiline": False, "forceInput": True}),
          "s3_url": ("STRING", {"multiline": False, "forceInput": True}),
          "civitai_url": ("STRING", {"multiline": False, "forceInput": True})
      }
    }
    
  RETURN_TYPES = ("STRING",)
  RETURN_NAMES = ("download_url",)
  FUNCTION = "upload_model_to_flowscale_volume"
  CATEGORY = "Utilities"
  OUTPUT_NODE = True
  
  def upload_model_to_flowscale_volume(self, model_type, path_in_volume, huggingface_url=None, s3_url=None, civitai_url=None):
    if not all([VOLUME_ID, CONTAINER_ID, API_URL]):
      raise Exception("Flowscale credentials not set")
    
    if not any([huggingface_url, s3_url, civitai_url]):
      raise Exception("No model URL provided")
    
    if huggingface_url:
      download_url = huggingface_url
    elif s3_url:
      download_url = s3_url
    elif civitai_url:
      download_url = civitai_url
    
    url = f"{API_URL}/api/v1/volume/{VOLUME_ID}/upload?access_token={ACCESS_TOKEN}"
    headers = {
      "X-Team": TEAM_ID,
    }
    body = {
      "path": path_in_volume,
      "download_url": download_url,
      "upload_type": "lora",
    }
        
    response = httpx.post(url, headers=headers, json=body)
    if response.status_code != 200:
      raise Exception(f"Failed to upload model to Flowscale volume: {response.text}")
    
    return {"ui": {"text": download_url}, "result": (download_url,)}
    
    
    