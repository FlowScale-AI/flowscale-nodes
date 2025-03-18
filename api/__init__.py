from .custom_node import register_routes
from .io import setup_io_handlers

# Register API routes
register_routes()

# Setup IO handlers
setup_io_handlers()