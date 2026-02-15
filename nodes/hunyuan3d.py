import logging
import os
import random
import string
import time

import folder_paths  # type: ignore
import httpx
import numpy as np
import torch
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FAL_API_URL = "https://fal.run/fal-ai/hunyuan-3d/v3.1/rapid/text-to-3d"
FAL_QUEUE_URL = "https://queue.fal.run/fal-ai/hunyuan-3d/v3.1/rapid/text-to-3d"


def _get_fal_key():
    key = os.environ.get("FAL_KEY", "")
    if not key:
        raise ValueError(
            "FAL_KEY environment variable is not set. "
            "Get your API key from https://fal.ai/dashboard/keys"
        )
    return key


class FSHunyuan3DGenerate:
    """Generate 3D models from text prompts using Hunyuan 3D v3.1 via fal.ai."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                        "placeholder": "Describe the 3D object to generate (max 200 chars)",
                    },
                ),
            },
            "optional": {
                "enable_pbr": (
                    "BOOLEAN",
                    {
                        "default": False,
                    },
                ),
                "enable_geometry": (
                    "BOOLEAN",
                    {
                        "default": False,
                    },
                ),
                "output_format": (
                    ["obj", "glb"],
                    {
                        "default": "obj",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "IMAGE", "STRING")
    RETURN_NAMES = ("model_path", "model_url", "thumbnail", "model_urls_json")
    FUNCTION = "generate_3d"
    CATEGORY = "FlowScale/Media/3D"
    OUTPUT_NODE = True

    def generate_3d(
        self,
        prompt,
        enable_pbr=False,
        enable_geometry=False,
        output_format="obj",
    ):
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if len(prompt) > 200:
            logger.warning("Prompt exceeds 200 characters, it will be truncated by the API")

        fal_key = _get_fal_key()
        headers = {
            "Authorization": f"Key {fal_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "prompt": prompt.strip(),
            "enable_pbr": enable_pbr,
            "enable_geometry": enable_geometry,
        }

        logger.info(f"Hunyuan 3D: Submitting generation request for prompt: '{prompt[:50]}...'")

        # Submit to queue for long-running generation
        timeout = httpx.Timeout(30.0, connect=10.0)
        response = httpx.post(FAL_QUEUE_URL, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        queue_data = response.json()

        request_id = queue_data.get("request_id")
        if not request_id:
            raise ValueError(f"No request_id in queue response: {queue_data}")

        logger.info(f"Hunyuan 3D: Queued with request_id: {request_id}")

        # Use URLs from the queue response (handles nested model paths correctly)
        status_url = queue_data.get("status_url")
        result_url = queue_data.get("response_url")
        if not status_url or not result_url:
            raise ValueError(
                f"Missing status_url or response_url in queue response: {queue_data}"
            )

        poll_timeout = httpx.Timeout(30.0, connect=10.0)

        max_wait = 600  # 10 minutes max
        start_time = time.time()
        poll_interval = 2.0

        while time.time() - start_time < max_wait:
            status_response = httpx.get(
                status_url, headers=headers, params={"logs": 1}, timeout=poll_timeout
            )
            status_response.raise_for_status()
            status_data = status_response.json()
            status = status_data.get("status")

            # Log any progress messages
            for log_entry in status_data.get("logs", []):
                logger.info(f"Hunyuan 3D: {log_entry.get('message', '')}")

            if status == "COMPLETED":
                logger.info("Hunyuan 3D: Generation completed!")
                break
            elif status in ("FAILED", "CANCELLED"):
                error = status_data.get("error", "Unknown error")
                raise RuntimeError(f"Hunyuan 3D generation failed: {error}")
            else:
                logger.info(f"Hunyuan 3D: Status: {status}, waiting...")
                time.sleep(poll_interval)
                poll_interval = min(poll_interval * 1.2, 5.0)
        else:
            raise TimeoutError("Hunyuan 3D: Generation timed out after 10 minutes")

        # Fetch result
        result_response = httpx.get(result_url, headers=headers, timeout=poll_timeout)
        result_response.raise_for_status()
        result = result_response.json()

        # Process outputs
        output_dir = folder_paths.get_output_directory()
        os.makedirs(output_dir, exist_ok=True)
        random_segment = "".join(random.choices(string.digits, k=6))

        # Download the 3D model file
        model_path = ""
        model_url = ""

        if output_format == "obj" and not enable_geometry:
            model_file = result.get("model_obj")
            if model_file and model_file.get("url"):
                model_url = model_file["url"]
                filename = f"hunyuan3d_{random_segment}.obj"
                model_path = os.path.join(output_dir, filename)
                self._download_file(model_url, model_path, headers)

                # Also download MTL and texture for OBJ
                mtl_file = result.get("material_mtl")
                if mtl_file and mtl_file.get("url"):
                    mtl_path = os.path.join(output_dir, f"hunyuan3d_{random_segment}_material.mtl")
                    self._download_file(mtl_file["url"], mtl_path, headers)

                texture_file = result.get("texture")
                if texture_file and texture_file.get("url"):
                    texture_path = os.path.join(
                        output_dir, f"hunyuan3d_{random_segment}_material.png"
                    )
                    self._download_file(texture_file["url"], texture_path, headers)
        else:
            # GLB format or geometry-only mode (which defaults to GLB)
            model_urls = result.get("model_urls", {})
            glb_file = model_urls.get("glb")
            if glb_file and glb_file.get("url"):
                model_url = glb_file["url"]
                filename = f"hunyuan3d_{random_segment}.glb"
                model_path = os.path.join(output_dir, filename)
                self._download_file(model_url, model_path, headers)

        # If no model was downloaded via preferred format, try alternatives
        if not model_path:
            model_urls = result.get("model_urls", {})
            for fmt in ["obj", "glb"]:
                fmt_data = model_urls.get(fmt)
                if fmt_data and fmt_data.get("url"):
                    model_url = fmt_data["url"]
                    ext = fmt
                    filename = f"hunyuan3d_{random_segment}.{ext}"
                    model_path = os.path.join(output_dir, filename)
                    self._download_file(model_url, model_path, headers)
                    break

        if not model_path:
            raise RuntimeError("Hunyuan 3D: No 3D model file found in API response")

        # Download and process thumbnail
        thumbnail_tensor = torch.zeros(1, 512, 512, 3)
        thumbnail_data = result.get("thumbnail")
        if thumbnail_data and thumbnail_data.get("url"):
            try:
                thumb_path = os.path.join(output_dir, f"hunyuan3d_{random_segment}_preview.png")
                self._download_file(thumbnail_data["url"], thumb_path, headers)
                img = Image.open(thumb_path).convert("RGB")
                img_array = np.array(img).astype(np.float32) / 255.0
                thumbnail_tensor = torch.from_numpy(img_array).unsqueeze(0)
            except Exception as e:
                logger.warning(f"Hunyuan 3D: Failed to load thumbnail: {e}")

        # Build model URLs JSON
        import json

        model_urls_json = json.dumps(result.get("model_urls", {}), indent=2)

        logger.info(f"Hunyuan 3D: Model saved to {model_path}")
        return {
            "ui": {"text": [os.path.basename(model_path)]},
            "result": (model_path, model_url, thumbnail_tensor, model_urls_json),
        }

    def _download_file(self, url, dest_path, headers):
        """Download a file from URL to destination path."""
        timeout = httpx.Timeout(120.0, connect=10.0)
        with httpx.stream("GET", url, timeout=timeout) as response:
            response.raise_for_status()
            with open(dest_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)
        logger.info(f"Hunyuan 3D: Downloaded {os.path.basename(dest_path)}")
