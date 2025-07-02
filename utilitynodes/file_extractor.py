import json
import os

import folder_paths  # type: ignore


class FileExtractorNode:
    """
    A ComfyUI node to extract an individual file from a collection of files.
    Works with the MultiFileLoaderNode to process files one by one.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_collection": ("STRING", {"multiline": True}),
                "index": ("INT", {"default": 0, "min": 0, "step": 1}),
            },
            "optional": {
                "auto_increment": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("file_path", "file_metadata", "current_index")
    FUNCTION = "extract_file"
    CATEGORY = "FlowScale/Files/Extract"

    # Store state for auto-increment feature
    current_index = 0

    def extract_file(self, file_collection, index=0, auto_increment=False):
        """
        Extract a single file from the file collection.

        Args:
            file_collection: JSON string containing file info objects
            index: Index of the file to extract
            auto_increment: Whether to auto-increment the index each time the node is called

        Returns:
            Tuple of (file_path, metadata_json, current_index)
        """
        try:
            # Parse the file collection
            files = json.loads(file_collection)

            if not isinstance(files, list):
                print(f"Error: Expected a list of files, got {type(files)}")
                return ("", "{}", index)

            # Handle auto-increment
            if auto_increment:
                # Use the stored index if it's within bounds
                if FileExtractorNode.current_index < len(files):
                    index = FileExtractorNode.current_index
                    FileExtractorNode.current_index += 1
                else:
                    # Reset to beginning if we've gone through all files
                    index = 0
                    FileExtractorNode.current_index = 1
            else:
                # Reset the stored index if not using auto-increment
                FileExtractorNode.current_index = 0

            # Check if index is valid
            if index < 0 or index >= len(files):
                print(f"Error: Index {index} out of range (0-{len(files) - 1})")
                return ("", "{}", index)

            # Extract the file info
            file_info = files[index]

            # If it's a simple string, convert to an object
            if isinstance(file_info, str):
                file_path = file_info
                metadata = {}
            else:
                file_path = file_info.get("path", "")
                # Remove path from metadata as it's returned separately
                metadata = {k: v for k, v in file_info.items() if k != "path"}

            # Make sure file exists
            if file_path.startswith("input/"):
                input_dir = folder_paths.get_input_directory()
                full_path = os.path.join(input_dir, file_path[6:])  # Remove "input/" prefix
                if not os.path.exists(full_path):
                    print(f"Warning: File not found: {full_path}")

            return (file_path, json.dumps(metadata, indent=2), index)

        except json.JSONDecodeError:
            print("Error: Invalid JSON in file_collection")
            return ("", "{}", index)
        except Exception as e:
            print(f"Error: {str(e)}")
            return ("", "{}", index)
