"""endpoints.py"""

from io import BytesIO
from contextlib import asynccontextmanager
from typing import Annotated
import asyncio

from dotenv import load_dotenv

import uvloop
from hypercorn.asyncio import serve
from hypercorn.config import Config

from fastapi import (
    FastAPI,
    BackgroundTasks,
    Request,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from chatbot import Chatbot
from speech_utils import recognize, synthesize

from jwt_auth_utils import require_jwt_authentication

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Defines startup and shutdown logic"""
    app.bot = await Chatbot().chatbot()
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")
# for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
@require_jwt_authentication
async def read_health(request: Request):
    """health check api"""
    return {"status": "healthy"}


@app.get("/")
async def home():
    """login and home page"""
    return FileResponse("dist/index.html")


@app.post("/api/converse")
@require_jwt_authentication
async def converse(
    request: Request,
    user_text: Annotated[str | None, Form()] = None,
    sample_rate_hertz: Annotated[int | None, Form()] = None,
    audio_file: Annotated[UploadFile | None, File()] = None,
    background_tasks: BackgroundTasks = BaseException(),
):
    """Accepts user speech as an audio file, returns chatbot response as an audio file"""
    # speech to text
    if not user_text:
        user_text = await audio_file.read()
        user_text = await recognize(
            spoken_content=user_text,
            sample_rate_hertz=sample_rate_hertz,
            mime_type=audio_file.content_type,
        )

    # chat bot response
    bot_text = await app.bot.handle_question(user_id=request.uid, text=user_text)

    # update cache
    background_tasks.add_task(
        app.bot.store_interaction, *(request.uid, user_text, bot_text)
    )

    # text to speech
    audio_bytes = await synthesize(text=bot_text)

    # return speech audio
    def iter_audio():
        """audio bytes generator for async response"""
        yield from BytesIO(audio_bytes)

    return StreamingResponse(
        iter_audio(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=audio.mp3"},
    )


if __name__ == "__main__":
    config = Config()
    config.bind = ["0.0.0.0:8080"]
    uvloop.install()
    asyncio.run(serve(app, config))
