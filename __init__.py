print("Initializing Flowscale Nodes")

from .api.io import * 
from .api.log import *

from .nodes.s3_utils import UploadModelToS3

NODE_CLASS_MAPPINGS = { 
  "UploadModelToS3": UploadModelToS3
}