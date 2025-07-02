import os
import uuid

import folder_paths  # type: ignore
import httpx


class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False


WILDCARD = AnyType("*")


class FSLoadLoRA:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "default_lora_name": (folder_paths.get_filename_list("loras"),),
                "lora_url": (
                    "STRING",
                    {"multiline": False, "default": ""},
                ),
                "auth_token": (
                    "STRING",
                    {"multiline": False, "default": ""},
                ),
                "save_filename": (
                    "STRING",
                    {"multiline": False, "default": ""},
                ),
                "label": (
                    "STRING",
                    {"default": "Input LoRA"},
                ),
            },
        }

    RETURN_TYPES = (WILDCARD,)
    RETURN_NAMES = ("path",)
    FUNCTION = "run"
    CATEGORY = "FlowScale/Models/LoRA"

    def run(
        self,
        default_lora_name=None,
        lora_url=None,
        auth_token=None,
        save_filename=None,
        label="Input LoRA",
    ):
        print(f"I/O Label: {label}")
        if lora_url:
            if lora_url.startswith("https://"):
                if save_filename:
                    existing_loras = folder_paths.get_filename_list("loras")
                    if save_filename in existing_loras:
                        print(f"using lora: {save_filename}")
                        return (save_filename,)
                else:
                    save_filename = str(uuid.uuid4()) + ".safetensors"
                destination_path = os.path.join(
                    folder_paths.folder_names_and_paths["loras"][0][0], save_filename
                )
                print(f"Saving lora {save_filename} to {destination_path}")
                headers = {"User-Agent": "Mozilla/5.0"}
                if auth_token:
                    headers["Authorization"] = f"Bearer {auth_token}"

                # Use httpx with timeout and better error handling
                timeout = httpx.Timeout(300.0, connect=30.0)  # 5 min download, 30s connect
                with httpx.stream(
                    "GET", lora_url, headers=headers, follow_redirects=True, timeout=timeout
                ) as response:
                    response.raise_for_status()  # Raise exception for HTTP errors
                    with open(destination_path, "wb") as out_file:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            out_file.write(chunk)
                return (save_filename,)
            else:
                print(f"Lora URL does not start with <https://>: {lora_url}")
                return (lora_url,)
        else:
            return (default_lora_name,)
