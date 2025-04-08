import json
import logging
import os
import httpx

VOLUME_ID = os.environ.get("FLOWSCALE_VOLUME_ID")
CONTAINER_ID = os.environ.get("CONTAINER_ID")
ACCESS_TOKEN = os.environ.get("FLOWSCALE_ACCESS_TOKEN")
TEAM_ID = os.environ.get("FLOWSCALE_TEAM_ID")
API_URL = os.environ.get("FLOWSCALE_API_URL")

HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")
CIVITAI_API_KEY = os.environ.get("CIVITAI_API_KEY")

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
          "path_in_volume": ("STRING", {"multiline": False, "placeholder": "/path/to/model, e.g. /loras"}),
          "download_url": ("STRING", {"multiline": False, "forceInput": True}),
      },
      "optional": {
          "api_key": ("STRING", {"multiline": False}),
          "model_name": ("STRING", {"multiline": False}),
          "webhook_url": ("STRING", {"multiline": False, "forceInput": True}),
      }
    }
    
  RETURN_TYPES = ("STRING", "STRING",)
  RETURN_NAMES = ("download_url", "file_id",)
  FUNCTION = "upload_model_to_flowscale_volume"
  CATEGORY = "FlowScale/Models/Storage"
  OUTPUT_NODE = True
  
  def _create_root_folder(self, model_type, webhook_url=""):
    """Create a root folder in the Flowscale volume"""
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
      if len(webhook_url.strip()) > 0:
        httpx.post(webhook_url, json={"error": str(e)})
      raise Exception(f"Failed to create folder in Flowscale volume: {e}")
    if response.status_code == 400:
      # Folder already exists
      logger.info("Folder already exists in Flowscale volume.")
      return
    elif response.status_code != 200:
      raise Exception(f"Failed to create folder in Flowscale volume: {response.text}")
      
  def _upload_single_model(self, model_type, path_in_volume, download_url, model_name, civitai_api_key="", hf_api_key="", webhook_url=""):
    """Upload a single model to the Flowscale volume"""
    logger.info(f"Uploading model to Flowscale volume {VOLUME_ID}...")
    url = f"{API_URL}/api/v1/volume/{VOLUME_ID}/upload?access_token={ACCESS_TOKEN}"
    headers = {
      "X-Team": TEAM_ID,
    }

    if len(civitai_api_key.strip()) == 0 and CIVITAI_API_KEY:
      civitai_api_key = CIVITAI_API_KEY.strip().rstrip("\n")

    if len(hf_api_key.strip()) == 0 and HUGGINGFACE_API_KEY:
      hf_api_key = HUGGINGFACE_API_KEY.strip().rstrip("\n")

    body = {
      "name": model_name,
      "civitai_api_key": civitai_api_key,
      "hf_api_key": hf_api_key,
      "path": path_in_volume,
      "download_url": download_url,
      "upload_type": model_type,
      "external_webhook_url": webhook_url,
    }
        
    timeout = httpx.Timeout(30.0, connect=30.0)
    file_id = None
    try:
      response = httpx.post(url, headers=headers, json=body, timeout=timeout)
      try:
          response_json = response.json()
      except json.JSONDecodeError as e:
          if len(webhook_url.strip()) > 0:
              httpx.post(webhook_url, json={"error": "Something went wrong while uploading the model to Flowscale volume"})
          raise Exception(f"Invalid JSON response: {e}")

      file_id = response_json.get("data").get("file_id")
      if not file_id:
        if len(webhook_url.strip()) > 0:
          httpx.post(webhook_url, json={"error": "Something went wrong while uploading the model to Flowscale volume"})
        raise Exception("Something went wrong while uploading the model to Flowscale volume")
    except httpx.RequestError as e:
      if len(webhook_url.strip()) > 0:
        httpx.post(webhook_url, json={"error": str(e)})
      raise Exception(f"Failed to upload model to Flowscale volume: {e}")
    
    if response.status_code != 200:
      response_json = response.json()
      if len(webhook_url.strip()) > 0:
        httpx.post(webhook_url, json={"error": json.dumps(response_json
        ).get("data")})
      raise Exception(f"Failed to upload model to Flowscale volume: {response_json.get('data')}")
    
    # Save model info to a file
    with open(f'output/{model_name}.txt', 'w') as f:
      if "." not in model_name:
        model_name += ".safetensors"
      data = {
        "lora_name": model_name,
        "download_url": download_url,
      }
      f.write(json.dumps(data))
    
    return download_url, file_id
 
  def upload_model_to_flowscale_volume(self, model_type, path_in_volume, 
                                       download_url, api_key="", model_name="", webhook_url=""):
    if not all([VOLUME_ID, CONTAINER_ID, API_URL]):
      raise Exception("Flowscale credentials are missing")
    
    try:
      civitai_api_key = ""
      hf_api_key = ""
      if "huggingface.co" in download_url:
        hf_api_key = api_key.strip().rstrip("\n")
      elif "civitai.com" in download_url:
        civitai_api_key = api_key.strip().rstrip("\n")

      # Create root folder
      self._create_root_folder(model_type, webhook_url)
        
      url, file_id = self._upload_single_model(
        model_type, 
        path_in_volume, 
        download_url, 
        model_name, 
        civitai_api_key=civitai_api_key, 
        hf_api_key=hf_api_key,
        webhook_url=webhook_url
      )
      return {"ui": {"text": url}, "result": (url, file_id)}
    except Exception as e:
      logger.exception(f"Error uploading model to Flowscale volume: {e}")
      if len(webhook_url.strip()) > 0:
        httpx.post(webhook_url, json={"error": str(e)})
      return {"ui": {"text": str(e)}, "result": (None, None)}