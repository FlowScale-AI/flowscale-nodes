from .nodes.s3_utils import UploadModelToS3, UploadModelToPublicS3, UploadModelToPrivateS3, LoadModelFromPublicS3, LoadModelFromPrivateS3, UploadImageToS3, UploadMediaToS3FromLink, UploadTextToS3
from .nodes.model_utils import LoadModelFromCivitAI
from .nodes.flowscale_volume_utils import SaveModelToFlowscaleVolume
from .nodes.io.text import FSLoadText, FSSaveText
from .nodes.io.image import FSLoadImage, FSSaveImage
from .nodes.io.video import FSLoadVideo, FSLoadVideoFromURL, FSSaveVideo
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
  "FSLoadVideoFromURL": FSLoadVideoFromURL,
  "FSSaveVideo": FSSaveVideo,
  "GithubReadmeExtractor": GitHubReadmeExtractor,
}

NODE_DISPLAY_NAME_MAPPINGS = {
  "UploadModelToS3": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Upload Model to S3",
  "UploadImageToS3": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Upload Image to S3",
  "UploadMediaToS3FromLink": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Upload Media to S3 from Link",
  "UploadTextToS3": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Upload Text to S3",
  "UploadModelToPublicS3": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Upload Model to Public S3",
  "UploadModelToPrivateS3": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Upload Model to Private S3",
  "LoadModelFromPublicS3": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Load Model from Public S3",
  "LoadModelFromPrivateS3": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Load Model to Private S3",
  "LoadModelFromCivitAI": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Load Model from CivitAI",
  "SaveModelToFlowscaleVolume": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Save Model to Flowscale Volume",
  "GithubReadmeExtractor": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Extract GitHub Readme",
  "WebhookSender": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Send to Webhook",
  "FileLoaderNode": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Load File",
  "ExtractPropertyNode": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Extract Property from JSON",
  "FSLoadText": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Load Text (Input)",
  "FSSaveText": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Save Text (Output)",
  "FSLoadImage": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Load Image (Input)",
  "FSSaveImage": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Save Image (Output)",
  "FSLoadVideo": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Load Video (Input)",
  "FSLoadVideoFromURL": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Load Video from URL (Input)",
  "FSSaveVideo": "[FS] <img src='https://hub-beta.flowscale.ai/logo.svg' width='16' height='16' style='vertical-align: middle'> Save Video (Output)",
}