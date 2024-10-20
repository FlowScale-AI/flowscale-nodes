print("Initializing Flowscale Nodes")

from .nodes.input import LoadImagesBatch
from .api import *

NODE_CLASS_MAPPINGS = {
  "Load Images Batch": LoadImagesBatch
}