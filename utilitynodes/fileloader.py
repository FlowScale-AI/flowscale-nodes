from pathlib import Path
from tempfile import NamedTemporaryFile
from PyPDF2 import PdfReader
import requests

class FileLoaderNode:
    """
    A ComfyUI node for loading individual or zipped text files.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_url": ("STRING", {}),
                "silent_errors": ("BOOLEAN",),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "load_file"
    CATEGORY = "FlowScale/Files/Load"

    def load_file(self, file_url, silent_errors=True):
        """
        Loads a file or processes a zip archive.
        """
        return self._load_from_url(file_url, silent_errors)
        
    def _load_from_url(self, url, silent_errors):
        """
        Loads data from a URL.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            
            if "application/pdf" in content_type:
                with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_file.write(chunk)
                    temp_path = Path(temp_file.name)

                return self._process_pdf_file(temp_path, silent_errors=silent_errors)
            elif "text/plain" in content_type:
                return response.text
            else:
                if silent_errors:
                    return {}
                raise ValueError(f"Unsupported content type: {content_type}")
        except Exception as e:
            if silent_errors:
                return {}
            raise ValueError(f"Failed to load data from URL: {e}")
        
    def _process_pdf_file(self, file_path, silent_errors):
        """
        Process a PDF file and extract its text content.
        """
        try:
            pdf_text = []
            with open(file_path, "rb") as file:
                reader = PdfReader(file)
                for page in reader.pages:
                    pdf_text.append(page.extract_text())

            print(pdf_text)
            response = "\n".join(pdf_text)
            return (response, )
        except Exception as e:
            if silent_errors:
                return {}
            raise ValueError(f"Failed to process PDF file: {e}")