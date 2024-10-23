print("Initializing Flowscale Nodes")

from .api.io import * 
from .api.log import *

from .nodes.s3_utils import UploadModelToS3
from nodes.model_utils import LoadModelFromCivitAI
from nodes.flowscale_volume_utils import UploadModelToFlowscaleVolume

NODE_CLASS_MAPPINGS = { 
  "UploadModelToS3": UploadModelToS3,
  "LoadModelFromCivitAI": LoadModelFromCivitAI,
  "UploadModelToFlowscaleVolume": UploadModelToFlowscaleVolume
}