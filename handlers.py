from datetime import datetime
from datetime import timedelta
import random
from typing import Optional

from fastapi import APIRouter
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from common.consts import FIRST_DATE
from logic import CacheSecretLogic
from logic import EasterEggLogic
from logic import VectorLogic

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_date(delta: timedelta):
    return datetime.utcnow().date() - delta


def get_logics(app: FastAPI, delta: timedelta = timedelta()):
    delta += app.state.days_delta
    date = get_date(delta)
    logic = VectorLogic(app.state.mongo, date)
    secret = logic.secret_logic.get_secret()
    cache_logic = CacheSecretLogic(
        app.state.mongo, app.state.redis, secret=secret, dt=date
    )
    return logic, cache_logic


def render(name: str, request, **kwargs):
    kwargs['js_version'] = request.app.state.js_version
    kwargs['request'] = request
    kwargs['enumerate'] = enumerate
    return templates.TemplateResponse(
        name,
        context=kwargs
    )


class DistanceResponse(BaseModel):
    similarity: Optional[float]
    distance: int
    egg: Optional[str] = None


@router.get("/health")
async def health():
    return {"message": "Healthy!"}


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index(request: Request):
    logic, cache_logic = get_logics(app=request.app)
    cache = await cache_logic.cache
    closest1 = await logic.get_similarity(cache[-2])
    closest10 = await logic.get_similarity(cache[-12])
    closest1000 = await logic.get_similarity(cache[0])

    date = get_date(delta=request.app.state.days_delta)
    number = (date - FIRST_DATE).days + 1

    yestersecret = await VectorLogic(
        mongo=request.app.state.mongo, dt=date - timedelta(days=1)
    ).secret_logic.get_secret()

    quotes = request.app.state.quotes
    quote = random.choices(quotes, weights=[0.5] + [0.5 / (len(quotes) - 1)] * (len(quotes) - 1))[0]

    return render(
        name='index.html',
        request=request,
        number=number,
        closest1=closest1,
        closest10=closest10,
        closest1000=closest1000,
        yesterdays_secret=yestersecret,
        quote=quote
    )


@router.get("/api/distance")
async def distance(word: str, request: Request) -> DistanceResponse:
    word = word.replace("'", "")
    if egg := EasterEggLogic.get_easter_egg(word):
        reply = DistanceResponse(similarity=99.99,
                                 distance=-1,
                                 egg=egg)

    else:
        logic, cache_logic = get_logics(app=request.app)
        sim = await logic.get_similarity(word)
        cache_score = await cache_logic.get_cache_score(word)
        reply = DistanceResponse(
            similarity=sim,
            distance=cache_score
        )
    return reply


@router.get("/yesterday-top-1000", response_class=HTMLResponse, include_in_schema=False)
async def yesterday_top(request: Request):
    # logic, cache_logic = get_logics(app=request.app, delta=timedelta(days=1))
    # cache = await cache_logic.cache
    # yesterday_sims = await logic.get_similarities(cache)
    return render(
        name='closest1000.html',
        request=request,
        # yesterday=sorted(yesterday_sims.items(), key=lambda ws: ws[1], reverse=True)
        yesterday=(["נראה שהמילים הקרובות מעצבנות יותר מדי אנשים, אז העמוד הוסר", 0],),
    )


@router.get("/secrets", response_class=HTMLResponse)
async def secrets(request: Request, api_key: Optional[str] = None):
    logic, _ = get_logics(app=request.app)
    all_secrets = await logic.secret_logic.get_all_secrets()
    if api_key != request.app.state.api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    return render(
        name='all_secrets.html',
        request=request,
        secrets=sorted(all_secrets, key=lambda ws: ws[1], reverse=True),
    )


@router.get("/faq", response_class=HTMLResponse, include_in_schema=False)
async def faq(request: Request):
    _, cache_logic = get_logics(app=request.app, delta=timedelta(days=1))
    cache = await cache_logic.cache
    return render(
        name='faq.html',
        request=request,
        # yesterday=cache[-11:]
        yesterday=[],
    )


@router.get("/videos", response_class=HTMLResponse, include_in_schema=False)
async def videos(request: Request):
    return render(
        name='videos.html',
        request=request,
        videos=request.app.state.videos
    )
