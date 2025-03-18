from .nodes.s3_utils import UploadModelToS3, UploadModelToPublicS3, UploadModelToPrivateS3, LoadModelFromPublicS3, LoadModelFromPrivateS3, UploadImageToS3, UploadMediaToS3FromLink, UploadTextToS3
from .nodes.model_utils import LoadModelFromCivitAI
from .nodes.flowscale_volume_utils import SaveModelToFlowscaleVolume
from .nodes.io.text import FSLoadText, FSSaveText
from .nodes.io.image import FSLoadImage, FSSaveImage
from .nodes.io.video import FSLoadVideo, FSSaveVideo
from .utilitynodes.webhook import WebhookSender
from .nodes.github_readme_extractor import GitHubReadmeExtractor
from .utilitynodes.fileloader import FileLoaderNode
from .utilitynodes.json_extractor import ExtractPropertyNode

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
  "FSLoadText": FSLoadText,
  "FSSaveText": FSSaveText,
  "FSLoadImage": FSLoadImage,
  "FSSaveImage": FSSaveImage,
  "FSLoadVideo": FSLoadVideo,
  "FSSaveVideo": FSSaveVideo,
  "GithubReadmeExtractor": GitHubReadmeExtractor,
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
  "GithubReadmeExtractor": "[FS] Extract GitHub Readme",
  "WebhookSender": "[FS] Send to Webhook",
  "FileLoaderNode": "[FS] Load File",
  "ExtractPropertyNode": "[FS] Extract Property from JSON",
  "FSLoadText": "[FS] Load Text (Input)",
  "FSSaveText": "[FS] Save Text (Output)",
  "FSLoadImage": "[FS] Load Image (Input)",
  "FSSaveImage": "[FS] Save Image (Output)",
  "FSLoadVideo": "[FS] Load Video (Input)",
  "FSSaveVideo": "[FS] Save Video (Output)",
}