import requests
import logging
import base64
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubReadmeExtractor:
    """
    A ComfyUI node for extracting README content from public GitHub repositories.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "github_url": ("STRING", {"default": "https://github.com/username/repository"}),
            },
            "optional": {
                "branch": ("STRING", {"default": "main"}),
                "silent_errors": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_readme"
    CATEGORY = "Utility"

    def extract_readme(self, github_url, branch="main", silent_errors=True):
        """
        Extracts README content from a GitHub repository.
        
        Args:
            github_url: URL to a GitHub repository
            branch: Branch to extract README from (default: main)
            silent_errors: Whether to silence errors (returns empty string on error)
            
        Returns:
            README content as text
        """
        try:
            # Parse GitHub URL to get owner and repo name
            parsed_url = urlparse(github_url)
            
            if parsed_url.netloc != "github.com":
                if silent_errors:
                    return ("Not a valid GitHub URL",)
                raise ValueError("Not a valid GitHub URL")
            
            path_parts = [part for part in parsed_url.path.split('/') if part]
            if len(path_parts) < 2:
                if silent_errors:
                    return ("Invalid GitHub repository URL",)
                raise ValueError("Invalid GitHub repository URL")
            
            owner = path_parts[0]
            repo = path_parts[1]
            
            # Common README file names to try
            readme_filenames = ["README.md", "README", "readme.md", "Readme.md", "README.txt"]
            
            readme_content = None
            
            # Try each possible README filename
            for filename in readme_filenames:
                # Form the GitHub API URL to get the readme content
                api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}?ref={branch}"
                
                logger.info(f"Trying to fetch {filename} from {owner}/{repo}")
                response = requests.get(api_url)
                
                if response.status_code == 200:
                    # Found a README file
                    content_data = response.json()
                    
                    if content_data.get("encoding") == "base64":
                        # Decode the base64 content
                        readme_content = base64.b64decode(content_data["content"]).decode("utf-8")
                        logger.info(f"Successfully extracted {filename}")
                        break
            
            if readme_content is None:
                if silent_errors:
                    return ("No README file found in the repository",)
                raise ValueError("No README file found in the repository")
            
            return (readme_content,)
        
        except Exception as e:
            logger.error(f"Error extracting README: {str(e)}")
            if silent_errors:
                return (f"Error: {str(e)}",)
            raise