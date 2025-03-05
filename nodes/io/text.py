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
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)

    FUNCTION = "save_text"

    CATEGORY = "text"
    OUTPUT_NODE = True

    def save_text(self, text, filename, append=False):
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

        return [filepath]

