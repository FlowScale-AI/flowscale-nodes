import asyncio
import glob
import logging
import os

import aiofiles
from aiohttp import web
from server import PromptServer  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_most_recent_log_file():
    root_path = os.path.dirname(os.path.abspath(__file__))
    three_dirs_up = os.path.dirname(os.path.dirname(os.path.dirname(root_path)))

    comfyui_logs_main = glob.glob(os.path.join(three_dirs_up, "comfyui*.log"))
    comfy_logs_user_dir = glob.glob(os.path.join(three_dirs_up, "user", "comfyui*.log"))

    log_files = comfyui_logs_main + comfy_logs_user_dir

    log_files.sort(key=os.path.getmtime, reverse=True)
    return log_files[0] if log_files else os.path.join(three_dirs_up, "comfyui.log")


@PromptServer.instance.routes.get("/flowscale/log/download")
async def download_logs(request):
    comfyui_file_path = get_most_recent_log_file()
    if not os.path.exists(comfyui_file_path):
        return web.json_response(
            {"error": "Log file does not exist."}, status=404, content_type="application/json"
        )

    suggested_filename = "flowscale_comfy_log.txt"

    headers = {
        "Content-Disposition": f'attachment; filename="{suggested_filename}"',
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    return web.FileResponse(path=comfyui_file_path, headers=headers)


@PromptServer.instance.routes.get("/flowscale/log/stream")
async def stream_logs(request):
    comfyui_file_path = get_most_recent_log_file()
    if not os.path.exists(comfyui_file_path):
        return web.json_response(
            {"error": "Log file does not exist."}, status=404, content_type="application/json"
        )

    last_event_id = request.headers.get("Last-Event-ID", None)
    logger.info(f"Last Event ID: {last_event_id}")

    response = web.StreamResponse(
        status=200,
        reason="OK",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Last-Event-ID",
        },
    )
    await response.prepare(request)

    await response.write(b"retry: 10000\n\n")

    line_count = 200
    if last_event_id and last_event_id.isdigit():
        line_count = int(last_event_id)

    last_n_lines = await read_last_n_lines(comfyui_file_path, line_count)
    for i, line in enumerate(last_n_lines):
        event_id = i + 1
        await response.write(f"id: {event_id}\ndata: {line}\n\n".encode())

    async def send_logs(comfyui_file_path, response, event_counter=1):
        try:
            async with aiofiles.open(comfyui_file_path) as log_file:
                await log_file.seek(0, os.SEEK_END)

                while True:
                    line = await log_file.readline()
                    if line:
                        await response.write(f"id: {event_counter}\ndata: {line}\n\n".encode())
                        await response.drain()
                        event_counter += 1
                    else:
                        await asyncio.sleep(1)

                    if response.task is None or response.task.done():
                        logger.info("Client disconnected")
                        break

        except ConnectionResetError:
            logger.error("[ERROR] Connection was reset by the client")
        except asyncio.CancelledError:
            logger.error("[ERROR] Stream connection was closed")
        except asyncio.TimeoutError:
            logger.error("[ERROR] Stream connection timed out")

    await send_logs(comfyui_file_path, response)
    return response


async def read_last_n_lines(file_path, n):
    if not os.path.exists(file_path):
        return []
    lines = []
    try:
        with open(file_path, "rb") as f:
            f.seek(0, os.SEEK_END)
            end_position = f.tell()

            buffer = bytearray()

            while end_position > 0 and len(lines) < n:
                read_size = min(1024, end_position)

                f.seek(end_position - read_size)
                buffer = f.read(read_size) + buffer
                end_position -= read_size

                lines = buffer.split(b"\n")

            lines = [line.decode("utf-8", errors="ignore") for line in lines[-n:]]
    except Exception as e:
        logger.error(f"Error reading last {n} lines: {e}")
    return lines
