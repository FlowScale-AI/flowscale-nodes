import os
import folder_paths
import random
import string
import json
import mimetypes
import re

class MultiFileLoaderNode:
    """
    A ComfyUI node for loading multiple files at once through the UI.
    Supports metadata extraction and file filtering.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_list": ("STRING", {"multiline": True, "default": "[]"}),
            },
            "optional": {
                "label": ("STRING", {"default": "Multi-File Uploader"}),
                "filter_extensions": ("STRING", {"default": "", "placeholder": "jpg,png,pdf (comma separated)"}),
                "extract_metadata": ("BOOLEAN", {"default": False})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_paths",)
    FUNCTION = "process_files"
    CATEGORY = "FlowScale/Files/Batch"

    def process_files(self, file_list, label="Multi-File Uploader", filter_extensions="", extract_metadata=False):
        """
        Process the uploaded files and return their paths with optional metadata.
        
        Args:
            file_list: JSON string containing file paths
            label: Display label for the node
            filter_extensions: Comma-separated list of extensions to filter (e.g. "jpg,png,pdf")
            extract_metadata: Whether to extract metadata from files
            
        Returns:
            JSON string with file paths and optional metadata
        """
        print(f"I/O Label: {label}")
        
        # Parse the file list JSON if it's not empty
        files = []
        if file_list and file_list.strip() != "[]":
            try:
                files = json.loads(file_list)
                if not isinstance(files, list):
                    print("Warning: Received invalid file_list format, expected JSON array")
                    files = []
            except json.JSONDecodeError:
                print("Warning: Couldn't parse file_list JSON")
                files = []
        
        # Apply extension filtering if specified
        if filter_extensions:
            extensions = [ext.strip().lower() for ext in filter_extensions.split(',') if ext.strip()]
            if extensions:
                files = [f for f in files if any(f.lower().endswith(f".{ext}") for ext in extensions)]
        
        # Process files and add metadata if requested
        result = []
        for file_path in files:
            # Skip invalid paths
            if not file_path or not isinstance(file_path, str):
                continue
                
            # Create full path if needed
            if file_path.startswith("input/"):
                input_dir = folder_paths.get_input_directory()
                full_path = os.path.join(input_dir, file_path[6:])  # Remove "input/" prefix
            else:
                full_path = file_path
            
            # Check if file exists
            if not os.path.exists(full_path):
                print(f"Warning: File not found: {full_path}")
                continue
                
            # Basic file info
            file_info = {"path": file_path}
            
            # Add metadata if requested
            if extract_metadata:
                file_info.update(self._extract_file_metadata(full_path))
            
            result.append(file_info)
        
        return (json.dumps(result, indent=2),)
    
    def _extract_file_metadata(self, file_path):
        """
        Extract metadata from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            "name": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "last_modified": os.path.getmtime(file_path)
        }
        
        # Guess mimetype
        mime_type, encoding = mimetypes.guess_type(file_path)
        if mime_type:
            metadata["mime_type"] = mime_type
            
            # Extract type category
            type_category = mime_type.split('/')[0]
            metadata["type"] = type_category
        
        # Handle special file types
        ext = os.path.splitext(file_path)[1].lower()
        
        # Get better file dimensions for images
        if mime_type and mime_type.startswith('image/'):
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    metadata["width"] = img.width
                    metadata["height"] = img.height
                    metadata["format"] = img.format
            except:
                pass
                
        # Get video info
        elif mime_type and mime_type.startswith('video/'):
            try:
                import cv2
                cap = cv2.VideoCapture(file_path)
                if cap.isOpened():
                    metadata["width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    metadata["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    metadata["fps"] = cap.get(cv2.CAP_PROP_FPS)
                    metadata["frame_count"] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    metadata["duration"] = metadata["frame_count"] / metadata["fps"] if metadata["fps"] > 0 else 0
                cap.release()
            except:
                pass
                
        return metadata