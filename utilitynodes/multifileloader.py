import os
import folder_paths
import random
import string
import json

class MultiFileLoaderNode:
    """
    A ComfyUI node for loading multiple files at once through the UI.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_list": ("STRING", {"multiline": True, "default": "[]"}),
            },
            "optional": {
                "label": ("STRING", {"default": "Multi-File Uploader"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("file_paths",)
    FUNCTION = "process_files"
    CATEGORY = "FlowScale/IO"

    def process_files(self, file_list, label="Multi-File Uploader"):
        """
        Process the uploaded files and return their paths.
        """
        print(f"I/O Label: {label}")
        
        # Parse the file list JSON if it's not empty
        if file_list and file_list.strip() != "[]":
            try:
                files = json.loads(file_list)
                if isinstance(files, list):
                    # Format paths as a JSON array for easier handling downstream
                    return (json.dumps(files),)
                else:
                    print("Warning: Received invalid file_list format, expected JSON array")
                    return ("[]",)
            except json.JSONDecodeError:
                print("Warning: Couldn't parse file_list JSON")
                return ("[]",)
        
        # Return empty array if no files were provided
        return ("[]",)