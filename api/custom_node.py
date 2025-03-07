from server import PromptServer # type: ignore
import logging
from aiohttp import web
import os
import git
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
CUSTOM_NODES_DIR = os.path.join(os.getcwd(), "custom_nodes")

@PromptServer.instance.routes.get("/flowscale/node/list")
async def list_nodes(request):
    """
    Endpoint to list all custom nodes in the `custom_nodes` folder.
    """
    try:
        # Get all items in the custom nodes directory
        all_items = os.listdir(CUSTOM_NODES_DIR)
        nodes = []
        
        for item_name in all_items:
            item_path = os.path.join(CUSTOM_NODES_DIR, item_name)
            item_type = "directory" if os.path.isdir(item_path) else "file"
            
            nodes.append({
                "name": item_name,
                "type": item_type
            })
            
        return web.json_response(nodes, status=200)
    except Exception as e:
        logger.error(f"Error listing nodes: {str(e)}")
        return web.json_response({"error": "Failed to list nodes", "details": str(e)}, status=500)
    
@PromptServer.instance.routes.post("/flowscale/node/install")
async def install_node(request):
    """
    Endpoint to install a Git repository into the `custom_nodes` folder.
    """
    try:
        body = await request.json()
        repo_url = body.get("repo_url")
        repo_branch = body.get("branch", "main")
        commit_sha = body.get("sha")  # Optional SHA for specific commit checkout
        pip_packages = body.get("pip_packages", [])
        apt_packages = body.get("apt_packages", [])

        if not repo_url:
            return web.json_response({"error": "Repository URL is required"}, status=400)

        repo_name = os.path.basename(repo_url).replace(".git", "")
        repo_path = os.path.join(CUSTOM_NODES_DIR, repo_name)

        if os.path.exists(repo_path):
            return web.json_response({"error": "Repository already installed"}, status=400)

        logger.info(f"Cloning repository {repo_url} into {repo_path}...")
        repo = git.Repo.clone_from(repo_url, repo_path, branch=repo_branch)

        if commit_sha and commit_sha.strip(): 
            logger.info(f"Checking out to commit {commit_sha}...")
            repo.git.checkout(commit_sha)
            logger.info(f"Successfully checked out to commit {commit_sha}")
        
        # Install APT packages if provided
        if apt_packages and len(apt_packages) > 0:
            logger.info(f"Installing APT packages: {', '.join(apt_packages)}")
            try:
                apt_command = ["apt-get", "install", "-y"] + apt_packages

                try:
                    subprocess.run(["which", "sudo"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    subprocess.check_call(["sudo"] + apt_command)
                except (subprocess.SubprocessError, FileNotFoundError):
                    logger.info("sudo not available, trying to install without it...")
                    subprocess.check_call(apt_command)
                subprocess.check_call(["sudo"] + apt_command)
                logger.info("APT packages installed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install APT packages: {e}")
        
        # Install pip packages if provided
        if pip_packages and len(pip_packages) > 0:
            logger.info(f"Installing pip packages: {', '.join(pip_packages)}")
            try:
                pip_command = [os.sys.executable, "-m", "pip", "install"] + pip_packages
                subprocess.check_call(pip_command)
                logger.info("pip packages installed successfully")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install pip packages: {e}")
                return web.json_response({"error": "Failed to install pip packages", "details": str(e)}, status=500)

        requirements_file = os.path.join(repo_path, "requirements.txt")
        if os.path.exists(requirements_file):
            logger.info(f"Found requirements.txt at {requirements_file}. Installing dependencies...")
            try:
                subprocess.check_call([os.sys.executable, "-m", "pip", "install", "-r", requirements_file])
                logger.info(f"Dependencies from {requirements_file} installed successfully.")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install dependencies: {e}")
                return web.json_response({"error": "Failed to install dependencies", "details": str(e)}, status=500)

        logger.info(f"Successfully cloned {repo_url} into {repo_path}")
        return web.json_response({"message": "Repository installed successfully", "path": repo_path, "commit": commit_sha or repo.head.commit.hexsha}, status=200)

    except Exception as e:
        logger.error(f"Error installing repository: {str(e)}")
        return web.json_response({"error": "Failed to install repository", "details": str(e)}, status=500)

@PromptServer.instance.routes.post("/flowscale/node/uninstall")
async def uninstall_node(request):
    """
    Endpoint to uninstall a Git repository from the `custom_nodes` folder.
    """
    try:
        body = await request.json()
        repo_url = body.get("repo_url")

        if not repo_url:
            return web.json_response({"error": "Repository url is required"}, status=400)

        repo_name = repo_url.split("?")[0].split("/")[-1]

        # Construct the path to the repository folder
        repo_path = os.path.join(CUSTOM_NODES_DIR, repo_name)

        if not os.path.exists(repo_path):
            return web.json_response({"error": "Repository not found"}, status=404)

        uninstall_script_path = os.path.join(repo_path, "uninstall.py")
        if os.path.exists(uninstall_script_path):
            logger.info(f"Found uninstall script at {uninstall_script_path}. Executing...")
            try:
                subprocess.check_call([os.sys.executable, uninstall_script_path])
                logger.info(f"Uninstall script {uninstall_script_path} executed successfully.")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to execute uninstall script: {e}")
                
        # Delete the repository folder
        logger.info(f"Uninstalling repository: {repo_name} at path {repo_path}")
        for root, dirs, files in os.walk(repo_path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(repo_path)
        
        logger.info(f"Successfully uninstalled repository: {repo_name}")
        return web.json_response({"message": f"Repository {repo_name} uninstalled successfully"}, status=200)

    except Exception as e:
        logger.error(f"Error uninstalling repository: {str(e)}")
        return web.json_response({"error": "Failed to uninstall repository", "details": str(e)}, status=500)