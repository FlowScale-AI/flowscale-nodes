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
import shutil
import folder_paths

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mimetypes.add_type('image/webp', '.webp')
mimetypes.add_type('audio/mp3', '.mp3')
mimetypes.add_type('audio/wav', '.wav')

@PromptServer.instance.routes.post("/flowscale/io/upload")
async def upload_media(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    try:
        reader = await request.multipart()
        field = await reader.next()

        if field is None or not field.filename:
            return web.json_response({'error': 'No file was uploaded.'}, status=400, headers=headers)

        filename = os.path.basename(field.filename)
        filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)

        # Get the file extension
        ext = os.path.splitext(filename)[1].lower()
        
        # Define allowed extensions
        allowed_image_exts = ['.jpg', '.jpeg', '.png', '.webp', '.avif', '.heif']
        allowed_video_exts = ['.mp4', '.webm', '.mkv', '.mov', '.avi', '.wmv', '.flv', '.gif']
        allowed_audio_exts = ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a']

        # Check if extension is allowed
        if ext not in allowed_image_exts + allowed_video_exts + allowed_audio_exts:
            return web.json_response(
                {'error': 'Invalid file type. Only images, videos, and audio files are allowed.'}, 
                status=400, 
                headers=headers
            )

        # Determine target directory (input for all media types)
        media_directory = os.path.join(os.getcwd(), "input")
        os.makedirs(media_directory, exist_ok=True)

        file_path = os.path.join(media_directory, filename)
        size = 0

        async with aiofiles.open(file_path, 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                size += len(chunk)
                await f.write(chunk)

        # Determine the file type for the response
        file_type = 'image'
        if ext in allowed_video_exts:
            file_type = 'video'
        elif ext in allowed_audio_exts:
            file_type = 'audio'

        return web.json_response({
            'message': 'File uploaded successfully.',
            'filename': filename,
            'size': size,
            'type': file_type
        }, headers=headers)

    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return web.json_response({'error': str(e)}, status=500, headers=headers)

@PromptServer.instance.routes.post("/flowscale/io/upload_batch")
async def upload_batch(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    try:
        reader = await request.multipart()
        path = None
        file_infos = []
        base_directory = os.getcwd()
        
        while True:
            field = await reader.next()
            if field is None:
                break
            
            if field.name == 'path':
                raw_path = await field.text()
                if raw_path.startswith("./") or raw_path.startswith("../"):
                    raw_path = raw_path.lstrip("./").lstrip("../")
                if raw_path.startswith("/") or raw_path.startswith("\\"):
                    raw_path = raw_path.lstrip("/").lstrip("\\")
                
                sanitized_path = os.path.normpath(os.path.join(base_directory, raw_path))
                
                if not sanitized_path.startswith(base_directory):
                    return web.json_response({'error': 'Invalid path provided.'}, status=400, headers=headers)
                
                os.makedirs(sanitized_path, exist_ok=True)
                path = sanitized_path
            
            elif field.name == 'images':
                if not path:
                    return web.json_response({'error': 'No path was provided.'}, status=400, headers=headers)
                
                if not field.filename:
                    continue
                
                filename = os.path.basename(field.filename)
                filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
                
                content_type = field.headers.get('Content-Type', '')
                if not content_type.startswith('image/'):
                    continue
                
                file_path = os.path.join(path, filename)
                size = 0
                
                async with aiofiles.open(file_path, 'wb') as f:
                    while True:
                        chunk = await field.read_chunk()
                        if not chunk:
                            break
                        size += len(chunk)
                        await f.write(chunk)
                        
                file_infos.append({'filename': filename, 'size': size, 'path': file_path})
            
            else:
                pass
        
        if not file_infos or not path:
            return web.json_response({'error': 'No images/path were uploaded.'}, status=400, headers=headers)
        
        return web.json_response({'message': 'Files uploaded successfully.', 'files': file_infos}, headers=headers)
    
    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        return web.json_response({'error': str(e)}, status=500, headers=headers)
    

@PromptServer.instance.routes.get("/flowscale/io/list")
async def fetch_path_contents(request):
    directory_name = request.query.get('directory', 'output')
    if directory_name.startswith("./") or directory_name.startswith("../"):
        directory_name = directory_name.lstrip("./").lstrip("../")
    if directory_name.startswith("/") or directory_name.startswith("\\"):
        directory_name = directory_name.lstrip("/").lstrip("\\")
    
    base_directory = os.getcwd()
        
    BLACKLISTED_DIRECTORIES = ["config", "api_server", "app", "comfy"]
    
    sanitized_directory_name = os.path.normpath(directory_name).lstrip(os.sep).rstrip(os.sep)
    
    directory_path = os.path.abspath(os.path.join(base_directory, sanitized_directory_name))

    if not directory_path.startswith(base_directory):
        return web.json_response({
            "error": "Invalid directory path."
        }, status=400, content_type='application/json')
        
    relative_path = os.path.relpath(directory_path, base_directory)
    path_parts = relative_path.split(os.sep)
    
    if any(part in BLACKLISTED_DIRECTORIES for part in path_parts):
        return web.json_response({
            "error": "Invalid directory path."
        }, status=400, content_type='application/json')
            
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return web.json_response({
            "error": "Directory does not exist."
        }, status=404, content_type='application/json')
    
    try:
        directory_contents = os.listdir(directory_path)
    except Exception as e:
        logger.error(f"Error fetching directory contents: {e}")
        return web.json_response({
            "error": str(e)
        }, status=500, content_type='application/json')
        
    return web.json_response({
        "directory": sanitized_directory_name,
        "directory_path": directory_path,
        "directory_contents": directory_contents
    }, content_type='application/json')


@PromptServer.instance.routes.get("/flowscale/io/search")
async def search_file(request):
    filepath = request.query.get('filepath')
    if not filepath:
        return web.json_response({
            "error": "filepath query parameter is required."
        }, status=400, content_type='application/json')
        
    if filepath.startswith("./") or filepath.startswith("../"):
        filepath = filepath.lstrip("./").lstrip("../")
    if filepath.startswith("/") or filepath.startswith("\\"):
        filepath = filepath.lstrip("/").lstrip("\\")

    base_directory = os.getcwd()
    BLACKLISTED_DIRECTORIES = ["api_server", "app", "comfy"]
        
    sanitized_filepath = os.path.normpath(filepath).lstrip(os.sep).rstrip(os.sep)
    
    path_parts = sanitized_filepath.split(os.sep)
    if any(part in BLACKLISTED_DIRECTORIES for part in path_parts):
        return web.json_response({
            "error": "Invalid file path."
        }, status=400, content_type='application/json')
        
    absolute_filepath = os.path.abspath(os.path.join(base_directory, sanitized_filepath))
    print(absolute_filepath)
    
    if not absolute_filepath.startswith(base_directory):
        return web.json_response({
            "error": "Invalid file path."
        }, status=400, content_type='application/json')
    
    search_directory = os.path.dirname(absolute_filepath)
    partial_filename = os.path.basename(absolute_filepath)
    
    if not os.path.exists(search_directory) or not os.path.isdir(search_directory):
        return web.json_response({
            "error": "Directory does not exist."
        }, status=404, content_type='application/json')
        

    supported_extensions = [
        ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm",
        ".gif",
        ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".svg", ".webp", ".avif", ".jfif", ".heif",
        ".txt", ".pdf", ".docx",
        ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a",
    ]
    
    candidates = []
    for extension in supported_extensions:
        pattern = partial_filename + "*" + extension
        pattern_path = os.path.join(search_directory, pattern)
        for candidate_filepath in glob.glob(pattern_path):
            candidate_absolute_path = os.path.abspath(candidate_filepath)
            if not candidate_absolute_path.startswith(base_directory):
                continue
            
            relative_path = os.path.relpath(candidate_absolute_path, base_directory)
            path_parts = relative_path.split(os.sep)
            if any(part in BLACKLISTED_DIRECTORIES for part in path_parts):
                continue
            
            if os.path.isfile(candidate_absolute_path):
                candidates.append(candidate_absolute_path)
                break
        
        if candidates:
            break
    
    if not candidates:
        return web.json_response({
            "error": "File not found."
        }, status=404, content_type='application/json')
        
    candidates.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    absolute_filepath = candidates[0]    
    
    file_extension = os.path.splitext(absolute_filepath)[1]
    if file_extension.lower() not in supported_extensions:
        return web.json_response({
            "error": "Unsupported file extension."
        }, status=415, content_type='application/json')
    
    video_extensions = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"]
    model_extensions = [".safetensors", ".pth", ".ckpt", ".onnx", ".pb", ".h5", ".pt", ".pkl"]
    max_delay = 30 if file_extension.lower() in video_extensions or file_extension.lower() in model_extensions else 5
    if not is_file_ready(absolute_filepath, max_delay):
        return web.json_response({
            "error": "File not ready yet."
        }, status=404, content_type='application/json')
    
    mime_type, _ = mimetypes.guess_type(absolute_filepath)
    if mime_type is None:
        mime_type = "application/octet-stream"
        
    if file_extension.lower() in model_extensions:
        with open(absolute_filepath.replace(file_extension, ".txt"), 'r') as f:
            content = f.read()

        logger.info(f"Reading model file: {absolute_filepath}")
        logger.info(f"Model metadata: {content}")
        
        data = json.loads(content)
        return web.json_response(data, content_type='application/json')
        
    else:
        try:
            return web.FileResponse(path=absolute_filepath, headers={
                'Content-Type': mime_type,
                'Content-Disposition': f'attachment; filename="{os.path.basename(absolute_filepath)}"'
            })
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return web.json_response({
                "error": str(e)
            }, status=500, content_type='application/json')

@PromptServer.instance.routes.delete("/flowscale/io/delete")
async def delete_file(request):   
    filename = request.query.get('filename')
    if not filename:
        return web.json_response({
            "error": "filename query parameter is required."
        }, status=400)
    
    filename = os.path.basename(filename)
    base_directory = os.getcwd()
    
    search_directories = ['output']
    file_found = False
    
    for directory in search_directories:
        file_path = os.path.join(base_directory, directory, filename)
        normalized_path = os.path.normpath(file_path)
        
        if not normalized_path.startswith(base_directory):
            continue
            
        relative_path = os.path.relpath(normalized_path, base_directory)
        path_parts = relative_path.split(os.sep)
        if any(part in ["config", "custom_nodes", "api_server", "app", "comfy"] for part in path_parts):
            continue
        
        try:
            if os.path.exists(normalized_path) and os.path.isfile(normalized_path):
                os.remove(normalized_path)
                file_found = True
                return web.json_response({
                    "message": f"File {filename} deleted successfully"
                })
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return web.json_response({
                "error": f"Error deleting file: {str(e)}"
            }, status=500)
    
    if not file_found:
        return web.json_response({
            "error": "File not found"
        }, status=404)
        
@PromptServer.instance.routes.delete("/flowscale/io/purge")
async def purge_directory(request):    
    output_dir = 'output'
    base_directory = os.getcwd()
    directory_path = os.path.abspath(os.path.join(base_directory, output_dir))
    
    try:
        os.makedirs(directory_path, exist_ok=True)
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        
        return web.json_response({
            "message": f"Directory purged successfully."
        })
    except Exception as e:
        logger.error(f"Error purging directory: {e}")
        return web.json_response({
            "error": f"Error purging directory: {str(e)}"
        }, status=500)

@PromptServer.instance.routes.delete("/flowscale/io/delete_directory")
async def delete_directory(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    directory_path = request.query.get('path')
    if not directory_path:
        return web.json_response({
            "error": "path query parameter is required."
        }, status=400, headers=headers)
    
    # Sanitize path input
    if directory_path.startswith("./") or directory_path.startswith("../"):
        directory_path = directory_path.lstrip("./").lstrip("../")
    if directory_path.startswith("/") or directory_path.startswith("\\"):
        directory_path = directory_path.lstrip("/").lstrip("\\")
    
    base_directory = os.getcwd()
    custom_nodes_dir = os.path.join(base_directory, "custom_nodes")
    
    # Ensure path is within custom_nodes directory
    sanitized_path = os.path.normpath(os.path.join(custom_nodes_dir, directory_path))
    
    if not sanitized_path.startswith(custom_nodes_dir):
        return web.json_response({
            "error": "Invalid directory path. Path must be within custom_nodes directory."
        }, status=400, headers=headers)
    
    # Prevent deletion of the custom_nodes directory itself
    if sanitized_path == custom_nodes_dir:
        return web.json_response({
            "error": "Cannot delete the custom_nodes directory itself."
        }, status=400, headers=headers)
    
    # Check if directory exists
    if not os.path.exists(sanitized_path) or not os.path.isdir(sanitized_path):
        return web.json_response({
            "error": "Directory does not exist."
        }, status=404, headers=headers)
    
    try:
        # Delete the directory and all contents
        shutil.rmtree(sanitized_path)
        logger.info(f"Directory deleted: {sanitized_path}")
        
        return web.json_response({
            "message": f"Directory {directory_path} deleted successfully. Server will reboot."
        }, headers=headers)
    except Exception as e:
        logger.error(f"Error deleting directory: {e}")
        return web.json_response({
            "error": f"Error deleting directory: {str(e)}"
        }, status=500, headers=headers)

@PromptServer.instance.routes.get("/flowscale/io/reboot")
async def reboot_server(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    try:
        import httpx
        import asyncio
        
        async def call_reboot():
            try:
                async with httpx.AsyncClient() as client:
                    reboot_url = f"http://localhost:{PromptServer.instance.port}/manager/reboot"
                    response = await client.get(reboot_url)
                    logger.info(f"Reboot API response: {response.status_code}")
        
            except Exception as e:
                logger.error(f"Error calling reboot API: {e}")
        
        asyncio.create_task(call_reboot())
        
        return web.json_response({
            "message": "Server will reboot."
        }, headers=headers)
    except Exception as e:
        logger.error(f"Error rebooting server: {e}")
        return web.json_response({
            "error": f"Error rebooting server: {str(e)}"
        }, status=500, headers=headers)

def is_file_ready(file_path, max_delay=15):
    check_interval = 5
    elapsed_time = 0
    stat_info = os.stat(file_path)
    size_initial = stat_info.st_size

    while elapsed_time < max_delay:
        time.sleep(check_interval)
        elapsed_time += check_interval
        stat_info = os.stat(file_path)
        size_current = stat_info.st_size

        if size_current != size_initial:
            return False
    
    return True

@PromptServer.instance.routes.post("/upload/video")
async def upload_video(request):
    try:
        data = await request.post()
        video = data['video']

        # Get filename and ensure it's safe
        filename = video.filename.lower()
        if not any(filename.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.webm', '.mkv', '.gif']):
            return web.Response(status=400, text="Invalid video format")

        # Save to input directory
        input_dir = folder_paths.get_input_directory()
        filepath = os.path.join(input_dir, filename)

        # Write the file
        with open(filepath, 'wb') as f:
            f.write(video.file.read())

        return web.Response(status=200)
    except Exception as e:
        return web.Response(status=500, text=str(e))

VIDEO_EXTENSIONS = ['mp4', 'avi', 'mov', 'webm']

@PromptServer.instance.routes.get("/fs/get_video_files")
async def get_video_files(request):
        input_dir = folder_paths.get_input_directory()
        files = []
        
        try:
            for f in os.listdir(input_dir):
                if os.path.isfile(os.path.join(input_dir, f)):
                    file_parts = f.split('.')
                    if len(file_parts) > 1 and (file_parts[-1].lower() in VIDEO_EXTENSIONS):
                        files.append(f)
            
            return web.json_response({"files": sorted(files)})
        except Exception as e:
            logger.error(f"Error getting video files: {e}")
            return web.Response(status=500, text=str(e))