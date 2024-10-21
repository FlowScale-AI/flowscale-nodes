from server import PromptServer # type: ignore
import logging
from aiohttp import web
import os
import mimetypes
import time
import re
import aiofiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Loading Flowscale IO nodes...")

mimetypes.add_type('image/webp', '.webp')

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

        # Check content type for images and videos
        content_type = field.headers.get('Content-Type', '')
        if not (content_type.startswith('image/') or content_type.startswith('video/')):
            return web.json_response({'error': 'Invalid content type. Only images and videos are allowed.'}, status=400, headers=headers)

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

        return web.json_response({'message': 'File uploaded successfully.', 'filename': filename, 'size': size}, headers=headers)

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
        
    BLACKLISTED_DIRECTORIES = ["models", "config", "custom_nodes", "api_server", "app", "comfy"]
    
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
    BLACKLISTED_DIRECTORIES = ["custom_nodes", "api_server", "app", "comfy"]
        
    sanitized_filepath = os.path.normpath(filepath).lstrip(os.sep).rstrip(os.sep)
    
    path_parts = sanitized_filepath.split(os.sep)
    if any(part in BLACKLISTED_DIRECTORIES for part in path_parts):
        return web.json_response({
            "error": "Invalid file path."
        }, status=400, content_type='application/json')
        
    absolute_filepath = os.path.abspath(os.path.join(base_directory, sanitized_filepath))
    
    if not absolute_filepath.startswith(base_directory):
        return web.json_response({
            "error": "Invalid file path."
        }, status=400, content_type='application/json')
    
    if not os.path.exists(absolute_filepath) or not os.path.isfile(absolute_filepath):
        return web.json_response({
            "error": "File does not exist."
        }, status=404, content_type='application/json')

    supported_extensions = [
        ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm",
        ".gif",
        ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".svg", ".webp", ".avif", ".jfif",
        ".txt", ".pdf", ".docx",
        ".safetensors", ".pth", ".ckpt", ".onnx", ".pb", ".h5", ".pt", ".pkl"
    ]
    
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
