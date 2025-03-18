import os
import random
import string
import numpy as np
import cv2
import folder_paths
import tempfile
from PIL import Image
import re
import requests
from io import BytesIO
import psutil
import time
import gc
import shutil
import subprocess
import shlex
import torch

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
                    "frame_count": ("INT", {"default": 16, "min": 1, "max": 1000}),
                    "skip_first_frames": ("INT", {"default": 0, "min": 0, "max": 10000}),
                    "select_every_nth": ("INT", {"default": 1, "min": 1, "max": 100}),
               },
               "hidden": {
                   "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
               }}

    CATEGORY = "FlowScale/IO"

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("IMAGES",)
    FUNCTION = "load_video"

    def load_video(self, video, frame_count=16, skip_first_frames=0, select_every_nth=1, prompt=None, extra_pnginfo=None):
        video_path = folder_paths.get_annotated_filepath(video)
        
        # Open the video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
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
        while len(frames) < frame_count and frame_idx < total_frames:
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
            
            if len(frames) >= frame_count:
                break
        
        cap.release()
        
        # Check if we got any frames
        if len(frames) == 0:
            raise ValueError("No frames could be extracted from the video")
            
        # Convert to tensor
        batch = torch.from_numpy(np.stack(frames))
        
        return (batch,)
        
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

class FSLoadVideoPath:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "start_frame": ("INT", {"default": 0, "min": 0, "step": 1}),
                "max_frames": ("INT", {"default": 64, "min": 1, "max": 1000, "step": 1}),
                "skip_frames": ("INT", {"default": 0, "min": 0, "step": 1}),
                "resize_to_width": ("INT", {"default": 512, "min": 0, "max": 4096, "step": 8}),
                "resize_to_height": ("INT", {"default": 0, "min": 0, "max": 2160, "step": 8}),
                "batch_size": ("INT", {"default": 4, "min": 1, "max": 16, "step": 1}),
                "auto_resize_high_res": ("BOOLEAN", {"default": True}),
            }
        }
    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT")
    RETURN_NAMES = ("frames", "frame_count", "width", "height")
    FUNCTION = "load_video"
    CATEGORY = "IO"
    def load_video(self, video_path, start_frame=0, max_frames=64, skip_frames=0, 
                   resize_to_width=512, resize_to_height=0, batch_size=4, auto_resize_high_res=True):
        # Check if the path is a URL
        if video_path.startswith(('http://', 'https://')):
            # Create FSLoadVideo instance and call with URL
            loader = FSLoadVideo()
            return loader.load_video(
                video_url=video_path,
                start_frame=start_frame,
                max_frames=max_frames,
                skip_frames=skip_frames,
                resize_to_width=resize_to_width,
                resize_to_height=resize_to_height,
                batch_size=batch_size,
                auto_resize_high_res=auto_resize_high_res
            )
        else:
            # Otherwise treat as a local path
            loader = FSLoadVideo()
            return loader.load_video(
                video=video_path,
                start_frame=start_frame,
                max_frames=max_frames, 
                skip_frames=skip_frames,
                resize_to_width=resize_to_width,
                resize_to_height=resize_to_height,
                batch_size=batch_size,
                auto_resize_high_res=auto_resize_high_res
            )

class FSSaveVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "FlowScale_"}),
                "fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 120.0, "step": 0.1}),
            },
            "optional": {
                "format": (["mp4", "avi", "mov", "webm"], {"default": "mp4"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "audio_path": ("STRING", {"default": ""}),
                "use_ffmpeg": ("BOOLEAN", {"default": True}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    
    FUNCTION = "save_video"
    
    CATEGORY = "IO"
    OUTPUT_NODE = True
    
    def save_video(self, images, filename_prefix="FlowScale_", fps=24.0, format="mp4", quality=95, audio_path="", use_ffmpeg=True):
        output_dir = folder_paths.get_output_directory()
        
        random_segment = ''.join(random.choices(string.digits, k=6))
        filename = f"{filename_prefix}_{random_segment}.{format}"        
            
        output_path = os.path.join(output_dir, filename)
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Convert images from [0,1] to [0,255] range
            uint8_frames = (images * 255).astype(np.uint8)
            
            # Get dimensions
            frame_count, height, width, channels = uint8_frames.shape
            
            if use_ffmpeg and self._has_ffmpeg():
                # Save frames to temporary directory
                temp_dir = tempfile.mkdtemp()
                try:
                    print(f"Saving {frame_count} frames to temporary directory...")
                    for i, frame in enumerate(uint8_frames):
                        # Save each frame as PNG
                        frame_path = os.path.join(temp_dir, f"frame_{i:05d}.png")
                        # Convert RGB to BGR for OpenCV
                        bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(frame_path, bgr_frame)
                    
                    # Use FFmpeg to encode video
                    self._encode_with_ffmpeg(temp_dir, output_path, fps, format, quality, audio_path)
                    
                finally:
                    # Clean up temporary directory
                    shutil.rmtree(temp_dir)
            else:
                # Fall back to OpenCV for encoding
                print("Using OpenCV for video encoding...")
                
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
                            print(f"Codec {codec} failed: {str(e)}")
                    
                    if working_codec is None:
                        # If no codec worked, try a very common codec
                        working_codec = 'XVID'
                        format = 'avi'  # Change format to match codec
                        output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.{format}")
                    
                    fourcc = cv2.VideoWriter_fourcc(*working_codec)
                    print(f"Using codec: {working_codec}")
                    
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
                
                # Add audio if provided
                if audio_path and os.path.exists(audio_path):
                    if self._has_ffmpeg():
                        self._add_audio_with_ffmpeg(output_path, audio_path, format)
                    else:
                        print("FFmpeg not found, cannot add audio to video")
            
            print(f"Video saved to: {output_path}")
            return (output_path,)
            
        except Exception as e:
            print(f"Error saving video: {e}")
            return ("",)
    
    def _has_ffmpeg(self):
        try:
            subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _encode_with_ffmpeg(self, frame_dir, output_path, fps, format, quality, audio_path=None):
        # Map quality (0-100) to CRF (0-51, lower is better)
        # Quality 95 -> CRF 15, Quality 0 -> CRF 51
        crf = max(0, min(51, int(51 - (quality / 100.0 * 36))))
        
        # Prepare FFmpeg command
        if format == "mp4":
            codec = "libx264"
            cmd = [
                'ffmpeg', '-y',  # Overwrite output
                '-framerate', str(fps),
                '-i', os.path.join(frame_dir, 'frame_%05d.png'),
                '-c:v', codec,
                '-preset', 'medium',  # Speed/compression trade-off
                '-crf', str(crf),     # Quality
                '-pix_fmt', 'yuv420p' # Widely compatible pixel format
            ]
        elif format == "webm":
            codec = "libvpx-vp9"
            cmd = [
                'ffmpeg', '-y',
                '-framerate', str(fps),
                '-i', os.path.join(frame_dir, 'frame_%05d.png'),
                '-c:v', codec,
                '-b:v', f"{int(quality / 100.0 * 5000)}k"  # Bitrate
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
        
        # Add audio if provided
        if audio_path and os.path.exists(audio_path):
            cmd.extend(['-i', audio_path, '-c:a', 'aac', '-shortest'])
        
        # Output file
        cmd.append(output_path)
        
        print(f"Running FFmpeg: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # Verify the output exists
        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise ValueError("FFmpeg failed to create the video file")
    
    def _add_audio_with_ffmpeg(self, video_path, audio_path, format):
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
            temp_path = temp_file.name
            
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-shortest',
            temp_path
        ]
        
        print(f"Adding audio with FFmpeg: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # Replace the original file with the one with audio
        os.replace(temp_path, video_path)
        print(f"Added audio from {audio_path} to video")