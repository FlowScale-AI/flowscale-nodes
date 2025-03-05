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
                "filename_prefix": ("STRING", {"default": "Flowscale"}),
            },
        }

    FUNCTION = "save_text"

    CATEGORY = "text"
    OUTPUT_NODE = True
    RETURN_TYPES = ()

    def save_text(self, text, filename_prefix="Flowscale"):
        import os

        filename_prefix = filename_prefix or "Flowscale"
        filename = f"{filename_prefix}.txt"

        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"Preview: {text}")
        
        # Return both the UI element and the filepath
        return {"ui": {"text": text}}

