import os
import boto3

class UploadModelToS3:
  """
  Uploads a model to S3
  """
  
  @classmethod
  def INPUT_TYPES(cls):
    return {
      "required": {
          "filepath": ("STRING", {"multiline": False})
      }
    }
    
  RETURN_TYPES = ("STRING",)
  FUNCTION = "upload_model_to_s3"
  CATEGORY = "Utilities"
  
  def upload_model_to_s3(self, filepath):
    AWS_ACCESS_KEY_ID = os.getenv("AWS_S3_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_S3_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_S3_REGION", "us-east-1")
    S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
    CONTAINER_ID = os.getenv("CONTAINER_ID")
    
    if filepath.startswith("./") or filepath.startswith("../"):
        filepath = filepath.lstrip("./").lstrip("../")
    if filepath.startswith("/") or filepath.startswith("\\"):
        filepath = filepath.lstrip("/").lstrip("\\")

    base_directory = os.getcwd()
    sanitized_filepath = os.path.normpath(filepath).lstrip(os.sep).rstrip(os.sep)
    absolute_filepath = os.path.abspath(os.path.join(base_directory, sanitized_filepath))
    
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
      raise Exception("AWS credentials not set")
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    s3_key = os.path.join("models", CONTAINER_ID, os.path.basename(absolute_filepath))
    
    try:
      s3_client.upload_file(absolute_filepath, S3_BUCKET_NAME, s3_key)
      download_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
      return download_url, filepath
    except Exception as e:
      raise Exception(f"Failed to upload model to S3: {str(e)}")