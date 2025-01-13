print("Initializing Flowscale Nodes")
from dotenv import load_dotenv

from .api.io import * 
from .api.log import *
from .api.custom_node import *

from .nodes.s3_utils import UploadModelToS3, UploadModelToPublicS3, UploadModelToPrivateS3, LoadModelFromPublicS3, LoadModelFromPrivateS3
from .nodes.model_utils import LoadModelFromCivitAI
from .nodes.flowscale_volume_utils import SaveModelToFlowscaleVolume
from .nodes.time_utils import Delay
from .nodes.upload import UploadImages

load_dotenv()

NODE_CLASS_MAPPINGS = { 
  "UploadModelToS3": UploadModelToS3,
  "UploadModelToPublicS3": UploadModelToPublicS3,
  "UploadModelToPrivateS3": UploadModelToPrivateS3,
  "LoadModelFromPublicS3": LoadModelFromPublicS3,
  "LoadModelFromPrivateS3": LoadModelFromPrivateS3,
  "LoadModelFromCivitAI": LoadModelFromCivitAI,
  "SaveModelToFlowscaleVolume": SaveModelToFlowscaleVolume,
  "Delay": Delay,
}

NODE_DISPLAY_NAME_MAPPINGS = {
  "UploadModelToS3": "[FS] Upload Model to S3",
  "UploadModelToPublicS3": "[FS] Upload Model to Public S3",
  "UploadModelToPrivateS3": "[FS] Upload Model to Private S3",
  "LoadModelFromPublicS3": "[FS] Load Model from Public S3",
  "LoadModelFromPrivateS3": "[FS] Load Model to Private S3",
  "LoadModelFromCivitAI": "[FS] Load Model from CivitAI",
  "SaveModelToFlowscaleVolume": "[FS] Save Model to Flowscale Volume",
  "Delay": "[FS] Delay",
}