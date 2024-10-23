print("Initializing Flowscale Nodes")
from dotenv import load_dotenv

from .api.io import * 
from .api.log import *

from .nodes.s3_utils import UploadModelToS3
from .nodes.model_utils import LoadModelFromCivitAI
from .nodes.flowscale_volume_utils import UploadModelToFlowscaleVolume

load_dotenv()

NODE_CLASS_MAPPINGS = { 
  "Upload Model To S3": UploadModelToS3,
  "Load Model From CivitAI": LoadModelFromCivitAI,
  "Upload Model To Flowscale Volume": UploadModelToFlowscaleVolume
}