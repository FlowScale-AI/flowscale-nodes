import random
import string

class FSLoadInteger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "default_value": (
                    "INT",
                    {"default": 0},
                ),
            },
            "optional": {
                "label": ("STRING", {"default": "Input Integer"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "run"

    CATEGORY = "FlowScale/Media/Integer"

    def run(self, default_value=int, label="Input Integer"):
        print(f"I/O Label: {label}")
        return [default_value]


class FSSaveInteger:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "integer": ("INT", {"forceInput": True}),
                "filename_prefix": ("STRING", {"default": "FlowScale"}),
            },
            "optional": {
                "label": ("STRING", {"default": "Output Text"}),
            },
        }

    FUNCTION = "save_integer"

    CATEGORY = "FlowScale/Media/Integer"

    OUTPUT_NODE = True
    RETURN_TYPES = ()
    RETURN_NAMES = ()

    def save_text(self, integer:int, filename_prefix="FlowScale", label="Output Text"):
        print(f"I/O Label: {label}")
        import os
        if not integer:
            integer = 0
        
        text = str(integer)
        random_segment = ''.join(random.choices(string.digits, k=6))
        filename = f"{filename_prefix}_{random_segment}.txt"

        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"Preview: {text}")
        
        return ()

