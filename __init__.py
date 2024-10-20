print("Initializing Flowscale Nodes")

from .nodes.input import SaveBatchImagesNode
from .api import *

NODE_CLASS_MAPPINGS = {
  "SaveBatchImagesNode": SaveBatchImagesNode,
}