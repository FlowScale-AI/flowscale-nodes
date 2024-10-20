import time
from server import PromptServer # type: ignore
from .. import logger
from aiohttp import web
import os
import glob
import mimetypes

logger.info("Loading output nodes...")

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