class FSLoadText:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "default_value": (
                    "STRING",
                    {"multiline": True, "default": ""},
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "run"

    CATEGORY = "text"

    def run(self, default_value=None):
        return [default_value]


class FSSaveText:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True}),
                "filename": ("STRING", {"default": "output.txt"}),
            },
            "optional": {
                "append": ("BOOLEAN", {"default": False}),
                "show_preview": ("BOOLEAN", {"default": True}),
                "max_preview_length": ("INT", {"default": 1000, "min": 100, "max": 10000, "step": 100}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)

    FUNCTION = "save_text"

    CATEGORY = "text"
    OUTPUT_NODE = True

    def save_text(self, text, filename, append=False, show_preview=True, max_preview_length=1000):
        import os

        # Ensure the filename has a .txt extension if not provided
        if not filename.endswith(".txt"):
            filename += ".txt"

        # Make sure we're writing to the output directory
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        # Write the text to the file (append or overwrite)
        mode = "a" if append else "w"
        with open(filepath, mode, encoding="utf-8") as f:
            f.write(text)
            
        # If append mode, read the entire file content for the preview
        if append and show_preview:
            with open(filepath, 'r', encoding="utf-8") as f:
                full_text = f.read()
                text_to_display = full_text
        else:
            text_to_display = text
            
        # Prepare UI preview
        if show_preview:
            # Limit preview length if needed
            if len(text_to_display) > max_preview_length:
                display_text = text_to_display[:max_preview_length] + "... (truncated)"
            else:
                display_text = text_to_display
                
            # Create a UI element for displaying the text
            results = [{
                "type": "text",
                "text": display_text,
                "filename": filename,
                "filepath": filepath
            }]
            
            # Return both the UI element and the filepath
            return {"ui": {"texts": results}, "result": (filepath,)}
        else:
            # Just return the filepath without UI display
            return (filepath,)

