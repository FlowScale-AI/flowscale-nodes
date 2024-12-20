import glob
import json
from server import PromptServer # type: ignore
import logging
from aiohttp import web
import os
import mimetypes
import time
import re
import aiofiles
import boto3
import git
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
CUSTOM_NODES_DIR = os.path.join(os.getcwd(), "custom_nodes")

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


        if not repo_url:
            return web.json_response({"error": "Repository URL is required"}, status=400)

        repo_name = os.path.basename(repo_url).replace(".git", "")
        repo_path = os.path.join(CUSTOM_NODES_DIR, repo_name)

        if os.path.exists(repo_path):
            return web.json_response({"error": "Repository already installed"}, status=400)

        logger.info(f"Cloning repository {repo_url} into {repo_path}...")
        repo = git.Repo.clone_from(repo_url, repo_path, branch=repo_branch)

        if commit_sha:
            logger.info(f"Checking out to commit {commit_sha}...")
            repo.git.checkout(commit_sha)
            logger.info(f"Successfully checked out to commit {commit_sha}")

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