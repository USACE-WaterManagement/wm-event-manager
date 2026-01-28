from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from cwms_batch_events.api.api import router
from cwms_batch_events.core.settings import settings

app = FastAPI(root_path=settings.root_path)

origins = r"http://localhost(:\d+)?"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
