print("Initializing FlowScale Nodes")
from dotenv import load_dotenv
load_dotenv()

from .api.io import * 
from .api.log import *
from .api.custom_node import *
from .api.model import *
from .node_index import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS


WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]