import os
import numpy as np
import cv2
import folder_paths
import tempfile
from PIL import Image
import re

class FSLoadVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "video_path": ("STRING", {"default": ""}),
            },
            "optional": {
                "start_frame": ("INT", {"default": 0, "min": 0, "step": 1}),
                "frame_count": ("INT", {"default": 0, "min": 0, "step": 1}),
                "skip_frames": ("INT", {"default": 0, "min": 0, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "INT", "INT", "INT")
    RETURN_NAMES = ("frames", "frame_count", "width", "height")

    FUNCTION = "load_video"

    CATEGORY = "IO"

    def load_video(self, video_path, start_frame=0, frame_count=0, skip_frames=0):
        try:
            # If path is absolute, use it directly
            if os.path.isabs(video_path):
                path = video_path
            else:
                # Otherwise, check in the input directory
                input_dir = folder_paths.get_input_directory()
                path = os.path.join(input_dir, video_path)
                
                # If not found in input directory, try absolute from cwd
                if not os.path.exists(path):
                    path = os.path.join(os.getcwd(), video_path)
                    
                # If still not found, check output directory
                if not os.path.exists(path):
                    output_dir = folder_paths.get_output_directory()
                    path = os.path.join(output_dir, video_path)
            
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
            
            # Validate frame parameters
            start_frame = max(0, min(start_frame, total_frames - 1))
            
            # If frame_count is 0 or exceeds available frames, use all remaining frames
            if frame_count <= 0 or (start_frame + frame_count) > total_frames:
                frame_count = total_frames - start_frame
                
            # Calculate number of frames to load with skip
            step = skip_frames + 1  # +1 because we want to include the current frame
            adjusted_frame_count = (frame_count + step - 1) // step
            
            # Seek to start frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            # Load the frames
            frames = []
            current_frame = start_frame
            loaded_count = 0
            
            while loaded_count < adjusted_frame_count and current_frame < total_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Convert from BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Normalize to [0,1] range for ComfyUI
                frame_norm = frame_rgb.astype(np.float32) / 255.0
                
                frames.append(frame_norm)
                loaded_count += 1
                
                # Skip frames if needed
                if skip_frames > 0:
                    current_frame += skip_frames
                    cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                
                current_frame += 1
            
            # Release the video object
            cap.release()
            
            if not frames:
                raise ValueError("No frames were loaded from the video")
            
            # Stack frames into a batch
            frame_batch = np.stack(frames)
            
            return (frame_batch, loaded_count, width, height)
            
        except Exception as e:
            print(f"Error loading video: {e}")
            # Return a small red placeholder image on error 
            error_img = np.ones((1, 64, 64, 3), dtype=np.float32)
            error_img[..., 1:] = 0  # Set green and blue channels to 0 (making it red)
            return (error_img, 0, 64, 64)


class FSSaveVideo:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename": ("STRING", {"default": "output_video"}),
                "fps": ("FLOAT", {"default": 24.0, "min": 1.0, "max": 120.0, "step": 0.1}),
            },
            "optional": {
                "format": (["mp4", "avi", "mov", "webm"], {"default": "mp4"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "audio_path": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("video_path",)
    
    FUNCTION = "save_video"
    
    CATEGORY = "IO"
    OUTPUT_NODE = True
    
    def save_video(self, images, filename, fps=24.0, format="mp4", quality=95, audio_path=""):
        output_dir = folder_paths.get_output_directory()
        
        # Ensure filename has extension
        if not re.search(r'\.\w+$', filename):
            filename = f"{filename}.{format}"
        elif not filename.endswith(f".{format}"):
            # Replace extension if it doesn't match selected format
            filename = re.sub(r'\.\w+$', f".{format}", filename)
            
        output_path = os.path.join(output_dir, filename)
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Convert images from [0,1] to [0,255] range
            uint8_frames = (images * 255).astype(np.uint8)
            
            # Get dimensions
            frame_count, height, width, channels = uint8_frames.shape
            
            # Choose codec based on format
            if format == "mp4":
                fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
            elif format == "avi":
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
            elif format == "mov":
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            elif format == "webm":
                fourcc = cv2.VideoWriter_fourcc(*'VP90')
            else:
                fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Default to H.264
                
            # Map quality (1-100) to bitrate
            # Higher quality = higher bitrate
            # Rough approximation: HD content at quality 95 ~= 8000 kbps
            base_bitrate = 8000000  # 8 Mbps for quality 95
            bitrate = int((quality / 95) * base_bitrate)
                
            # Create video writer
            video_writer = cv2.VideoWriter(
                output_path,
                fourcc,
                fps,
                (width, height)
            )
            
            # Set bitrate if possible (not all codecs support this)
            try:
                video_writer.set(cv2.VIDEOWRITER_PROP_QUALITY, quality)
            except:
                pass
                
            for frame in uint8_frames:
                # Convert RGB to BGR for OpenCV
                bgr_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                video_writer.write(bgr_frame)
                
            video_writer.release()
            
            # Add audio if provided
            if audio_path and os.path.exists(audio_path):
                try:
                    import subprocess
                    import shlex
                    
                    # Create a temporary file for the output with audio
                    with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
                        temp_path = temp_file.name
                        
                    # Use ffmpeg to add audio
                    cmd = f"ffmpeg -i {shlex.quote(output_path)} -i {shlex.quote(audio_path)} -c:v copy -c:a aac -shortest {shlex.quote(temp_path)}"
                    subprocess.run(cmd, shell=True, check=True)
                    
                    # Replace the original file with the one with audio
                    os.replace(temp_path, output_path)
                    print(f"Added audio from {audio_path} to video")
                    
                except Exception as e:
                    print(f"Error adding audio to video: {e}")
            
            print(f"Video saved to: {output_path}")
            return (output_path,)
            
        except Exception as e:
            print(f"Error saving video: {e}")
            return ("",)