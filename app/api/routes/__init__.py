from app.api.routes.run_agent import router as run_agent_router
from app.api.routes.read_image import router as read_image_router
from app.api.routes.read_video import router as read_video_router
from app.api.routes.deepfake_check import router as deepfake_check_router

__all__ = [
    run_agent_router,
    read_image_router,
    read_video_router,
    deepfake_check_router
]