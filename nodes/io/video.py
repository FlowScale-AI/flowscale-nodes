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

class FSLoadVideo:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and 
                any(f.lower().endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.webm', '.mkv'])]
        
        return {
            "required": {},
            "optional": {
                "video": (sorted(files), {"video_upload": True}),
                "video_url": ("STRING", {"default": ""}),
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
    
    def load_video(self, video="", video_url="", start_frame=0, max_frames=64, skip_frames=0, 
                   resize_to_width=512, resize_to_height=0, batch_size=4, auto_resize_high_res=True):
        try:
            temp_file = None
            
            # Check that at least one source is provided
            if not video and not video_url:
                raise ValueError("Either video or video_url must be provided")
            
            # If URL is provided, download the video to a temporary file
            if video_url:
                try:
                    print(f"Downloading video from URL: {video_url}")
                    response = requests.get(video_url, stream=True)
                    response.raise_for_status()
                    
                    # Create a temporary file with appropriate extension
                    suffix = ".mp4"  # Default extension
                    content_type = response.headers.get('Content-Type', '')
                    if 'webm' in content_type:
                        suffix = ".webm"
                    elif 'quicktime' in content_type:
                        suffix = ".mov"
                    elif 'x-msvideo' in content_type:
                        suffix = ".avi"
                    
                    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
                    for chunk in response.iter_content(chunk_size=8192): 
                        if chunk:
                            temp_file.write(chunk)
                    temp_file.flush()
                    temp_file.close()
                    
                    path = temp_file.name
                    print(f"Video downloaded to temporary file: {path}")
                except Exception as e:
                    if temp_file and os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
                    print(f"Error downloading video from URL: {e}")
                    raise
            else:
                # If path is absolute, use it directly
                if os.path.isabs(video):
                    path = video
                else:
                    # Otherwise, check in the input directory
                    input_dir = folder_paths.get_input_directory()
                    path = os.path.join(input_dir, video)
                    
                    # If not found in input directory, try absolute from cwd
                    if not os.path.exists(path):
                        path = os.path.join(os.getcwd(), video)
                        
                    # If still not found, check output directory
                    if not os.path.exists(path):
                        output_dir = folder_paths.get_output_directory()
                        path = os.path.join(output_dir, video)
            
            if not os.path.exists(path):
                raise FileNotFoundError(f"Video not found at path: {path}")
            
            # Open the video file
            cap = cv2.VideoCapture(path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {path}")
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"Video loaded: {path}")
            print(f"Total frames: {total_frames}, FPS: {fps}, Resolution: {width}x{height}")
            
            # Calculate resized dimensions
            should_resize = False
            target_width, target_height = width, height
            
            # Auto-resize high-resolution videos if option is enabled
            if auto_resize_high_res and (width > 1280 or height > 720):
                # Only auto-resize if user hasn't set specific dimensions
                if resize_to_width == 0 and resize_to_height == 0:
                    # Calculate aspect ratio and resize to fit within HD bounds
                    aspect_ratio = width / height
                    if width > height:
                        target_width = min(width, 1280)
                        target_height = int(target_width / aspect_ratio)
                    else:
                        target_height = min(height, 720)
                        target_width = int(target_height * aspect_ratio)
                    
                    should_resize = True
                    print(f"Auto-resizing high-resolution video to {target_width}x{target_height}")
            
            # If user specified dimensions, use those instead
            if resize_to_width > 0 and resize_to_height > 0:
                target_width, target_height = resize_to_width, resize_to_height
                should_resize = True
            elif resize_to_width > 0:
                target_width = resize_to_width
                target_height = int(height * (resize_to_width / width))
                should_resize = True
            elif resize_to_height > 0:
                target_height = resize_to_height
                target_width = int(width * (resize_to_height / height))
                should_resize = True
                
            if should_resize:
                print(f"Resizing video from {width}x{height} to {target_width}x{target_height}")
                
            # Adjust start frame
            start_frame = max(0, min(start_frame, total_frames - 1))
            
            # Calculate memory requirements for a single frame
            bytes_per_frame = target_width * target_height * 3 * 4  # width * height * channels * sizeof(float32)
            
            # Calculate available memory with safety margin (leave 40% free for processing)
            available_memory = int(psutil.virtual_memory().available * 0.6)
            
            # Calculate maximum number of frames that can fit in memory
            memory_limited_frames = max(1, available_memory // bytes_per_frame)
            
            # Adjust frame count based on memory limits and user settings
            if max_frames <= 0 or max_frames > memory_limited_frames:
                frame_count = memory_limited_frames
                print(f"Memory limit: Can safely load {memory_limited_frames} frames at {target_width}x{target_height}")
            else:
                frame_count = max_frames
            
            # Calculate number of frames to load with skip
            step = skip_frames + 1  # +1 because we want to include the current frame
            adjusted_frame_count = min((frame_count + step - 1) // step, total_frames - start_frame)
            
            # Determine batch size based on available memory
            max_batch_size = max(1, min(batch_size, memory_limited_frames // 4))  # 1/4 of what would fit in memory
            if max_batch_size < batch_size:
                print(f"Reducing batch size from {batch_size} to {max_batch_size} due to memory constraints")
                batch_size = max_batch_size
            
            # Process frames in batches
            all_frames = []
            current_frame = start_frame
            loaded_count = 0
            
            print(f"Processing {adjusted_frame_count} frames in batches of {batch_size}")
            
            while loaded_count < adjusted_frame_count:
                # Calculate batch end
                batch_end = min(loaded_count + batch_size, adjusted_frame_count)
                batch_size_current = batch_end - loaded_count
                
                # Load batch
                batch_frames = []
                
                # Seek to correct position
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                
                for i in range(batch_size_current):
                    ret, frame = cap.read()
                    if not ret:
                        break
                        
                    # Convert from BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Resize if needed
                    if should_resize:
                        frame_rgb = cv2.resize(frame_rgb, (target_width, target_height), 
                                              interpolation=cv2.INTER_AREA)  # Better for downsampling
                    
                    # Normalize to [0,1] range for ComfyUI
                    frame_norm = frame_rgb.astype(np.float32) / 255.0
                    
                    batch_frames.append(frame_norm)
                    loaded_count += 1
                    
                    # Skip frames if needed
                    if skip_frames > 0:
                        current_frame += skip_frames + 1
                    else:
                        current_frame += 1
                
                if batch_frames:
                    # Stack batch frames
                    batch_stack = np.stack(batch_frames)
                    all_frames.append(batch_stack)
                    
                    # Free memory explicitly
                    batch_frames = None
                    
                    # Force garbage collection
                    gc.collect()
                    
                    print(f"Loaded {loaded_count}/{adjusted_frame_count} frames")
                else:
                    break
            
            # Release the video object
            cap.release()
            
            # Clean up temporary file if we created one
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
                
            if not all_frames:
                raise ValueError("No frames were loaded from the video")
            
            # Combine all batches
            try:
                frame_batch = np.concatenate(all_frames, axis=0)
                
                # Free memory of individual batches
                all_frames = None
                gc.collect()
                
                print(f"Successfully loaded {frame_batch.shape[0]} frames with shape {frame_batch.shape[1:]}")
                
                return (frame_batch, frame_batch.shape[0], target_width, target_height)
            except Exception as e:
                print(f"Error concatenating frames: {e}. Returning the first batch.")
                # Return just the first batch if concatenation fails
                if all_frames:
                    return (all_frames[0], all_frames[0].shape[0], target_width, target_height)
                raise
            
        except Exception as e:
            # Clean up temporary file if an error occurred
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
                
            print(f"Error loading video: {e}")
            # Return a small red placeholder image on error 
            error_img = np.ones((1, 64, 64, 3), dtype=np.float32)
            error_img[..., 1:] = 0  # Set green and blue channels to 0 (making it red)
            return (error_img, 0, 64, 64)

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