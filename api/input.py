from server import PromptServer # type: ignore
from .. import logger
from aiohttp import web
import os
import re
import aiofiles

logger.info("Loading input nodes...")

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
