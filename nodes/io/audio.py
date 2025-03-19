import os
import random
import string
import numpy as np
import torch
import torchaudio
import folder_paths
import requests
import tempfile
import hashlib
import io
import json
from io import BytesIO

AUDIO_EXTENSIONS = ['.wav', '.mp3', '.ogg', '.flac', '.m4a', '.aac']

class FSLoadAudio:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = folder_paths.filter_files_content_types(os.listdir(input_dir), ["audio"])
        return {
            "required": {
                "audio": (sorted(files), ),
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
            if (audio_url):
                try:
                    response = requests.get(audio_url)
                    response.raise_for_status()
                    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(audio_url)[1], delete=False) as temp_file:
                        temp_file.write(response.content)
                        temp_file_path = temp_file.name
                        
                    # Use torchaudio to load audio
                    waveform, sample_rate = torchaudio.load(temp_file_path)
                    os.unlink(temp_file_path)  # Delete the temporary file
                except Exception as e:
                    print(f"Error loading audio from URL: {e}")
                    raise
            else:
                # Get annotated filepath
                audio_path = folder_paths.get_annotated_filepath(audio)
                
                if not os.path.exists(audio_path):
                    raise FileNotFoundError(f"Audio file not found at path: {audio_path}")
                    
                # Use torchaudio to load audio
                waveform, sample_rate = torchaudio.load(audio_path)

            # Create audio dictionary in the expected format
            audio_data = {"waveform": waveform.unsqueeze(0), "sample_rate": sample_rate}
            
            # Create preview information for the UI
            preview = {
                "ui": {
                    "audio": [{
                        "filename": os.path.basename(audio_path if not audio_url else audio_url),
                        "type": "input",
                        "sample_rate": sample_rate,
                        "channels": waveform.shape[0],
                        "duration": waveform.shape[1] / sample_rate,
                        "url": f"file={audio_path}" if not audio_url else audio_url
                    }]
                }
            }
            
            print(f"I/O Label: {label}")
            return {"ui": preview, "result": (audio_data,)}

        except Exception as e:
            print(f"Error loading audio: {e}")
            # Return empty audio dict on error
            empty_waveform = torch.zeros((1, 1), dtype=torch.float32)
            empty_audio = {"waveform": empty_waveform.unsqueeze(0), "sample_rate": 44100}
            return {"result": (empty_audio,)}

    @classmethod
    def IS_CHANGED(s, audio, **kwargs):
        audio_path = folder_paths.get_annotated_filepath(audio)
        m = hashlib.sha256()
        with open(audio_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()
    
    @classmethod
    def VALIDATE_INPUTS(s, audio, **kwargs):
        if not folder_paths.exists_annotated_filepath(audio):
            return "Invalid audio file: {}".format(audio)
        return True

def insert_or_replace_vorbis_comment(file_buff, metadata_dict):
    """
    Insert or replace Vorbis comments in a FLAC file buffer with metadata
    """
    from mutagen.flac import FLAC
    
    # Create a temporary file to handle the data
    with tempfile.NamedTemporaryFile(suffix='.flac', delete=False) as temp_file:
        temp_file.write(file_buff.getbuffer() if isinstance(file_buff, io.BytesIO) else file_buff)
        temp_path = temp_file.name
    
    try:
        # Open the FLAC file with mutagen
        audio = FLAC(temp_path)
        
        # Add or update metadata as Vorbis comments
        for key, value in metadata_dict.items():
            audio[key] = value
            
        # Save the changes
        audio.save()
        
        # Read the modified file back into a buffer
        with open(temp_path, 'rb') as f:
            if isinstance(file_buff, io.BytesIO):
                new_buff = io.BytesIO(f.read())
            else:
                new_buff = f.read()
                
        return new_buff
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)

class FSSaveAudio:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "filename_prefix": ("STRING", {"default": "audio/FlowScale"})
            },
            "optional": {
                "format": (["flac", "wav", "mp3", "ogg"], {"default": "flac"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1}),
                "label": ("STRING", {"default": "Output Audio"}),
            },
            "hidden": {
                "prompt": "PROMPT", 
                "extra_pnginfo": "EXTRA_PNGINFO"
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "save_audio"
    CATEGORY = "FlowScale/IO"
    OUTPUT_NODE = True
    
    def save_audio(self, audio, filename_prefix, format="flac", quality=95, label="Output Audio", prompt=None, extra_pnginfo=None):
        # Apply any prefix append (for extension compatibility)
        filename_prefix += self.prefix_append
        
        # Get full path using the same helper as images
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir)
        
        # Ensure the output directory exists
        os.makedirs(full_output_folder, exist_ok=True)
        
        # Prepare results list
        results = []
        
        # Prepare metadata for audio files
        metadata = {}
        try:
            # Check if we're allowed to save metadata
            import sys
            args = sys.argv
            disable_metadata = '--disable-metadata' in args
            
            if not disable_metadata:
                if prompt is not None:
                    metadata["prompt"] = json.dumps(prompt)
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata[x] = json.dumps(extra_pnginfo[x])
        except:
            # If anything fails, continue without metadata
            pass
        
        # Loop through all waveforms in the batch
        for (batch_number, waveform) in enumerate(audio["waveform"].cpu()):
            # Replace batch number placeholder in filename
            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.{format}"
            filepath = os.path.join(full_output_folder, file)
            
            try:
                if format == "flac":
                    # For FLAC, save to a buffer first to add metadata
                    buff = io.BytesIO()
                    torchaudio.save(buff, waveform, audio["sample_rate"], format="FLAC")
                    
                    # Add metadata as Vorbis comments if we have any
                    if metadata:
                        try:
                            buff = insert_or_replace_vorbis_comment(buff, metadata)
                        except Exception as e:
                            print(f"Warning: Failed to add metadata to FLAC file: {e}")
                    
                    # Write the buffer to file
                    with open(filepath, 'wb') as f:
                        if isinstance(buff, io.BytesIO):
                            f.write(buff.getbuffer())
                        else:
                            f.write(buff)
                            
                elif format == "mp3":
                    # For mp3 format, use torchaudio with quality setting
                    compression = max(0, min(9, int(9 - (quality / 100.0 * 9))))  # Convert quality to compression level
                    
                    # Save directly or use fallback method
                    try:
                        torchaudio.save(
                            filepath, 
                            waveform, 
                            audio["sample_rate"], 
                            format="mp3",
                            compression=compression
                        )
                    except Exception as e:
                        # Fallback to ffmpeg via temporary file
                        temp_wav = os.path.join(full_output_folder, f"temp_{random.randint(1000, 9999)}.wav")
                        torchaudio.save(temp_wav, waveform, audio["sample_rate"])
                        
                        try:
                            import subprocess
                            subprocess.run([
                                'ffmpeg', '-y',
                                '-i', temp_wav,
                                '-codec:a', 'libmp3lame',
                                '-qscale:a', str(int(9 - (quality / 10))),  # Convert quality to ffmpeg scale (0-9)
                                filepath
                            ], check=True)
                        finally:
                            if os.path.exists(temp_wav):
                                os.remove(temp_wav)
                
                else:
                    # For WAV and OGG formats
                    torchaudio.save(filepath, waveform, audio["sample_rate"], format=format.upper())
                
                # Add to results
                results.append({
                    "filename": file,
                    "subfolder": subfolder,
                    "type": self.type,
                    "sample_rate": audio["sample_rate"],
                    "channels": waveform.shape[0],
                    "format": format,
                })
                
            except Exception as e:
                print(f"Error saving audio file {file}: {e}")
                continue
                
            counter += 1
                
        # Create preview info for UI
        preview = {
            "audio": results
        }
        
        print(f"I/O Label: {label}")
        return {"ui": preview}

class FSProcessAudio:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio": ("AUDIO",),
                "operation": (["normalize", "fade_in", "fade_out", "trim", "resample", "mono", "stereo", "speed"], {"default": "normalize"}),
            },
            "optional": {
                "fade_time": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 30.0, "step": 0.1}),
                "trim_start": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3600.0, "step": 0.1}),
                "trim_end": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 3600.0, "step": 0.1}),
                "target_sr": ("INT", {"default": 44100, "min": 8000, "max": 192000}),
                "speed_factor": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 4.0, "step": 0.1}),
                "label": ("STRING", {"default": "Processed Audio"}),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "process_audio"
    CATEGORY = "FlowScale/Utilities"

    def process_audio(self, audio, operation, fade_time=1.0, trim_start=0.0, trim_end=0.0, 
                     target_sr=44100, speed_factor=1.0, label="Processed Audio"):
        try:
            # Extract audio data
            waveform = audio["waveform"]
            sample_rate = audio["sample_rate"]
            
            # Original shape before any processing
            orig_shape = waveform.shape
            
            # Remove batch dimension for processing if present
            if len(waveform.shape) > 2:
                waveform = waveform.squeeze(0)
            
            # Apply selected operation
            if operation == "normalize":
                # Normalize audio to peak at 0 dB
                max_val = torch.max(torch.abs(waveform))
                if max_val > 0:
                    waveform = waveform / max_val
                    
            elif operation == "fade_in":
                # Apply fade in effect (linear fade)
                fade_samples = int(fade_time * sample_rate)
                if fade_samples > 0:
                    if fade_samples > waveform.shape[1]:
                        fade_samples = waveform.shape[1]
                    fade = torch.linspace(0, 1, fade_samples)
                    waveform[:, :fade_samples] *= fade
                    
            elif operation == "fade_out":
                # Apply fade out effect (linear fade)
                fade_samples = int(fade_time * sample_rate)
                if fade_samples > 0:
                    if fade_samples > waveform.shape[1]:
                        fade_samples = waveform.shape[1]
                    fade = torch.linspace(1, 0, fade_samples)
                    waveform[:, -fade_samples:] *= fade
                    
            elif operation == "trim":
                # Trim audio to specified time range
                start_sample = int(trim_start * sample_rate)
                end_sample = int(trim_end * sample_rate) if trim_end > 0 else waveform.shape[1]
                
                if start_sample >= waveform.shape[1]:
                    start_sample = 0
                if end_sample <= start_sample or end_sample > waveform.shape[1]:
                    end_sample = waveform.shape[1]
                    
                waveform = waveform[:, start_sample:end_sample]
                
            elif operation == "resample":
                # Resample audio to target sample rate
                if target_sr != sample_rate:
                    resampler = torchaudio.transforms.Resample(sample_rate, target_sr)
                    waveform = resampler(waveform)
                    sample_rate = target_sr
                    
            elif operation == "mono":
                # Convert stereo to mono
                if waveform.shape[0] > 1:
                    waveform = torch.mean(waveform, dim=0, keepdim=True)
                    
            elif operation == "stereo":
                # Convert mono to stereo if needed
                if waveform.shape[0] == 1:
                    waveform = waveform.repeat(2, 1)
                    
            elif operation == "speed":
                # Change playback speed without changing pitch
                if speed_factor != 1.0:
                    effects = [
                        ["speed", str(speed_factor)],
                        ["rate", str(sample_rate)]
                    ]
                    waveform, sample_rate = torchaudio.sox_effects.apply_effects_tensor(
                        waveform, sample_rate, effects)
            
            # Restore batch dimension if it was present
            if len(orig_shape) > 2:
                waveform = waveform.unsqueeze(0)
                
            # Create processed audio dict
            processed_audio = {
                "waveform": waveform,
                "sample_rate": sample_rate
            }
            
            print(f"I/O Label: {label}")
            return (processed_audio,)
            
        except Exception as e:
            print(f"Error processing audio: {e}")
            # Return original audio on error
            return (audio,)

class FSCombineAudio:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "audio1": ("AUDIO",),
                "audio2": ("AUDIO",),
                "operation": (["overlay", "concat", "mix"], {"default": "overlay"}),
                "volume1": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
                "volume2": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.1}),
            },
            "optional": {
                "label": ("STRING", {"default": "Combined Audio"}),
            }
        }

    RETURN_TYPES = ("AUDIO",)
    RETURN_NAMES = ("audio",)
    FUNCTION = "combine_audio"
    CATEGORY = "FlowScale/Utilities"

    def combine_audio(self, audio1, audio2, operation, volume1=1.0, volume2=1.0, label="Combined Audio"):
        try:
            # Extract audio data
            waveform1 = audio1["waveform"].squeeze(0) * volume1
            sample_rate1 = audio1["sample_rate"]
            
            waveform2 = audio2["waveform"].squeeze(0) * volume2
            sample_rate2 = audio2["sample_rate"]
            
            # Ensure both audios have the same sampling rate
            if sample_rate1 != sample_rate2:
                resampler = torchaudio.transforms.Resample(sample_rate2, sample_rate1)
                waveform2 = resampler(waveform2)
                sample_rate = sample_rate1
            else:
                sample_rate = sample_rate1
            
            # Ensure both have same number of channels
            if waveform1.shape[0] != waveform2.shape[0]:
                # Convert to mono if different channel configurations
                if waveform1.shape[0] > 1:
                    waveform1 = torch.mean(waveform1, dim=0, keepdim=True)
                if waveform2.shape[0] > 1:
                    waveform2 = torch.mean(waveform2, dim=0, keepdim=True)
                
                # Now both are mono, duplicate to match
                num_channels = max(waveform1.shape[0], waveform2.shape[0])
                if waveform1.shape[0] < num_channels:
                    waveform1 = waveform1.repeat(num_channels, 1)
                if waveform2.shape[0] < num_channels:
                    waveform2 = waveform2.repeat(num_channels, 1)
            
            # Apply selected operation
            if operation == "overlay":
                # Overlay audio2 on top of audio1
                result_len = max(waveform1.shape[1], waveform2.shape[1])
                combined = torch.zeros((waveform1.shape[0], result_len), dtype=waveform1.dtype, device=waveform1.device)
                combined[:, :waveform1.shape[1]] += waveform1
                combined[:, :waveform2.shape[1]] += waveform2
                
            elif operation == "concat":
                # Concatenate audio2 after audio1
                combined = torch.cat([waveform1, waveform2], dim=1)
                
            elif operation == "mix":
                # Mix audio1 and audio2 (average them)
                result_len = max(waveform1.shape[1], waveform2.shape[1])
                combined = torch.zeros((waveform1.shape[0], result_len), dtype=waveform1.dtype, device=waveform1.device)
                
                # Add weighted first audio
                combined[:, :waveform1.shape[1]] += waveform1
                
                # Add weighted second audio
                combined[:, :waveform2.shape[1]] += waveform2
                
                # Calculate average based on overlapping portions
                overlap = min(waveform1.shape[1], waveform2.shape[1])
                if overlap > 0:
                    combined[:, :overlap] *= 0.5  # Average in the overlapping region
            
            # Create the combined audio dict
            combined_audio = {
                "waveform": combined.unsqueeze(0),  # Add batch dimension back
                "sample_rate": sample_rate
            }
            
            print(f"I/O Label: {label}")
            return (combined_audio,)
            
        except Exception as e:
            print(f"Error combining audio: {e}")
            # Return first audio on error
            return (audio1,)