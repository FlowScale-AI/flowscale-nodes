from server import PromptServer # type: ignore
import asyncio
from aiohttp import web
import logging
import os
import glob
import aiofiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_most_recent_log_file():
    root_path = os.path.dirname(os.path.abspath(__file__))
    two_dirs_up = os.path.dirname(os.path.dirname(root_path))

    print("two_dirs_up", two_dirs_up)
    comfyui_logs_main = glob.glob(os.path.join(two_dirs_up, 'comfyui*.log'))
    comfy_logs_user_dir = glob.glob(os.path.join(two_dirs_up, 'user', 'comfyui*.log'))

    print("user_path", os.path.join(two_dirs_up, 'user'))
    print("comfyui_logs_main", comfyui_logs_main)
    print("comfy_logs_user_dir", comfy_logs_user_dir)

    log_files = comfyui_logs_main + comfy_logs_user_dir
    print(log_files)

    log_files.sort(key=os.path.getmtime, reverse=True)
    return log_files[0] if log_files else os.path.join(two_dirs_up, 'comfyui.log')
        
@PromptServer.instance.routes.get("/flowscale/log/download")
async def download_logs(request):
    comfyui_file_path = get_most_recent_log_file()
    if not os.path.exists(comfyui_file_path):
        return web.json_response({
            "error": "Log file does not exist."
        }, status=404, content_type='application/json')

    suggested_filename = "flowscale_comfy_log.txt"
    
    headers = {
        'Content-Disposition': f'attachment; filename="{suggested_filename}"',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    return web.FileResponse(path=comfyui_file_path, headers=headers)
        

@PromptServer.instance.routes.get("/flowscale/log/stream")
async def stream_logs(request):
    comfyui_file_path = get_most_recent_log_file()
    if not os.path.exists(comfyui_file_path):
        return web.json_response({
            "error": "Log file does not exist."
        }, status=404, content_type='application/json')

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
            async with aiofiles.open(comfyui_file_path, 'r') as log_file:
                await log_file.seek(0, os.SEEK_END)
    
                while True:
                    line = await log_file.readline()
                    if line:
                        await response.write(f"data: {line}\n\n".encode('utf-8'))
                        await response.drain()
                    else:
                        await asyncio.sleep(2)
                    
                    if response.task is None or response.task.done():
                        logger.info("Client disconnected")
                        break

        except ConnectionResetError:
            logger.error("[ERROR] Connection was reset by the client")
        except asyncio.CancelledError:
            logger.error("[ERROR] Stream connection was closed")
        except asyncio.TimeoutError:
            logger.error("[ERROR] Stream connection timed out")

    await send_logs()
    return response

async def read_last_n_lines(file_path, n):
    if not os.path.exists(file_path):
        return []
    lines = []
    try:
        with open(file_path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            end_position = f.tell()
            
            buffer = bytearray()
            
            while end_position > 0 and len(lines) < n:
                read_size = min(1024, end_position)
                
                f.seek(end_position - read_size)
                buffer = f.read(read_size) + buffer
                end_position -= read_size
                
                lines = buffer.split(b'\n')

            lines = [line.decode('utf-8', errors='ignore') for line in lines[-n:]]
    except Exception as e:
        logger.error(f"Error reading last {n} lines: {e}")
    return lines