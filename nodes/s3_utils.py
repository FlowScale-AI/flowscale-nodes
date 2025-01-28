import os
import boto3
import logging
import numpy as np
from PIL import Image
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from boto3.exceptions import S3UploadFailedError
import folder_paths 
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AWS_ACCESS_KEY_ID = os.environ.get("AWS_S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_S3_SECRET_ACCESS_KEY")
AWS_REGION = os.environ.get("AWS_S3_REGION", "us-east-1")
S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")


class UploadModelToS3:
  """
  Uploads a model to S3
  """
  
  @classmethod
  def INPUT_TYPES(cls):
    return {
      "required": {
          "filepath": ("STRING", {"forceInput": True}),
          "model_name": ("STRING", {"forceInput": False})
      },
    }
    
  RETURN_TYPES = ("STRING", "STRING")
  RETURN_NAMES = ("download_url", "model_name")
  FUNCTION = "upload_model_to_s3"
  CATEGORY = "Utilities"
  
  def upload_model_to_s3(self, filepath, model_name=None):
    CONTAINER_ID = os.environ.get("CONTAINER_ID")
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
      if "." not in model_name and "." not in os.path.basename(absolute_filepath):
        absolute_filepath += ".safetensors"
      if "." not in model_name:
        modified_model_name = model_name + ".safetensors"
      s3_key = os.path.join("models", CONTAINER_ID, modified_model_name)
    else:
      if "." not in os.path.basename(absolute_filepath):
        absolute_filepath += ".safetensors"
      s3_key = os.path.join("models", CONTAINER_ID, os.path.basename(absolute_filepath))
    
    try:
      s3_client.upload_file(absolute_filepath, S3_BUCKET_NAME, s3_key)
      download_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
      return (download_url, model_name,)
    except Exception as e:
      raise Exception(f"Failed to upload model to S3: {str(e)}")

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
    
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
      raise Exception("AWS credentials not set")
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    if model_name:
      if "." not in model_name:
          modified_model_name = model_name + ".safetensors"
      else:
          modified_model_name = model_name
      
      logger.info(os.path.join(base_directory, sanitized_filepath))
      if os.path.isdir(os.path.join(base_directory, sanitized_filepath)):
          absolute_filepath = os.path.join(base_directory, sanitized_filepath, modified_model_name)
          logger.info(f"Direcory - Uploading model from {absolute_filepath}")
      else:
          absolute_filepath = os.path.join(base_directory, sanitized_filepath)
          if "." not in os.path.basename(absolute_filepath):
              absolute_filepath += ".safetensors"
          logger.info(f"File - Uploading model from {absolute_filepath}")
      
      logger.info(f"Uploading model from {absolute_filepath}")
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

        if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME]):
            raise Exception("AWS credentials not set")

        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

        if model_name:
          if "." not in model_name:
              modified_model_name = model_name + ".safetensors"
          else:
              modified_model_name = model_name
              
          if os.path.isdir(os.path.join(base_directory, sanitized_filepath)):
              absolute_filepath = os.path.join(base_directory, sanitized_filepath, modified_model_name)
          else:
              absolute_filepath = os.path.join(base_directory, sanitized_filepath)
              if "." not in os.path.basename(absolute_filepath):
                  absolute_filepath += ".safetensors"
          
          logger.info(f"Uploading model from {absolute_filepath}")
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
            response = httpx.get(download_url, stream=True)
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

        base_directory = os.getcwd()
        save_path = os.path.join(base_directory, save_path)
        
        if os.path.isdir(os.path.dirname(save_path)):
            file_name = os.path.basename(s3_key)
            save_path = os.path.join(save_path, file_name)
    
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))

        logger.info(f"Downloading model from S3 key {s3_key} and saving to {save_path}")
        try:
            s3_client.download_file(S3_BUCKET_NAME, s3_key, save_path)
            logger.info(f"Model downloaded from S3 key {s3_key} and saved to {save_path}")
            return (save_path, )
        except Exception as e:
            raise Exception(f"Failed to download model from S3: {str(e)}")
        
        

class UploadImageToS3:
    """
    Uploads images to S3 and returns download URLs
    """

    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get("AWS_S3_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_S3_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("AWS_S3_REGION", "us-east-1")
        )
        self.region = os.environ.get("AWS_S3_REGION", "us-east-1")
        self.bucket_name = os.environ.get("AWS_S3_BUCKET_NAME")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to upload."}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "Filename for saved images"}),            },
            "optional": {
                "user_id": ("STRING", {"default": "flowscale_user", "tooltip": "User ID to add to metadata"}),
                "identifier": ("STRING", {"default": "default", "tooltip": "Identifier to add to metadata"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("s3_urls",)
    FUNCTION = "upload_images_to_s3"
    CATEGORY = "Utilities"
    OUTPUT_NODE = True
  
    def upload_images_to_s3(self, images, filename_prefix="ComfyUI", user_id="flowscale_user", identifier="default"):
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0]
        )
        results = list()
        s3_urls = []

        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            # Save image locally
            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            local_file = f"{filename_with_batch_num}_{counter:05}_.png"
            local_file_path = os.path.join(full_output_folder, local_file)
            img.save(local_file_path, compress_level=4)

            # Upload to S3
            s3_filename = f"duke_media/{identifier}/{user_id}_{identifier}" + local_file
            try:
                logger.info(f"Uploading file {local_file} to S3 bucket {self.bucket_name}...")
                self.s3_client.upload_file(
                    local_file_path, 
                    self.bucket_name, 
                    s3_filename,
                    ExtraArgs={"Metadata": {"user_id": user_id, "identifier": identifier}}
                )
                s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_filename}"
                s3_urls.append(s3_url)
                results.append({
                    "filename": s3_filename,
                    "type": "output",
                    "message": f"File {s3_filename} uploaded successfully to S3 bucket {self.bucket_name}."
                })
                logger.info(f"File {s3_filename} uploaded successfully to S3 bucket {self.bucket_name}.")
            except NoCredentialsError:
                logger.error("AWS credentials not found in environment variables.")
                results.append({
                    "filename": local_file,
                    "subfolder": subfolder,
                    "type": "output",
                    "error": "AWS credentials not found in environment variables."
                })
            except PartialCredentialsError:
                logger.error("Incomplete AWS credentials provided.")
                results.append({
                    "filename": local_file,
                    "subfolder": subfolder,
                    "type": "output",
                    "error": "Incomplete AWS credentials provided."
                })
            except S3UploadFailedError as e:
                logger.error(f"Failed to upload file to S3: {str(e)}")
                results.append({
                    "filename": local_file,
                    "subfolder": subfolder,
                    "type": "output",
                    "error": f"Failed to upload file to S3: {str(e)}"
                })
            except Exception as e:
                logger.error(f"An unexpected error occurred: {str(e)}")
                results.append({
                    "filename": local_file,
                    "subfolder": subfolder,
                    "type": "output",
                    "error": f"An unexpected error occurred: {str(e)}"
                })

            counter += 1

        return {"ui": {"images": results}, "result": (",".join(s3_urls),)}


class UploadMediaToS3FromLink:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.region = AWS_REGION
        self.bucket_name = S3_BUCKET_NAME

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "link": ("STRING", {"default": "", "tooltip": "Direct image link to copy to S3"}),
                "filename_prefix": ("STRING", {"default": "ComfyUI_Video", "tooltip": "Filename prefix for the S3 object"})
            },
            "optional": {
                "user_id": ("STRING", {"default": "flowscale_user", "tooltip": "User ID to add to metadata"}),
                "identifier": ("STRING", {"default": "default", "tooltip": "Identifier to add to metadata"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("s3_url",)
    FUNCTION = "upload_media_to_s3"
    CATEGORY = "Utilities"
    OUTPUT_NODE = True

    def upload_media_to_s3(self, link, filename_prefix="default", user_id="flowscale_user", identifier="default"):
        import httpx
        import tempfile
        import os
        from uuid import uuid4

        results = []
        s3_urls = []

        if not link:
            error_msg = "No link provided."
            logger.error(error_msg)
            results.append({
                "filename": None,
                "type": "output",
                "error": error_msg
            })
            return {"ui": {"images": results}, "result": ("",)}

        unique_id = str(uuid4())
        extension = os.path.splitext(link)[1] if "." in os.path.basename(link) else ".png"
        temp_filename = f"{filename_prefix}_{unique_id}{extension}"

        with tempfile.TemporaryDirectory() as temp_dir:
            local_file_path = os.path.join(temp_dir, temp_filename)
            try:
                logger.info(f"Downloading image from {link}...")
                response = httpx.get(link)
                response.raise_for_status()
                with open(local_file_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Downloaded image from {link} to {local_file_path}.")
            except httpx.HTTPError as e:
                error_msg = f"Failed to download image from URL: {e}"
                logger.error(error_msg)
                results.append({
                    "filename": temp_filename,
                    "type": "output",
                    "error": error_msg
                })
                return {"ui": {"images": results}, "result": ("",)}

            # Upload the downloaded file to S3
            s3_filename = f"duke_media/{identifier}/{user_id}_{identifier}" + temp_filename
            try:
                self.s3_client.upload_file(
                    local_file_path,
                    self.bucket_name,
                    s3_filename,
                    ExtraArgs={"Metadata": {"user_id": user_id, "identifier": identifier}}
                )
                s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_filename}"
                s3_urls.append(s3_url)
                results.append({
                    "filename": s3_filename,
                    "type": "output",
                    "message": f"File {s3_filename} uploaded successfully to S3 bucket {self.bucket_name}."
                })
                logger.info(f"File {s3_filename} uploaded successfully to S3 bucket {self.bucket_name}.")
            except NoCredentialsError:
                error_msg = "AWS credentials not found in environment variables."
                logger.error(error_msg)
                results.append({
                    "filename": s3_filename,
                    "type": "output",
                    "error": error_msg
                })
            except PartialCredentialsError:
                error_msg = "Incomplete AWS credentials provided."
                logger.error(error_msg)
                results.append({
                    "filename": s3_filename,
                    "type": "output",
                    "error": error_msg
                })
            except S3UploadFailedError as e:
                error_msg = f"Failed to upload file to S3: {str(e)}"
                logger.error(error_msg)
                results.append({
                    "filename": s3_filename,
                    "type": "output",
                    "error": error_msg
                })
            except Exception as e:
                error_msg = f"An unexpected error occurred: {str(e)}"
                logger.error(error_msg)
                results.append({
                    "filename": s3_filename,
                    "type": "output",
                    "error": error_msg
                })

        return {"ui": {"images": results}, "result": (",".join(s3_urls),)}

class UploadTextToS3:
    """
    Creates a text file from input string and uploads to S3 with user metadata
    """
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.region = AWS_REGION
        self.bucket_name = S3_BUCKET_NAME

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "Text content to save"}),
                "filename_prefix": ("STRING", {"default": "ComfyUI_Text", "tooltip": "Filename prefix for the text file"}),
            },
            "optional": {
                "user_id": ("STRING", {"default": "flowscale_user", "tooltip": "User ID to add to metadata"}),
                "identifier": ("STRING", {"default": "default", "tooltip": "Identifier to add to metadata"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("s3_url",)
    FUNCTION = "upload_text_to_s3"
    CATEGORY = "Utilities"
    OUTPUT_NODE = True

    def upload_text_to_s3(self, text, filename_prefix="ComfyUI_Text", user_id="flowscale_user", identifier="default"):
        import tempfile
        import os
        from uuid import uuid4

        results = []
        s3_urls = []

        if not text.strip():
            error_msg = "No text content provided"
            logger.error(error_msg)
            results.append({
                "filename": None,
                "type": "output",
                "error": error_msg
            })
            return {"ui": {"texts": results}, "result": ("",)}

        # Create temporary text file
        unique_id = str(uuid4())
        txt_filename = f"{filename_prefix}_{unique_id}.txt"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            local_file_path = os.path.join(temp_dir, txt_filename)
            
            try:
                # Write text to file
                with open(local_file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                logger.info(f"Created temporary text file at {local_file_path}")

                s3_filename = f"duke_media/{identifier}/{user_id}_{identifier}" + txt_filename
                # Upload to S3
                self.s3_client.upload_file(
                    local_file_path,
                    self.bucket_name,
                    s3_filename,
                    ExtraArgs={
                        'Metadata': {
                            'user_id': user_id,
                            'identifier': identifier,
                            'content-type': 'text/plain'
                        }
                    }
                )
                
                s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_filename}"
                s3_urls.append(s3_url)
                results.append({
                    "filename": s3_filename,
                    "type": "output",
                    "message": f"Text file {s3_filename} uploaded successfully with metadata"
                })
                logger.info(f"Text file uploaded to {s3_url}")
                
            except NoCredentialsError:
                error_msg = "AWS credentials not found in environment variables"
                logger.error(error_msg)
                results.append({
                    "filename": s3_filename,
                    "type": "output",
                    "error": error_msg
                })
            except S3UploadFailedError as e:
                error_msg = f"S3 upload failed: {str(e)}"
                logger.error(error_msg)
                results.append({
                    "filename": s3_filename,
                    "type": "output",
                    "error": error_msg
                })
            except Exception as e:
                error_msg = f"Error processing text file: {str(e)}"
                logger.error(error_msg)
                results.append({
                    "filename": s3_filename,
                    "type": "output",
                    "error": error_msg
                })

        return {"ui": {"texts": results}, "result": (",".join(s3_urls),)}