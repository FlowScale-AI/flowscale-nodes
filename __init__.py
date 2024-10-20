print("Initializing Flowscale Nodes")

from .nodes.input import SaveBatchImagesNode, LoadImagesFromDirectoryNode
from .api import *

NODE_CLASS_MAPPINGS = {
  "SaveBatchImagesNode": SaveBatchImagesNode,
  "LoadImagesFromDirectoryNode": LoadImagesFromDirectoryNode
}