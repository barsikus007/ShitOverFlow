from typing import Optional

from fastapi import APIRouter, Request, Query, Form, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlmodel.ext.asyncio.session import AsyncSession

from db import get_db
from utils import get_user_hash
from schema import QuestionIn, AnswerIn
from models import Question, Answer
import crud


template_router = APIRouter()
templates = Jinja2Templates(directory='../templates')


@template_router.get('/page/{page}', include_in_schema=False)
async def render_page(
        request: Request,
        page: int = Query(1, ge=1),
        db: AsyncSession = Depends(get_db),
):
    user_hash = get_user_hash(request)
    questions = await crud.get_questions(db, page)
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'user_hash': user_hash,
            'page': page,
            'questions': questions['questions'],
            'count': questions['count'],
        }
    )


@template_router.get('/', include_in_schema=False)
async def render_index(
        request: Request,
        db: AsyncSession = Depends(get_db),
):
    return await render_page(request, 1, db)


@template_router.get('/search', include_in_schema=False)
async def search_page(
        request: Request,
        q: str, page: int = 1,
        db: AsyncSession = Depends(get_db),
):
    user_hash = get_user_hash(request)
    questions = await crud.search_questions(db, q, page)
    return templates.TemplateResponse(
        'search.html',
        {
            'request': request,
            'user_hash': user_hash,
            'page': page,
            'questions': questions['questions'],
            'count': questions['count'],
            'query': q,
        }
    )


@template_router.get('/questions/ask', include_in_schema=False)
async def render_create(request: Request):
    user_hash = get_user_hash(request)
    return templates.TemplateResponse(
        'create.html',
        {
            'request': request,
            'user_hash': user_hash,
        }
    )


@template_router.post('/questions/ask', include_in_schema=False)
async def question_form(
        name: str = Form(..., min_length=2, max_length=64),
        title: str = Form(..., min_length=3, max_length=1024),
        body: str = Form(..., min_length=3, max_length=4096),
        tags: str = Form(None, min_length=1, max_length=1024),
        db: AsyncSession = Depends(get_db),
):
    question = QuestionIn(
        author=name,
        title=title,
        body=body,
        tags=tags,
    )
    res = await crud.create_question(db, Question(**question.dict()))
    return RedirectResponse(f'/questions/{res.id}', status_code=303)


@template_router.get('/questions/{question_id}', include_in_schema=False)
async def render_question(
        question_id: int, request: Request,
        page: Optional[int] = Query(1, ge=1),
        db: AsyncSession = Depends(get_db),
):
    user_hash = get_user_hash(request)
    question = await crud.get_question(db, user_hash, question_id)
    if not question:
        raise HTTPException(status_code=404)
    answers = await crud.get_answers(db, user_hash, question_id, page)
    details = {'answers_count': answers['count']}
    return templates.TemplateResponse(
        'thread.html',
        {
            'request': request,
            'user_hash': user_hash,
            'question_id': question_id,
            'question': question,
            'answers': answers['answers'],
            'details': details,
            'page': page,
        })


@template_router.post('/questions/{question_id}', include_in_schema=False)
async def post_create(
        question_id: int,
        name: str = Form(..., min_length=2, max_length=64),
        body: str = Form(..., min_length=3, max_length=4096),
        db: AsyncSession = Depends(get_db),
):
    answer = AnswerIn(
        question_id=question_id,
        author=name,
        body=body,
    )
    await crud.create_answer(db, Answer(**answer.dict()))
    return RedirectResponse(f'/questions/{question_id}', status_code=303)


@template_router.get('/about', include_in_schema=False)
async def about():
    """???"""
    return StreamingResponse(open('static/about.webm', 'rb'), media_type="video/mp4")
