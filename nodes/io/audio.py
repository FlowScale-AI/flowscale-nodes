import os
import random
import string
import numpy as np
import torch
import soundfile as sf
import folder_paths
import requests
import tempfile

AUDIO_EXTENSIONS = ['.wav', '.mp3', '.ogg', '.flac', '.m4a', '.aac']

class FSLoadAudio:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f)) and 
                os.path.splitext(f)[1].lower() in AUDIO_EXTENSIONS]
        return {
            "required": {
                "audio": (sorted(files), {"audio_upload": True}),
            },
            "optional": {
                "label": ("STRING", {"default": "Input Audio"}),
                "audio_url": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "load_audio"
    CATEGORY = "FlowScale/IO"

    def load_audio(self, audio, audio_url="", label="Input Audio"):
        try:
            # If audio_url is provided, load from URL
            if audio_url:
                try:
                    response = requests.get(audio_url)
                    response.raise_for_status()
                    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(audio_url)[1]) as temp_file:
                        temp_file.write(response.content)
                        temp_file.flush()
                        data, samplerate = sf.read(temp_file.name)
                        path = f"URL: {audio_url}"
                except Exception as e:
                    print(f"Error loading audio from URL: {e}")
                    raise
            else:
                # If path is absolute, use it directly
                if os.path.isabs(audio):
                    path = audio
                else:
                    # Otherwise, check in the input directory
                    input_dir = folder_paths.get_input_directory()
                    path = os.path.join(input_dir, audio)
                    
                    # If not found in input directory, try absolute from cwd
                    if not os.path.exists(path):
                        path = os.path.join(os.getcwd(), audio)
                
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Audio file not found at path: {path}")
                    
                # Load the audio with soundfile
                data, samplerate = sf.read(path)

            # Convert to tensor
            if len(data.shape) == 1:
                # Mono audio, add channel dimension
                data = data[:, np.newaxis]
            elif len(data.shape) > 2:
                raise ValueError("Audio has more than 2 channels")

            # Convert to float32 tensor
            audio_tensor = torch.from_numpy(data.astype(np.float32))
            
            # Create preview info
            preview = {
                "ui": {
                    "audio": [{
                        "filename": os.path.basename(path),
                        "type": "input",
                        "samplerate": samplerate,
                        "channels": data.shape[1],
                        "format": os.path.splitext(path)[1][1:],
                        "url": f"file={path}"
                    }]
                }
            }
            
            print(f"I/O Label: {label}")
            return {"ui": preview, "result": (audio_tensor,)}

        except Exception as e:
            print(f"Error loading audio: {e}")
            # Return an empty tensor on error
            return {"ui": {"error": str(e)}, "result": (torch.zeros((1, 1), dtype=torch.float32),)}


class FSSaveAudio:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "filename_prefix": ("STRING", {"default": "FlowScale_"}),
                "format": (["wav", "mp3", "ogg", "flac"], {"default": "wav"}),
                "samplerate": ("INT", {"default": 44100, "min": 8000, "max": 192000})
            },
            "optional": {
                "label": ("STRING", {"default": "Output Audio"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    FUNCTION = "save_audio"
    CATEGORY = "FlowScale/IO"
    OUTPUT_NODE = True
    
    def save_audio(self, audio, filename_prefix, format="wav", samplerate=44100, quality=95, label="Output Audio"):
        output_dir = folder_paths.get_output_directory()
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate random filename
        random_segment = ''.join(random.choices(string.digits, k=6))
        filename = f"{filename_prefix}_{random_segment}.{format}"
        filepath = os.path.join(output_dir, filename)
        
        try:
            # Convert torch tensor to numpy array
            if isinstance(audio, torch.Tensor):
                audio_data = audio.cpu().numpy()
            else:
                audio_data = audio

            # Save based on format with appropriate options
            if format == "mp3":
                import soundfile as sf
                import subprocess
                
                # First save as WAV
                temp_wav = os.path.join(output_dir, f"temp_{random_segment}.wav")
                sf.write(temp_wav, audio_data, samplerate)
                
                # Convert to MP3 using ffmpeg
                try:
                    subprocess.run([
                        'ffmpeg', '-y',
                        '-i', temp_wav,
                        '-codec:a', 'libmp3lame',
                        '-qscale:a', str(int(10 - (quality / 10))),  # Convert quality to ffmpeg scale (0-9)
                        filepath
                    ], check=True)
                finally:
                    if os.path.exists(temp_wav):
                        os.remove(temp_wav)
            else:
                # For WAV, OGG, and FLAC
                sf.write(filepath, audio_data, samplerate, format=format)
            
            # Create preview info
            preview = {
                "ui": {
                    "audio": [{
                        "filename": filename,
                        "type": "output",
                        "samplerate": samplerate,
                        "channels": audio_data.shape[1] if len(audio_data.shape) > 1 else 1,
                        "format": format,
                        "url": f"file={filepath}"
                    }]
                }
            }
            
            print(f"I/O Label: {label}")
            return {"ui": preview, "result": (filepath,)}
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            return {"ui": {"error": str(e)}, "result": ("",)}