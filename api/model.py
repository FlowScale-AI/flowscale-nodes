from server import PromptServer # type: ignore
import logging
from aiohttp import web
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MODELS_DIR = os.path.join(os.getcwd(), "models")

# Increase the maximum upload size limit (default is usually 1MB)
# Set to 10GB (10 * 1024 * 1024 * 1024 bytes)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024 * 1024

@PromptServer.instance.routes.get("/flowscale/model/list")
async def list_models(request):
    """
    Endpoint to list all models in the `models` folder.
    """
    try:
        # Get all items in the models directory
        model_folder = request.query.get("model_folder", "")
        all_items = os.listdir(MODELS_DIR if not model_folder else os.path.join(MODELS_DIR, model_folder))
        models = []

        for item_name in all_items:                
            item_path = os.path.join(MODELS_DIR, item_name)
            item_type = "directory" if os.path.isdir(item_path) else "file"
            
            models.append({
                "name": item_name,
                "type": item_type
            })
            
        return web.json_response(models, status=200)
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return web.json_response({"error": "Failed to list models", "details": str(e)}, status=500)
    
@PromptServer.instance.routes.post("/flowscale/model/upload")
async def upload_model(request):
    """
    Endpoint to upload a model to the `models` folder.
    """
    try:
        logger.info("Starting model upload process")
        
        # Get the content type
        content_type = request.headers.get('Content-Type', '')
        logger.debug(f"Content-Type: {content_type}")
        
        # Check if we have a multipart form
        if not content_type.startswith('multipart/form-data'):
            return web.json_response({"error": "Expected multipart/form-data"}, status=400)
            
        # Process using multipart reader directly
        reader = await request.multipart()
        
        model_name = None
        model_folder = ""
        model_file_field = None
        
        # Process each part of the multipart request
        logger.debug("Processing multipart form data parts")
        async for part in reader:
            logger.debug(f"Processing part: {part.name}")
            if part.name == 'model_name':
                model_name = await part.text()
                logger.debug(f"Got model_name: {model_name}")
            elif part.name == 'model_folder':
                model_folder = await part.text()
                logger.debug(f"Got model_folder: {model_folder}")
            elif part.name == 'model_file':
                model_file_field = part
                if model_file_field.filename:
                    logger.debug(f"Got model_file with filename: {model_file_field.filename}")
                    if not model_name:
                        model_name = model_file_field.filename
                        logger.debug(f"Using filename as model_name: {model_name}")
                break  # Once we find the file field, we can break and process it
        
        if not model_name or not model_file_field:
            logger.error("Missing model name or file in request")
            return web.json_response({"error": "Model name and file are required"}, status=400)
        
        # Ensure the model name has .safetensors extension if it's a safetensors file
        if model_file_field.filename and model_file_field.filename.endswith('.safetensors') and not model_name.endswith('.safetensors'):
            logger.debug(f"Adding .safetensors extension to model name")
            model_name = f"{model_name}.safetensors"
            logger.debug(f"Updated model name: {model_name}")
        
        # Create the directory if it doesn't exist
        target_dir = os.path.join(MODELS_DIR, model_folder)
        logger.debug(f"Target directory: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)
        
        # Save the uploaded file to the models directory
        destination_path = os.path.join(target_dir, model_name)
        logger.debug(f"Destination path: {destination_path}")
        
        # Stream the file data to disk in chunks
        size = 0
        chunk_count = 0
        chunk_size = 64 * 1024  # 64KB chunks
        
        logger.debug(f"Starting streaming file write with {chunk_size}B chunks")
        with open(destination_path, 'wb') as f:
            while True:
                chunk = await model_file_field.read_chunk(size=chunk_size)
                if not chunk:
                    break
                
                chunk_count += 1
                current_chunk_size = len(chunk)
                size += current_chunk_size
                f.write(chunk)
                
                if chunk_count % 100 == 0:
                    logger.debug(f"Wrote {chunk_count} chunks, {size} bytes so far")
                
        logger.debug(f"Completed streaming write: {chunk_count} chunks, {size} total bytes")
        
        # Verify the file was saved correctly
        if os.path.exists(destination_path):
            file_size = os.path.getsize(destination_path)
            logger.debug(f"Saved file size: {file_size} bytes")
            if size > 0 and file_size != size:
                logger.error(f"Size mismatch! Written: {size}, on disk: {file_size}")
        else:
            logger.error(f"File not found at {destination_path} after write!")
        
        logger.info(f"Model uploaded successfully to {destination_path}")
        return web.json_response({
            "message": "Model uploaded successfully",
            "path": destination_path,
            "size_bytes": size
        }, status=200)
    except Exception as e:
        logger.error(f"Error uploading model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return web.json_response({"error": "Failed to upload model", "details": str(e)}, status=500)