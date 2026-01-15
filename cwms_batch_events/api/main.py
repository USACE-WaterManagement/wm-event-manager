from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router

app = FastAPI()

origins = r"http://localhost(:\d+)?"

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
