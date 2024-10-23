import json
import os
import httpx

VOLUME_ID = os.environ.get("FLOWSCALE_VOLUME_ID")
CONTAINER_ID = os.environ.get("CONTAINER_ID")
ACCESS_TOKEN = os.environ.get("FLOWSCALE_ACCESS_TOKEN")
TEAM_ID = os.environ.get("FLOWSCALE_TEAM_ID")
API_URL = os.environ.get("FLOWSCALE_API_URL")

class UploadModelToFlowscaleVolume:
  """ 
  Uploads a model to a Flowscale volume.
  """
  
  @classmethod
  def INPUT_TYPES(cls):
    return {
      "required": {
          "path_in_volume": ("STRING", {"multiline": False, "placeholder": "path/to/model, e.g. loras/my_model"})
      },
      "optional": {
          "huggingface_url": ("STRING", {"multiline": False, "forceInput": True}),
          "s3_url": ("STRING", {"multiline": False, "forceInput": True}),
          "civilai_url": ("STRING", {"multiline": False, "forceInput": True})
      }
    }
    
  RETURN_TYPES = ("STRING",)
  RETURN_NAMES = ("status",)
  FUNCTION = "upload_model_to_flowscale_volume"
  CATEGORY = "Utilities"
  
  def upload_model_to_flowscale_volume(self, s3_url, path_in_volume):
    if not all([VOLUME_ID, CONTAINER_ID, API_URL]):
      raise Exception("Flowscale credentials not set")
    
    url = f"{API_URL}/api/v1/volume/{VOLUME_ID}/upload?access_token={ACCESS_TOKEN}"
    headers = {
      "X-Team": TEAM_ID,
    }
    body = {
      "name": os.path.basename(s3_url),
      "path": path_in_volume,
      "download_url": s3_url,
      "upload_type": "lora",
    }
    
    curl_command = f"curl -X POST {url} -H 'X-Team: {TEAM_ID}' -H 'Content-Type: application/json' -d '{json.dumps(body)}'"
    print(curl_command)
    
    response = httpx.post(url, headers=headers, json=body)
    if response.status_code != 200:
      raise Exception(f"Failed to upload model to Flowscale volume: {response.text}")
    
    return {"ui": {"text": "Model Upload Initialized"}, "result": ("Model Upload Initialized",)}  
    
    
    
    
    
    