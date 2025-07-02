from dotenv import load_dotenv

from .api.custom_node import *  # noqa: F403
from .api.io import *  # noqa: F403
from .api.log import *  # noqa: F403
from .api.model import *  # noqa: F403
from .node_index import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

print("Initializing FlowScale Nodes")
load_dotenv()

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
