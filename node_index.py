from .constants import FS_NODE_ICON
from .nodes.flowscale_volume_utils import SaveModelToFlowscaleVolume
from .nodes.github_readme_extractor import GitHubReadmeExtractor
from .nodes.io.audio import (
    FSCombineAudio,
    FSLoadAudio,
    FSLoadAudioFromURL,
    FSProcessAudio,
    FSSaveAudio,
)
from .nodes.io.image import FSLoadImage, FSLoadImageFromURL, FSSaveImage
from .nodes.io.integer import FSLoadInteger, FSSaveInteger
from .nodes.io.lora import FSLoadLoRA
from .nodes.io.text import FSLoadText, FSSaveText
from .nodes.io.video import FSLoadVideo, FSLoadVideoFromURL, FSSaveVideo
from .nodes.model_utils import LoadModelFromURL
from .nodes.s3_utils import (
    LoadModelFromPrivateS3,
    LoadModelFromPublicS3,
    UploadImageToS3,
    UploadMediaToS3FromLink,
    UploadModelToPrivateS3,
    UploadModelToPublicS3,
    UploadModelToS3,
    UploadTextToS3,
)
from .utilitynodes.file_extractor import FileExtractorNode
from .utilitynodes.fileloader import FileLoaderNode
from .utilitynodes.json_extractor import ExtractPropertyNode
from .utilitynodes.multifileloader import MultiFileLoaderNode
from .utilitynodes.time_utils import FSDelay
from .utilitynodes.webhook import WebhookSender

NODE_CLASS_MAPPINGS = {
    "UploadModelToS3": UploadModelToS3,
    "UploadImageToS3": UploadImageToS3,
    "UploadMediaToS3FromLink": UploadMediaToS3FromLink,
    "UploadTextToS3": UploadTextToS3,
    "UploadModelToPublicS3": UploadModelToPublicS3,
    "UploadModelToPrivateS3": UploadModelToPrivateS3,
    "LoadModelFromPublicS3": LoadModelFromPublicS3,
    "LoadModelFromPrivateS3": LoadModelFromPrivateS3,
    "LoadModelFromURL": LoadModelFromURL,
    "SaveModelToFlowscaleVolume": SaveModelToFlowscaleVolume,
    "WebhookSender": WebhookSender,
    "FileLoaderNode": FileLoaderNode,
    "MultiFileLoaderNode": MultiFileLoaderNode,
    "FileExtractorNode": FileExtractorNode,
    "ExtractPropertyNode": ExtractPropertyNode,
    "FSLoadInteger": FSLoadInteger,
    "FSSaveInteger": FSSaveInteger,
    "FSLoadText": FSLoadText,
    "FSSaveText": FSSaveText,
    "FSLoadLoRA": FSLoadLoRA,
    "FSLoadImage": FSLoadImage,
    "FSLoadImageFromURL": FSLoadImageFromURL,
    "FSSaveImage": FSSaveImage,
    "FSLoadVideo": FSLoadVideo,
    "FSLoadVideoFromURL": FSLoadVideoFromURL,
    "FSSaveVideo": FSSaveVideo,
    "FSLoadAudio": FSLoadAudio,
    "FSLoadAudioFromURL": FSLoadAudioFromURL,
    "FSSaveAudio": FSSaveAudio,
    "FSProcessAudio": FSProcessAudio,
    "FSCombineAudio": FSCombineAudio,
    "GithubReadmeExtractor": GitHubReadmeExtractor,
    "FSDelay": FSDelay,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "UploadModelToS3": f"[FS]{FS_NODE_ICON}Upload Model to S3",
    "UploadImageToS3": f"[FS]{FS_NODE_ICON}Upload Image to S3",
    "UploadMediaToS3FromLink": f"[FS]{FS_NODE_ICON}Upload Media to S3 from Link",
    "UploadTextToS3": f"[FS]{FS_NODE_ICON}Upload Text to S3",
    "UploadModelToPublicS3": f"[FS]{FS_NODE_ICON}Upload Model to Public S3",
    "UploadModelToPrivateS3": f"[FS]{FS_NODE_ICON}Upload Model to Private S3",
    "LoadModelFromPublicS3": f"[FS]{FS_NODE_ICON}Load Model from Public S3",
    "LoadModelFromPrivateS3": f"[FS]{FS_NODE_ICON}Load Model to Private S3",
    "LoadModelFromURL": f"[FS]{FS_NODE_ICON}Load Model from URL",
    "SaveModelToFlowscaleVolume": f"[FS]{FS_NODE_ICON}Save Model to Flowscale Volume",
    "GithubReadmeExtractor": f"[FS]{FS_NODE_ICON}Extract GitHub Readme",
    "WebhookSender": f"[FS]{FS_NODE_ICON}Send to Webhook",
    "FileLoaderNode": f"[FS]{FS_NODE_ICON}Load File",
    "MultiFileLoaderNode": f"[FS]{FS_NODE_ICON}Multi-File Uploader",
    "FileExtractorNode": f"[FS]{FS_NODE_ICON}Extract File",
    "ExtractPropertyNode": f"[FS]{FS_NODE_ICON}Extract Property from JSON",
    "FSLoadInteger": f"[FS]{FS_NODE_ICON}Load Integer (Input)",
    "FSSaveInteger": f"[FS]{FS_NODE_ICON}Save Integer (Output)",
    "FSLoadText": f"[FS]{FS_NODE_ICON}Load Text (Input)",
    "FSSaveText": f"[FS]{FS_NODE_ICON}Save Text (Output)",
    "FSLoadLoRA": f"[FS]{FS_NODE_ICON}Load LoRA (Input)",
    "FSLoadImage": f"[FS]{FS_NODE_ICON}Load Image (Input)",
    "FSLoadImageFromURL": f"[FS]{FS_NODE_ICON}Load Image from URL (Input)",
    "FSSaveImage": f"[FS]{FS_NODE_ICON}Save Image (Output)",
    "FSLoadVideo": f"[FS]{FS_NODE_ICON}Load Video (Input)",
    "FSLoadVideoFromURL": f"[FS]{FS_NODE_ICON}Load Video from URL (Input)",
    "FSSaveVideo": f"[FS]{FS_NODE_ICON}Save Video (Output)",
    "FSLoadAudio": f"[FS]{FS_NODE_ICON}Load Audio (Input)",
    "FSLoadAudioFromURL": f"[FS]{FS_NODE_ICON}Load Audio from URL (Input)",
    "FSSaveAudio": f"[FS]{FS_NODE_ICON}Save Audio (Output)",
    "FSProcessAudio": f"[FS]{FS_NODE_ICON}Process Audio",
    "FSCombineAudio": f"[FS]{FS_NODE_ICON}Combine Audio",
    "FSDelay": f"[FS]{FS_NODE_ICON}Delay",
}
