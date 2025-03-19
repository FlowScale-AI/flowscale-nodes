# FlowScale Nodes for ComfyUI

FlowScale Nodes is a collection of custom nodes for [ComfyUI](https://github.com/comfyanonymous/ComfyUI) that enhances your workflow with powerful media handling, cloud integration, and utility features. While designed to work seamlessly with the [FlowScale](https://flowscale.ai/) platform, many features can be used independently in any ComfyUI setup.

> **Note:** For the best experience and full feature set, these nodes integrate exceptionally well with FlowScale environments, where many configurations come pre-set.

## Features

- ⚡ IO Nodes: Easy loading and saving of text, images, videos, audio, and  files
- 🔄 Cloud Integration: Upload and download models, images, videos, and text to AWS S3
- 📦 Utilities: Extract files, process JSON, send webhooks
- 🤖 Model Management: Load models from CivitAI and save to volumes
- 🎞️ Media Preview: Live previews for images, videos, and audio files
- 📝 Text Processing: Load, save, and process text content
- 🧰 Multi-file handling: Batch upload multiple files together

## Enhanced FlowScale Integration

When used with FlowScale, these nodes unlock additional capabilities:

- Pre-configured integration for models, images, video, and audio
- Specialized volume management
- Optimized for FlowScale environments

## Installation

### Requirements

For basic functionality:
- ComfyUI installed

For enhanced functionality:
- AWS S3 credentials (for S3 nodes)
- A FlowScale environment (for seamless integration)

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/flowscale-ai/flowscale-nodes
cd flowscale-nodes
pip install -r requirements.txt
```

### Environment Variables

These nodes use environment variables for certain features. In FlowScale environments, these are automatically configured.

For standalone use, you'll need to configure:

- For S3 nodes:
  - `AWS_S3_ACCESS_KEY_ID`
  - `AWS_S3_SECRET_ACCESS_KEY`
  - `AWS_S3_REGION` (default: "us-east-1")
  - `AWS_S3_BUCKET_NAME`

You can either set these in your environment in Project Settings within a project in FlowScale; or create a `.env` file in the flowscale-nodes directory.

## Node Categories

### FlowScale/Media

Media handling nodes for various file types:

#### Image
- **FSLoadImage**: Load an image from your filesystem
- **FSLoadImageFromURL**: Load an image from a URL
- **FSSaveImage**: Save an image to your filesystem with format options

#### Video
- **FSLoadVideo**: Load a video file from your filesystem
- **FSLoadVideoFromURL**: Load a video from a URL
- **FSSaveVideo**: Save a video to your filesystem

#### Audio
- **FSLoadAudio**: Load an audio file from your filesystem
- **FSLoadAudioFromURL**: Load audio from a URL
- **FSSaveAudio**: Save audio to your filesystem
- **FSProcessAudio**: Process audio files with various operations
- **FSCombineAudio**: Combine multiple audio files together

#### Text
- **FSLoadText**: Load text content from a file
- **FSSaveText**: Save text content to a file

### FlowScale/Cloud

Cloud storage and integration nodes:

#### Models
- **UploadModelToS3**: Upload a model file to S3
- **UploadModelToPublicS3**: Upload a model to a public S3 bucket
- **UploadModelToPrivateS3**: Upload a model to a private S3 bucket
- **LoadModelFromPublicS3**: Load a model from a public S3 URL
- **LoadModelFromPrivateS3**: Load a model from a private S3 key

#### Media
- **UploadImageToS3**: Upload images to S3
- **UploadMediaToS3FromLink**: Upload media from a URL to S3
- **UploadTextToS3**: Upload text content to S3

### FlowScale/Files

File handling and processing nodes:

#### Load
- **FileLoaderNode**: Load individual or zipped text files

#### Batch
- **MultiFileLoaderNode**: Load multiple files at once with metadata extraction and filtering

#### Extract
- **FileExtractorNode**: Extract files from archives

#### Parse
- **ExtractPropertyNode**: Extract specific properties from JSON data

### FlowScale/Models

Model management nodes:

#### Download
- **LoadModelFromCivitAI**: Load models directly from CivitAI

#### Storage
- **SaveModelToFlowscaleVolume**: Save models to a volume with metadata for persistent storage

### FlowScale/Web

Web integration nodes:

#### GitHub
- **GithubReadmeExtractor**: Extract README content from GitHub repositories

#### Webhooks
- **WebhookSender**: Send data to webhook endpoints

### FlowScale/Utils

General utility nodes:

#### Time
- **Delay**: Add configurable delays to workflows

## Usage Examples

### Loading and Saving Images

1. Add the `FSLoadImage` node to load an image from your filesystem
2. Process the image with ComfyUI nodes
3. Use `FSSaveImage` to save the resulting image

### Uploading Models to S3

1. Use `LoadModelFromCivitAI` to download a model
2. Connect the output to `UploadModelToS3` to store it in your S3 bucket
3. Use the returned URL to access your model

### Working with Multiple Files

1. Add the `MultiFileLoaderNode` for batch processing of files
2. Connect to other nodes for processing each file
3. Use the file metadata for conditional operations

### Audio Processing

1. Load audio with `FSLoadAudio` 
2. Process it with `FSProcessAudio`
3. Combine with another audio file using `FSCombineAudio`
4. Save the result with `FSSaveAudio`

## FlowScale User Benefits

If you're using FlowScale, you'll enjoy these additional benefits:

- Automatic deployment API configuration
- Directly save a trained model to FlowScale Volume

## Development

To add new nodes or contribute to the project:

1. Fork the repository
2. Add your node in the appropriate category folder
3. Register your node in `node_index.py`
4. Add UI features in `web/js/flowscale.core.js` if needed
5. Submit a pull request

## Support

For general node functionality questions, please open an issue in the GitHub repository.

If you're using FlowScale and need platform-specific help, FlowScale support is available to assist you.

## Credits

Developed with ❤️ by the FlowScale team and contributors