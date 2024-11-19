import os
import boto3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = os.environ.get("AWS_S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_S3_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_S3_REGION", "us-east-1")
S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")

class UploadModelToPublicS3:
  """
  Uploads a model to Public S3 Buckets
  """
  
  @classmethod
  def INPUT_TYPES(cls):
    return {
      "required": {
          "filepath": ("STRING", {"forceInput": False}),
          "model_name": ("STRING", {"forceInput": False})
      },
      "optional": {
          "file": ("*", ),
      }
    }

  @classmethod
  def VALIDATE_INPUTS(s, input_types):
      return True
    
  RETURN_TYPES = ("STRING", "STRING")
  RETURN_NAMES = ("download_url", "model_name")
  FUNCTION = "upload_model_to_s3"
  CATEGORY = "Utilities"
  OUTPUT_NODE = True
  
  def upload_model_to_s3(self, filepath, model_name=None, file=None):
    if filepath.startswith("./") or filepath.startswith("../"):
        filepath = filepath.lstrip("./").lstrip("../")
    if filepath.startswith("/") or filepath.startswith("\\"):
        filepath = filepath.lstrip("/").lstrip("\\")

    base_directory = os.getcwd()
    sanitized_filepath = os.path.normpath(filepath).lstrip(os.sep).rstrip(os.sep)
    absolute_filepath = os.path.abspath(os.path.join(base_directory, sanitized_filepath))
    logger.info(f"Uploading model from {absolute_filepath}")
    
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
      raise Exception("AWS credentials not set")
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    if model_name:
      if not os.path.isfile(absolute_filepath) and os.path.isdir(absolute_filepath):
        absolute_filepath = os.path.join(absolute_filepath, model_name + '.safetensors')
      elif "." not in model_name and "." not in os.path.basename(absolute_filepath):
          absolute_filepath += ".safetensors"
          
      if "." not in model_name:
          modified_model_name = model_name + ".safetensors"
      else:
          modified_model_name = model_name
      s3_key = os.path.join("models", modified_model_name)
    else:
      if "." not in os.path.basename(absolute_filepath):
        absolute_filepath += ".safetensors"
      s3_key = os.path.join("models", os.path.basename(absolute_filepath))
    
    try:
      s3_client.upload_file(absolute_filepath, S3_BUCKET_NAME, s3_key)
      download_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
      return (download_url, model_name,)
    except Exception as e:
      raise Exception(f"Failed to upload model to S3: {str(e)}")


class UploadModelToPrivateS3:
    """
    Uploads a model to a private S3 bucket
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "filepath": ("STRING", {"forceInput": False}),
                "model_name": ("STRING", {"forceInput": False})
            },
            "optional": {
                "file": ("*", ),
            }
        }
    
    @classmethod
    def VALIDATE_INPUTS(s, input_types):
        return True

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("s3_key", )
    FUNCTION = "upload_model_to_s3"
    CATEGORY = "Utilities"
    OUTPUT_NODE = True

    def upload_model_to_s3(self, filepath, model_name=None, file=None):
        if filepath.startswith("./") or filepath.startswith("../"):
            filepath = filepath.lstrip("./").lstrip("../")
        if filepath.startswith("/") or filepath.startswith("\\"):
            filepath = filepath.lstrip("/").lstrip("\\")
        base_directory = os.getcwd()
        sanitized_filepath = os.path.normpath(filepath).lstrip(os.sep).rstrip(os.sep)
        absolute_filepath = os.path.abspath(os.path.join(base_directory, sanitized_filepath))
        logger.info(f"Uploading model from {absolute_filepath}")

        if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
            raise Exception("AWS credentials not set")

        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

        if model_name:
            if not os.path.isfile(absolute_filepath) and os.path.isdir(absolute_filepath):
              absolute_filepath = os.path.join(absolute_filepath, model_name + '.safetensors')
            elif "." not in model_name and "." not in os.path.basename(absolute_filepath):
                absolute_filepath += ".safetensors"
                
            if "." not in model_name:
                modified_model_name = model_name + ".safetensors"
            else:
                modified_model_name = model_name
            s3_key = os.path.join("models", modified_model_name)
        else:
            if "." not in os.path.basename(absolute_filepath):
                absolute_filepath += ".safetensors"
            s3_key = os.path.join("models", os.path.basename(absolute_filepath))

        try:
            s3_client.upload_file(absolute_filepath, S3_BUCKET_NAME, s3_key)
            return (s3_key, )
        except Exception as e:
            raise Exception(f"Failed to upload model to S3: {str(e)}")


class LoadModelFromPublicS3:
    """
    Loads a model from a public S3 bucket and saves it to a filepath
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "download_url": ("STRING", {"forceInput": False}),
                "save_path": ("STRING", {"forceInput": False}),
            },
        }

    @classmethod
    def VALIDATE_INPUTS(s, input_types):
        return True


    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("save_path", )
    FUNCTION = "load_model_from_s3"
    CATEGORY = "Utilities"

    def load_model_from_s3(self, download_url, save_path):
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            logger.info(f"Model downloaded and saved to {save_path}")
            return (save_path, )
        except Exception as e:
            raise Exception(f"Failed to download model from S3: {str(e)}")


class LoadModelFromPrivateS3:
    """
    Loads a model from a private S3 bucket and saves it to a filepath
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "s3_key": ("STRING", {"forceInput": False}),
                "save_path": ("STRING", {"forceInput": False}),
            },
        }

    RETURN_TYPES = ("STRING", )
    RETURN_NAMES = ("save_path", )
    FUNCTION = "load_model_from_s3"
    CATEGORY = "Utilities"

    def load_model_from_s3(self, s3_key, save_path):
        if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
            raise Exception("AWS credentials not set")

        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

        try:
            s3_client.download_file(S3_BUCKET_NAME, s3_key, save_path)
            logger.info(f"Model downloaded from S3 key {s3_key} and saved to {save_path}")
            return (save_path, )
        except Exception as e:
            raise Exception(f"Failed to download model from S3: {str(e)}")