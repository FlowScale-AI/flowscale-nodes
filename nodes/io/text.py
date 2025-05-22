import random
import string
import os

ORCHESTRATOR_API_URL = os.environ.get("ORCHESTRATOR_API_URL")
ORCHESTRATOR_API_KEY = os.environ.get("ORCHESTRATOR_API_KEY")

class FSLoadText:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "default_value": (
                    "STRING",
                    {"multiline": True, "default": ""},
                ),
                "label": ("STRING", {"default": "Input Text"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "run"

    CATEGORY = "FlowScale/Media/Text"

    def run(self, default_value=None, label="Input Text"):
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
                "label": ("STRING", {"default": "Output Text"}),
            },
        }

    FUNCTION = "save_text"

    CATEGORY = "FlowScale/Media/Text"

    OUTPUT_NODE = True
    RETURN_TYPES = ()
    RETURN_NAMES = ()

    def save_text(self, text, filename_prefix="FlowScale", label="Output Text"):
        print(f"I/O Label: {label}")
        import os
        if not text:
            text = ""

        random_segment = ''.join(random.choices(string.digits, k=6))
        filename = f"{filename_prefix}_{random_segment}.txt"

        if ORCHESTRATOR_API_URL:
            import httpx
            try:
                body = {
                    "type": "text",
                    "content": text,
                    "filename_prefix": filename_prefix,
                }
                headers = {
                    "X-API-Key": ORCHESTRATOR_API_KEY,
                }
                httpx.post(f"{ORCHESTRATOR_API_URL}/api/v1/webhook", json=body, headers=headers)
            except httpx.RequestError as e:
                print(f"Error fetching text from webhook: {e}")

        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"Preview: {text}")
        
        return ()

