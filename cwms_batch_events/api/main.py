import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cwms_batch_events.api.routers import health, internal, jobs, scripts, users
from cwms_batch_events.core.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)

app = FastAPI(root_path=settings.root_path)


origins = r"http://localhost(:\d+)?"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(internal.router)
app.include_router(jobs.router)
app.include_router(scripts.router)
app.include_router(users.router)
