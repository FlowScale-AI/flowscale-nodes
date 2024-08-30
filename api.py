from server import PromptServer
from aiohttp import web
import os
import glob
import mimetypes
import asyncio

root_path = os.path.dirname(os.path.abspath(__file__))
two_dirs_up = os.path.dirname(os.path.dirname(root_path))
log_files = glob.glob(os.path.join(two_dirs_up, 'comfyui*.log'))

log_files.sort(key=os.path.getmtime, reverse=True)
comfyui_file_path = log_files[0] 

async def read_last_n_lines(file_path, n):
    with open(file_path, 'rb') as f:
        f.seek(0, os.SEEK_END)
        end_position = f.tell()
        
        buffer = bytearray()
        lines = []
        
        while end_position > 0 and len(lines) < n:
            read_size = min(1024, end_position)
            
            f.seek(end_position - read_size)
            buffer.extend(f.read(read_size))
            end_position -= read_size
            
            lines_in_buffer = buffer.split(b'\n')            
            buffer = lines_in_buffer[0]            
            lines = lines_in_buffer[1:] + lines

        lines = [line.decode('utf-8') for line in lines[-n:]]

        return lines
        
@PromptServer.instance.routes.get("/flowscale/logs/stream")
async def stream_logs(request):
    response = web.StreamResponse(
        status=200, 
        reason="OK", 
        headers={
            'Content-Type': 'text/event-stream',  
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            }
        )
    await response.prepare(request)

    last_200_lines = await read_last_n_lines(comfyui_file_path, 200)
    for line in last_200_lines:
        await response.write(f"data: {line}\n\n".encode('utf-8'))
        
    async def send_logs():
        try:
            with open(comfyui_file_path, 'r') as log_file:
                log_file.seek(0, os.SEEK_END)
    
                while True:
                    line = log_file.readline()
                    if line:
                        await response.write(f"data: {line}\n\n".encode('utf-8'))
                        await response.drain()
                    else:
                        await asyncio.sleep(2)

                    if response._payload_writer.transport.is_closing():
                        print("Client disconnected")
                        break
        except asyncio.CancelledError:
            print("Stream connection was closed")

    await send_logs()
    return response

@PromptServer.instance.routes.get("/flowscale/logs/download")
async def download_logs(request):
    suggested_filename = "flowscale_comfy_log.txt"
    
    headers = {
        'Content-Disposition': f'attachment; filename="{suggested_filename}"',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    return web.FileResponse(path=comfyui_file_path, headers=headers)
    
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
