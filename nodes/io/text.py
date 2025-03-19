import random
import string

class FSLoadText:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "default_value": (
                    "STRING",
                    {"multiline": True, "default": ""},
                ),
                "label": ("STRING", {"default": "Input Image"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "run"

    CATEGORY = "FlowScale/IO"

    def run(self, default_value=None, label="Input Image"):
        print(f"I/O Label: {label}")
        return [default_value]


class FSSaveText:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "filename_prefix": ("STRING", {"default": "FlowScale"}),
            },
            "optional": {
                "label": ("STRING", {"default": "Input Image"}),
            },
        }

    FUNCTION = "save_text"

    CATEGORY = "FlowScale/IO"

    OUTPUT_NODE = True
    RETURN_TYPES = ()
    RETURN_NAMES = ()

    def save_text(self, text, filename_prefix="FlowScale", label="Input Image"):
        print(f"I/O Label: {label}")
        import os

        random_segment = ''.join(random.choices(string.digits, k=6))
        filename = f"{filename_prefix}_{random_segment}.txt"

        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"Preview: {text}")
        
        return ()

