from fastapi import APIRouter

from app.api.routes import (
    runtime,
    admin,
    video_folder,
    train_job,
    predict_job,
    jobs_common,
    prediction,
    weights,
)
from app.api.routes import settings_page

api_router = APIRouter()


@api_router.get("/ping")
def route_ping():
    return {"message": "pong"}


api_router.include_router(train_job.router, prefix="/train_job")
api_router.include_router(predict_job.router, prefix="/predict_job")
api_router.include_router(jobs_common.router, prefix="/jobs_common")
api_router.include_router(video_folder.router, prefix="/video_folder")

api_router.include_router(runtime.router, prefix="/runtime")
api_router.include_router(prediction.router, prefix="/prediction")
api_router.include_router(weights.router, prefix="/weights")

api_router.include_router(settings_page.router, prefix="/settings_page")

api_router.include_router(admin.router, prefix="/admin")
