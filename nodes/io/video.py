import os
import random
import string
import numpy as np
import cv2
import folder_paths
import tempfile
import re
import requests
import shutil
import subprocess
import torch
import json
import datetime
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of supported video extensions
VIDEO_EXTENSIONS = ['webm', 'mp4', 'mkv', 'gif', 'mov', 'avi', 'wmv']

class FSLoadVideo:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = []
        for f in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, f)):
                file_parts = f.split('.')
                if len(file_parts) > 1 and (file_parts[-1].lower() in VIDEO_EXTENSIONS):
                    files.append(f)
                    
        return {"required": {
                    "video": (sorted(files),),
                    "skip_first_frames": ("INT", {"default": 0, "min": 0, "max": 10000}),
                    "select_every_nth": ("INT", {"default": 1, "min": 1, "max": 100}),
               },
               "optional": {
                     "label": ("STRING", {"default": "Input Video"}),
                },
               "hidden": {
                   "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
               }}

    CATEGORY = "FlowScale/Media/Video"

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGES",)
    FUNCTION = "load_video"

    def load_video(self, video, skip_first_frames=0, select_every_nth=1, prompt=None, extra_pnginfo=None, label="Input Video"):
        logger.info(f"I/O Label: {label}")
        video_path = folder_paths.get_annotated_filepath(video)
        
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Could not open video file: {video_path}")
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        # Skip initial frames
        for _ in range(skip_first_frames):
            cap.read()
        
        frames = []
        frame_idx = 0
        
        # Read frames
        while frame_idx < total_frames:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_idx += 1
            
            # Select every nth frame
            if (frame_idx - 1) % select_every_nth != 0:
                continue
                
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to float32 and normalize
            frame_float = np.array(frame_rgb).astype(np.float32) / 255.0
            
            frames.append(frame_float)
        
        cap.release()
        
        # Check if we got any frames
        if len(frames) == 0:
            raise ValueError("No frames could be extracted from the video")
            
        # Convert to tensor
        batch = torch.from_numpy(np.stack(frames))
        
        # Prepare preview info
        preview = {
            "ui": {
                "video": [{
                    "filename": os.path.basename(video_path),
                    "type": "input",
                    "fps": fps,
                    "total_frames": total_frames,
                    "format": os.path.splitext(video_path)[1][1:],
                    "url": f"file={video_path}"
                }]
            }
        }
        
        return {"ui": preview, "result": (batch,)}

    @classmethod
    def IS_CHANGED(s, video, **kwargs):
        video_path = folder_paths.get_annotated_filepath(video)
        m_time = os.path.getmtime(video_path)
        return m_time
    
    @classmethod
    def VALIDATE_INPUTS(s, video, **kwargs):
        if not folder_paths.exists_annotated_filepath(video):
            return "Invalid video file: {}".format(video)
        return True
    
class FSLoadVideoFromURL:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video_url": ("STRING",),
                "skip_first_frames": ("INT", {"default": 0, "min": 0, "max": 10000}),
                "select_every_nth": ("INT", {"default": 1, "min": 1, "max": 100}),
            },
            "optional": {
                "label": ("STRING", {"default": "Input Video"}),
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            }
        }
    CATEGORY = "FlowScale/Media/Video"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGES",)
    FUNCTION = "load_video_from_url"

    def load_video_from_url(self, video_url, skip_first_frames=0, select_every_nth=1, prompt=None, extra_pnginfo=None, label="Input Video"):
        logger.info(f"I/O Label: {label}")
        # Check if the URL is valid
        if not re.match(r'^(http|https)://', video_url):
            raise ValueError("Invalid URL format. Please provide a valid HTTP or HTTPS URL.")
        
        # Download the video file
        response = requests.get(video_url)
        if response.status_code != 200:
            raise ValueError(f"Failed to download video from URL: {video_url}")
        
        # Save the video to a temporary file
        temp_video_path = os.path.join(tempfile.gettempdir(), "temp_video.mp4")
        with open(temp_video_path, 'wb') as f:
            f.write(response.content)
            
        # Create preview info
        preview = {
            "ui": {
                "video": [{
                    "filename": os.path.basename(video_url),
                    "type": "input",
                    "url": video_url
                }]
            }
        }
        
        # Load the video using OpenCV
        result = FSLoadVideo().load_video(temp_video_path, skip_first_frames, select_every_nth, prompt, extra_pnginfo)
        
        # Extract the image tensor from the result
        if isinstance(result, dict) and "result" in result:
            image_tensor = result["result"][0]
        else:
            image_tensor = result[0]
            
        return {"ui": preview, "result": (image_tensor,)}

class FSSaveVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "FlowScale"}),
                "fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 120.0, "step": 0.1}),
            },
            "optional": {
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "label": ("STRING", {"default": "Output Video"}),
            },
            "hidden": {
                "prompt": "PROMPT", 
                "extra_pnginfo": "EXTRA_PNGINFO"
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    
    FUNCTION = "save_video"
    
    CATEGORY = "FlowScale/Media/Video"
    OUTPUT_NODE = True
    
    def save_video(self, images, filename_prefix="FlowScale", fps=24.0, quality=95, label="Output Video", prompt=None, extra_pnginfo=None):
        logger.info(f"I/O Label: {label}")
        output_dir = folder_paths.get_output_directory()
        format = "mp4"  # Default format
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get proper filename with counter
        (
            full_output_folder,
            filename,
            _,
            subfolder,
            _,
        ) = folder_paths.get_save_image_path(filename_prefix, output_dir)
        
        # comfy counter workaround
        max_counter = 0
        # Loop through the existing files
        matcher = re.compile(f"{re.escape(filename)}_(\\d+)\\D*\\..+", re.IGNORECASE)
        for existing_file in os.listdir(full_output_folder):
            # Check if the file matches the expected format
            match = matcher.fullmatch(existing_file)
            if match:
                # Extract the numeric portion of the filename
                file_counter = int(match.group(1))
                # Update the maximum counter value if necessary
                if file_counter > max_counter:
                    max_counter = file_counter
        # Increment the counter by 1 to get the next available value
        counter = max_counter + 1
        
        # File name with counter
        save_filename = f"{filename}_{counter:05}.{format}"
        output_path = os.path.join(full_output_folder, save_filename)
        
        # Save first frame as PNG with metadata
        metadata = PngInfo()
        if extra_pnginfo is not None:
            for x in extra_pnginfo:
                metadata.add_text(x, json.dumps(extra_pnginfo[x]))
        metadata.add_text("CreationTime", datetime.datetime.now().isoformat(" ")[:19])
        
        # Save first frame as PNG
        first_image_file = f"{filename}_{counter:05}.png"
        first_image_path = os.path.join(full_output_folder, first_image_file)
        
        results = []
        output_files = []
        
        try:
            # Convert tensor to numpy and then to uint8
            uint8_frames = (images.cpu().numpy() * 255).astype(np.uint8)
            
            # Save first frame as PNG
            first_frame = uint8_frames[0]
            Image.fromarray(first_frame).save(
                first_image_path,
                pnginfo=metadata,
                compress_level=4,
            )
            output_files.append(first_image_path)
            
            # Get dimensions
            frame_count, height, width, channels = uint8_frames.shape
            
            # Try using FFmpeg first
            if self._has_ffmpeg():
                # Save frames to temporary directory
                temp_dir = tempfile.mkdtemp()
                try:
                    logger.info(f"Saving {frame_count} frames to temporary directory...")
                    for i, frame in enumerate(uint8_frames):
                        # Save each frame as PNG
                        frame_path = os.path.join(temp_dir, f"frame_{i:05d}.png")
                        # Convert RGB to BGR for OpenCV
                        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(frame_path, bgr_frame)
                    
                    # Use FFmpeg to encode video
                    logger.info("Using FFmpeg for video encoding...")
                    self._encode_with_ffmpeg(temp_dir, output_path, fps, format, quality)
                    
                finally:
                    # Clean up temporary directory
                    shutil.rmtree(temp_dir)
            else:
                # Fall back to OpenCV for encoding
                logger.info("Using OpenCV for video encoding...")
                
                # Choose codec based on format
                if format == "mp4":
                    # Try multiple codecs in order of preference
                    codecs = ['avc1', 'mp4v', 'divx', 'xvid']
                    working_codec = None
                    
                    for codec in codecs:
                        try:
                            fourcc = cv2.VideoWriter_fourcc(*codec)
                            test_path = os.path.join(output_dir, f"test_{codec}.{format}")
                            test_writer = cv2.VideoWriter(test_path, fourcc, fps, (width, height))
                            
                            if test_writer.isOpened():
                                test_writer.release()
                                working_codec = codec
                                os.remove(test_path)
                                break
                            else:
                                test_writer.release()
                                if os.path.exists(test_path):
                                    os.remove(test_path)
                                    
                        except Exception as e:
                            logger.info(f"Codec {codec} failed: {str(e)}")
                    
                    if working_codec is None:
                        # If no codec worked, try a very common codec
                        working_codec = 'XVID'
                        format = 'avi'  # Change format to match codec
                        output_path = os.path.join(output_dir, f"{os.path.splitext(save_filename)[0]}.{format}")
                        save_filename = f"{filename}_{counter:05}.{format}"
                    
                    fourcc = cv2.VideoWriter_fourcc(*working_codec)
                    logger.info(f"Using codec: {working_codec}")
                    
                elif format == "avi":
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                elif format == "mov":
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                elif format == "webm":
                    fourcc = cv2.VideoWriter_fourcc(*'VP90')
                else:
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    
                # Create video writer
                video_writer = cv2.VideoWriter(
                    output_path,
                    fourcc,
                    fps,
                    (width, height)
                )
                
                if not video_writer.isOpened():
                    raise ValueError("Could not open VideoWriter. Try using FFmpeg instead.")
                
                # Write frames
                for frame in uint8_frames:
                    # Convert RGB to BGR for OpenCV
                    bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    video_writer.write(bgr_frame)
                    
                video_writer.release()
            
            output_files.append(output_path)
            logger.info(f"Video saved to: {output_path}")
            
            # Create preview info for web player compatibility
            preview = {
                "ui": {
                    "gifs": [{
                        "filename": save_filename,
                        "subfolder": subfolder,
                        "type": "output",
                        "frame_rate": fps,
                        "total_frames": len(images),
                        "format": 'video/mp4' if format == 'mp4' else (
                            'video/webm' if format == 'webm' else 
                            'video/quicktime' if format == 'mov' else 
                            'video/x-msvideo'  # for avi
                        ),
                        "workflow": first_image_file,
                        "fullpath": output_path,
                    }]
                }
            }            
            return {"ui": preview, "result": (output_path,)}
            
        except Exception as e:
            logger.error(f"Error saving video: {e}")
            return {"ui": {"videos": []}, "result": ("",)}
    
    def _has_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _encode_with_ffmpeg(self, frame_dir, output_path, fps, format, quality):
        # Map quality (0-100) to CRF (0-51, lower is better)
        # Quality 95 -> CRF 15, Quality 0 -> CRF 51
        crf = max(0, min(51, int(51 - (quality / 100.0 * 36))))
        
        # Prepare FFmpeg command
        if format == "mp4":
            cmd = [
                'ffmpeg', '-y',  # Overwrite output
                '-framerate', str(fps),
                '-i', os.path.join(frame_dir, 'frame_%05d.png'),
                '-c:v', 'libx264',  # Use H.264 for web compatibility
                '-profile:v', 'baseline',  # More compatible profile
                '-level', '3.0',
                '-pix_fmt', 'yuv420p',  # Required for browser compatibility
                '-movflags', '+faststart',  # Web streaming optimization
                '-crf', str(crf)
            ]
        elif format == "webm":
            codec = "libvpx-vp9"
            cmd = [
                'ffmpeg', '-y',
                '-framerate', str(fps),
                '-i', os.path.join(frame_dir, 'frame_%05d.png'),
                '-c:v', codec,
                '-crf', '30',
                '-b:v', '0',
                '-pix_fmt', 'yuv420p'
            ]
        else:  # avi, mov, etc.
            codec = "mpeg4" if format == "avi" else "h264"
            cmd = [
                'ffmpeg', '-y',
                '-framerate', str(fps),
                '-i', os.path.join(frame_dir, 'frame_%05d.png'),
                '-c:v', codec,
                '-q:v', str(int(31 - (quality / 100.0 * 30)))  # Quality parameter
            ]
        
        # Output file
        cmd.append(output_path)
        
        logger.info(f"Running FFmpeg: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # Verify the output exists
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            logger.error("FFmpeg failed to create the video file")
            raise ValueError("FFmpeg failed to create the video file")