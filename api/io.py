from server import PromptServer # type: ignore
from .. import logger
from aiohttp import web
import os
import glob
import mimetypes
import time
import re
import aiofiles

logger.info("Loading io nodes...")

@PromptServer.instance.routes.post("/flowscale/upload")
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

    
# OUTPUT

@PromptServer.instance.routes.get("/flowscale/output/list")
async def fetch_output_contents(request):
    output_directory = os.path.join(os.getcwd(), "output")
    
    if not os.path.exists(output_directory):
        return web.json_response({
            "error": "Output directory does not exist."
        }, status=404, content_type='application/json')
    
    try:
        directory_contents = os.listdir(output_directory)
    except Exception as e:
        return web.json_response({
            "error": str(e)
        }, status=500, content_type='application/json')
    
    print("Output Directory:", output_directory)
    print("Directory Contents:", directory_contents)
    
    return web.json_response({
        "output_directory": output_directory,
        "directory_contents": directory_contents
    }, content_type='application/json')


@PromptServer.instance.routes.get("/flowscale/output/search")
async def search_output(request):
    filename = request.query.get('filename')
    if not filename:
        return web.json_response({
            "error": "Filename query parameter is required."
        }, status=400, content_type='application/json')

    output_directory = os.path.join(os.getcwd(), "output")

    supported_extensions = [
        ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm",
        ".gif",
        ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".svg",
        ".txt", ".pdf", ".docx"
    ]
    
    search_patterns = [filename + "*" + ext for ext in supported_extensions] + [filename]
    
    file_path = None
    for search_pattern in search_patterns:
        file_paths = glob.glob(os.path.join(output_directory, "*" + search_pattern + "*"))
        if file_paths:
            file_path = file_paths[0]
            break

    if not file_path:
        return web.json_response({
            "error": "File not found."
        }, status=404, content_type='application/json')

    video_extensions = [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"]
    max_delay = 30 if any(file_path.endswith(ext) for ext in video_extensions) else 5

    if not is_file_ready(file_path, max_delay=max_delay):
        return web.json_response({
            "error": "File not ready yet."
        }, status=404, content_type='application/json')

    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = "application/octet-stream"

    try:
        with open(file_path, 'rb') as file:
            file_content = file.read()
    except Exception as e:
        return web.json_response({
            "error": str(e)
        }, status=500, content_type='application/json')

    return web.Response(body=file_content, content_type=mime_type)

# Directory listing
@PromptServer.instance.routes.get("/flowscale/output/directory")
async def fetch_output_directory(request, folder_path=None):
    output_directory = os.path.join(os.getcwd(), "output")
    
    if not os.path.exists(output_directory):
        return web.json_response({
            "error": "Output directory does not exist."
        }, status=404, content_type='application/json')
    
    try:
        directory_contents = os.listdir(output_directory)
    except Exception as e:
        return web.json_response({
            "error": str(e)
        }, status=500, content_type='application/json')
    
    return web.json_response({
        "output_directory": output_directory,
        "directory_contents": directory_contents
    }, content_type='application/json')
  
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
