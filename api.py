from server import PromptServer
from aiohttp import web
import os
import glob
import mimetypes

@PromptServer.instance.routes.get("/flowscale/output")
async def fetch_outputs(request):
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

@PromptServer.instance.routes.get("/flowscale/search")
async def search_output(request):
    filename = request.query.get('filename')
    if not filename:
        return web.json_response({
            "error": "Filename query parameter is required."
        }, status=400, content_type='application/json')

    output_directory = os.path.join(os.getcwd(), "output")
    
    search_patterns = [
        filename + "*" + ".mp4",
        filename + "*" + ".gif",
        filename + "*" + ".txt",
        filename
    ]
    
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
