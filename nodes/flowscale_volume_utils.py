import json
import logging
import os
import httpx
import tarfile
import tempfile
import shutil
from pathlib import Path

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
  
  def _create_root_folder(self, model_type):
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
      raise Exception(f"Failed to create folder in Flowscale volume: {e}")
    if response.status_code == 400:
      # Folder already exists
      pass
    elif response.status_code != 200:
      raise Exception(f"Failed to create folder in Flowscale volume: {response.text}")
      
  def _upload_single_model(self, model_type, path_in_volume, download_url, model_name, civitai_api_key="", hf_api_key=""):
    """Upload a single model to the Flowscale volume"""
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
        
    timeout = httpx.Timeout(30.0, connect=30.0)
    try:
      logger.info(f"URL: {url}")
      logger.info(f"Headers: {headers}")
      logger.info(f"Body: {body}")
      response = httpx.post(url, headers=headers, json=body, timeout=timeout)
    except httpx.RequestError as e:
      raise Exception(f"Failed to upload model to Flowscale volume: {e}")
    
    if response.status_code != 200:
      raise Exception(f"Failed to upload model to Flowscale volume: {response.text}")
    
    # Save model info to a file
    with open(f'output/{model_name}.txt', 'w') as f:
      if "." not in model_name:
        model_name += ".safetensors"
      data = {
        "lora_name": model_name,
        "download_url": download_url,
      }
      f.write(json.dumps(data))
    
    return download_url
  
  def _download_file(self, url, api_key=""):
    """Download a file from a URL to a temporary location"""
    logger.info(f"Downloading file from {url}...")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.basename(url))
    
    headers = {}
    if "huggingface.co" in url and api_key:
      headers["Authorization"] = f"Bearer {api_key}"
    elif "civitai.com" in url and api_key:
      headers["Authorization"] = f"Bearer {api_key}"
      
    with httpx.stream("GET", url, headers=headers, timeout=None) as response:
      if response.status_code != 200:
        temp_file.close()
        os.unlink(temp_file.name)
        raise Exception(f"Failed to download file: {response.text}")
        
      for chunk in response.iter_bytes():
        temp_file.write(chunk)
          
    temp_file.close()
    return temp_file.name
    
  def _extract_safetensors_from_tar(self, tar_path):
    """Extract all safetensors files from a tar archive"""
    logger.info(f"Extracting safetensors files from {tar_path}...")
    temp_dir = tempfile.mkdtemp()
    
    try:
      with tarfile.open(tar_path) as tar:
        tar.extractall(path=temp_dir)
        
      # Find all safetensors files
      safetensors_files = []
      for root, _, files in os.walk(temp_dir):
        for file in files:
          if file.endswith(".safetensors"):
            full_path = os.path.join(root, file)
            safetensors_files.append((file, full_path))
            
      logger.info(f"Found {len(safetensors_files)} safetensors files")
      return temp_dir, safetensors_files
    except Exception as e:
      shutil.rmtree(temp_dir, ignore_errors=True)
      raise Exception(f"Failed to extract tar file: {e}")
  
  def upload_model_to_flowscale_volume(self, model_type, path_in_volume, 
                                       download_url, model_name="", api_key=""):
    # if not all([VOLUME_ID, CONTAINER_ID, API_URL]):
    #   raise Exception("Flowscale credentials not set")
    
    civitai_api_key = ""
    hf_api_key = ""
    if "huggingface.co" in download_url:
      hf_api_key = api_key.strip().rstrip("\n")
    elif "civitai.com" in download_url:
      civitai_api_key = api_key.strip().rstrip("\n")

    # Create root folder
    # self._create_root_folder(model_type)
    
    # Check if the URL ends with .tar - if so, handle it differently
    if download_url.lower().endswith('.tar'):
      logger.info("Detected .tar file, processing multiple models...")
      
      # Download the tar file
      temp_tar_path = self._download_file(download_url, api_key=api_key)
      
      try:
        # Extract safetensors from the tar
        temp_dir, safetensors_files = self._extract_safetensors_from_tar(temp_tar_path)
        
        if not safetensors_files:
          raise Exception("No safetensors files found in the tar archive")
        
        # Upload each safetensors file
        uploaded_urls = []
        for file_name, file_path in safetensors_files:
          # Create a unique path for each model
          model_path = path_in_volume
          
          # For now, we'll host the file locally and create a temporary URL
          # In a real scenario, you might use a different approach
          file_url = f"file://{file_path}"
          
          # Use the filename as model name if not provided
          current_model_name = model_name if model_name else os.path.splitext(file_name)[0]
          
          # Upload the model
          logger.info(f"Uploading {file_name} to {model_path}...")
          uploaded_url = self._upload_single_model(
            model_type, 
            model_path, 
            file_url, 
            current_model_name, 
            civitai_api_key=civitai_api_key, 
            hf_api_key=hf_api_key
          )
          uploaded_urls.append(uploaded_url)
        
        # Clean up
        os.unlink(temp_tar_path)
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        # Return the original download URL as a reference
        return {"ui": {"text": download_url}, "result": (download_url,)}
        
      except Exception as e:
        # Clean up on error
        if os.path.exists(temp_tar_path):
          os.unlink(temp_tar_path)
        raise e
    else:
      # Process a single model as before
      url = self._upload_single_model(
        model_type, 
        path_in_volume, 
        download_url, 
        model_name, 
        civitai_api_key=civitai_api_key, 
        hf_api_key=hf_api_key
      )
      return {"ui": {"text": url}, "result": (url,)}


