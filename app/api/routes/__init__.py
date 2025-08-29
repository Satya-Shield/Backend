from app.api.routes.run_agent import router as run_agent_router
from app.api.routes.read_image import router as read_image_router

__all__ = [
    run_agent_router,
    read_image_router
]