print("Initializing Flowscale Nodes")
from dotenv import load_dotenv

from .api.io import * 
from .api.log import *
from .api.custom_node import *

from .nodes.s3_utils import UploadModelToS3, UploadModelToPublicS3, UploadModelToPrivateS3, LoadModelFromPublicS3, LoadModelFromPrivateS3, UploadImageToS3, UploadMediaToS3FromLink, UploadTextToS3
from .nodes.model_utils import LoadModelFromCivitAI
from .nodes.flowscale_volume_utils import SaveModelToFlowscaleVolume
from .utilitynodes.webhook import WebhookSender
from .utilitynodes.fileloader import FileLoaderNode
from .utilitynodes.json_extractor import ExtractPropertyNode

load_dotenv()

NODE_CLASS_MAPPINGS = { 
  "UploadModelToS3": UploadModelToS3,
  "UploadImageToS3": UploadImageToS3,
  "UploadMediaToS3FromLink": UploadMediaToS3FromLink,
  "UploadTextToS3": UploadTextToS3,
  "UploadModelToPublicS3": UploadModelToPublicS3,
  "UploadModelToPrivateS3": UploadModelToPrivateS3,
  "LoadModelFromPublicS3": LoadModelFromPublicS3,
  "LoadModelFromPrivateS3": LoadModelFromPrivateS3,
  "LoadModelFromCivitAI": LoadModelFromCivitAI,
  "SaveModelToFlowscaleVolume": SaveModelToFlowscaleVolume,
  "WebhookSender": WebhookSender,
  "FileLoaderNode": FileLoaderNode,
  "ExtractPropertyNode": ExtractPropertyNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
  "UploadModelToS3": "[FS] Upload Model to S3",
  "UploadImageToS3": "[FS] Upload Image to S3",
  "UploadMediaToS3FromLink": "[FS] Upload Media to S3 from Link",
  "UploadTextToS3": "[FS] Upload Text to S3",
  "UploadModelToPublicS3": "[FS] Upload Model to Public S3",
  "UploadModelToPrivateS3": "[FS] Upload Model to Private S3",
  "LoadModelFromPublicS3": "[FS] Load Model from Public S3",
  "LoadModelFromPrivateS3": "[FS] Load Model to Private S3",
  "LoadModelFromCivitAI": "[FS] Load Model from CivitAI",
  "SaveModelToFlowscaleVolume": "[FS] Save Model to Flowscale Volume",
  "WebhookSender": "[FS] Send to Webhook",
  "FileLoaderNode": "[FS] Load File",
  "ExtractPropertyNode": "[FS] Extract Property",
}