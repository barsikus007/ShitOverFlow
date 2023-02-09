import time

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from config import settings

from api import api_router
from render import template_router
from utils import get_user_hash


app = FastAPI(
    title='ShitOverFlow official API docs',
    description='Nice API for shit site',
    version='1.0',
    default_response_class=ORJSONResponse,
)
app.mount('/static', StaticFiles(directory='../static'), name='static')
app.include_router(template_router)
app.include_router(api_router)


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-User-Secret'] = get_user_hash(request)
    response.headers['X-Process-Time'] = str(process_time)
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app", host="127.0.0.1",
        log_level="debug" if settings.DEBUG else "critical",
        debug=settings.DEBUG, reload=settings.DEBUG,
    )
