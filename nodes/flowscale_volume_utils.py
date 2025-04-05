import json
import logging
import os
import httpx

VOLUME_ID = os.environ.get("FLOWSCALE_VOLUME_ID")
CONTAINER_ID = os.environ.get("CONTAINER_ID")
ACCESS_TOKEN = os.environ.get("FLOWSCALE_ACCESS_TOKEN")
TEAM_ID = os.environ.get("FLOWSCALE_TEAM_ID")
API_URL = os.environ.get("FLOWSCALE_API_URL")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SaveModelToFlowscaleVolume:
  """ 
  Save a model to a Flowscale volume.
  """
  
  @classmethod
  def INPUT_TYPES(cls):
    return {
      "required": {
          "model_type": (["lora", "controlnet", "vae", "unet", "other"],),
          "path_in_volume": ("STRING", {"multiline": False, "placeholder": "path/to/model, e.g. loras/my_model"}),
          "download_url": ("STRING", {"multiline": False, "forceInput": True}),
      },
      "optional": {
          "model_name": ("STRING", {"multiline": False, "forceInput": True}),
          "api_key": ("STRING", {"multiline": False, "forceInput": True}),
      }
    }
    
  RETURN_TYPES = ("STRING",)
  RETURN_NAMES = ("download_url",)
  FUNCTION = "upload_model_to_flowscale_volume"
  CATEGORY = "FlowScale/Models/Storage"
  OUTPUT_NODE = True
  
  def upload_model_to_flowscale_volume(self, model_type, path_in_volume, 
                                       download_url, model_name="", api_key=""):
    if not all([VOLUME_ID, CONTAINER_ID, API_URL]):
      raise Exception("Flowscale credentials not set")
    
    source = "generic"
    civitai_api_key = ""
    hf_api_key = ""
    if "huggingface.co" in download_url:
      hf_api_key = api_key.strip().rstrip("\n")
    elif "civitai.com" in download_url:
      civitai_api_key = api_key.strip().rstrip("\n")

    # Create root folder
    logger.info(f"Creating root folder in Flowscale volume {VOLUME_ID}...")
    url = f"{API_URL}/api/v1/volume/{VOLUME_ID}/folder?access_token={ACCESS_TOKEN}"
    headers = {
      "X-Team": TEAM_ID,
    }
    body = {
      "folder_name": "loras" if model_type == "lora" else model_type,
      "path": "/",
    }
    timeout = httpx.Timeout(30.0, connect=30.0)
    try:
      response = httpx.post(url, headers=headers, json=body, timeout=timeout)
    except httpx.RequestError as e:
      raise Exception(f"Failed to create folder in Flowscale volume: {e}")
    if response.status_code == 400:
      # Folder already exists
      pass
    elif response.status_code != 200:
      raise Exception(f"Failed to create folder in Flowscale volume: {response.text}")
    
    # Add model to volume and fs
    logger.info(f"Uploading model to Flowscale volume {VOLUME_ID}...")
    url = f"{API_URL}/api/v1/volume/{VOLUME_ID}/upload?access_token={ACCESS_TOKEN}"
    headers = {
      "X-Team": TEAM_ID,
    }
    body = {
      "name": model_name,
      "civitai_api_key": civitai_api_key,
      "hf_api_key": hf_api_key,
      "path": path_in_volume,
      "download_url": download_url,
      "upload_type": model_type,
    }
        
    try:
      logger.info(f"URL: {url}")
      logger.info(f"Headers: {headers}")
      logger.info(f"Body: {body}")
      response = httpx.post(url, headers=headers, json=body, timeout=timeout)
    except httpx.RequestError as e:
      raise Exception(f"Failed to upload model to Flowscale volume: {e}")
    
    
    if response.status_code != 200:
      raise Exception(f"Failed to upload model to Flowscale volume: {response.text}")
    
    with open(f'output/{model_name}.txt', 'w') as f:
      if "." not in model_name:
        model_name += ".safetensors"
      data = {
        "lora_name": model_name,
        "download_url": download_url,
      }
      f.write(json.dumps(data))
    
    return {"ui": {"text": download_url}, "result": (download_url,)}


