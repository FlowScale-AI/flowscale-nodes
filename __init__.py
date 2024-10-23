print("Initializing Flowscale Nodes")
from dotenv import load_dotenv

from .api.io import * 
from .api.log import *

from .nodes.s3_utils import UploadModelToS3
from .nodes.model_utils import LoadModelFromCivitAI
from .nodes.flowscale_volume_utils import UploadModelToFlowscaleVolume

load_dotenv()

NODE_CLASS_MAPPINGS = { 
  "UploadModelToS3": UploadModelToS3,
  "LoadModelFromCivitAI": LoadModelFromCivitAI,
  "UploadModelToFlowscaleVolume": UploadModelToFlowscaleVolume
}

NODE_DISPLAY_NAME_MAPPINGS = {
  "UploadModelToS3": "[FS] Upload Model to S3",
  "LoadModelFromCivitAI": "[FS] Load Model from CivitAI",
  "UploadModelToFlowscaleVolume": "[FS] Upload Model to Flowscale Volume"
}