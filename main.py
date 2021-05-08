import time
from hashlib import md5
from typing import Optional, List, Dict

from fastapi import FastAPI, Request, Path, Query, Form
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from config import DB_AUTH
from db import Database as Db
from models import ResponseID, ResponseSuccess
from models import VoteType, PostType, PostTypeQA
from models import QuestionIn, AnswerIn, CommentIn
from models import QuestionOut, AnswerOut, CommentOut
from models import Questions, Answers, Comments

db = Db(DB_AUTH)

app = FastAPI(
    title='ShitOverFlow official API docs',
    version='1.0',
    description='Nice API for shit site'
)

app.mount('/static', StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory='templates')


def get_user_hash(request: Request):
    user_agent = request.headers.get('user-agent')
    if not user_agent:
        raise HTTPException(status_code=403, detail='Invalid user agent')
    user_hash = md5(
        f'{request.client.host}{user_agent}'.encode()
    ).hexdigest()
    return user_hash


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-User-Secret'] = get_user_hash(request)
    response.headers['X-Process-Time'] = str(process_time)
    return response


@app.get('/', include_in_schema=False)
async def render_index(request: Request):
    user_hash = get_user_hash(request)
    questions = await db.get_questions(1)
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request,
            'user_hash': user_hash,
            'page': 1,
            'questions': questions['questions'],
            'count': questions['count'],
        }
    )


@app.get('/page/{page}', include_in_schema=False)
async def render_page(request: Request, page: int):
    user_hash = get_user_hash(request)
    questions = await db.get_questions(page)
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


@app.get('/search', include_in_schema=False)
async def search_page(request: Request, q: str, page: Optional[int] = 1):
    """Gets all the questions on the site."""
    user_hash = get_user_hash(request)
    questions = await db.search_questions(q, page)
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


@app.get('/questions/ask', include_in_schema=False)
async def render_create(request: Request):
    user_hash = get_user_hash(request)
    return templates.TemplateResponse(
        'create.html',
        {
            'request': request,
            'user_hash': user_hash,
        }
    )


@app.post('/questions/ask', include_in_schema=False)
async def post_create(
        name: str = Form(..., min_length=2, max_length=64),
        title: str = Form(..., min_length=3),
        body: str = Form(..., min_length=3),
        tags: str = Form(None, min_length=1)
):
    question = QuestionIn()
    question.author = name
    question.title = title
    question.body = body
    question.tags = tags
    res = await db.create_question(question)
    return RedirectResponse(f'/questions/{res["id"]}', status_code=303)


@app.get('/questions/{question_id}', include_in_schema=False)
async def render_question(question_id: int, request: Request):
    user_hash = get_user_hash(request)
    question = await db.get_question(user_hash, question_id)
    if not question:
        raise HTTPException(status_code=404)
    answers = await db.get_answers(user_hash, question_id, 1)
    comments = await db.get_comments(user_hash, PostType.question, question_id, 1)
    details = {'answers_count': answers['count']}
    return templates.TemplateResponse(
        'thread.html',
        {
            'request': request,
            'user_hash': user_hash,
            'question_id': question_id,
            'question': question,
            'answers': answers['answers'],
            'comments': comments,
            'details': details,
        })


@app.post('/questions/{question_id}', include_in_schema=False)
async def post_create(
        question_id: int,
        name: str = Form(..., min_length=2, max_length=64),
        body: str = Form(..., min_length=3)
):
    answer = AnswerIn()
    answer.author = name
    answer.body = body
    await db.create_answer(question_id, answer)
    return RedirectResponse(f'/questions/{question_id}', status_code=303)


@app.get('/api/v1/search/questions', response_model=List[QuestionOut], tags=['question'])
async def search_questions(q: str):
    """Gets all the questions on the site."""
    return await db.search_questions(q)


@app.get('/api/v1/questions', response_model=Questions, tags=['question'])
async def get_questions(page: Optional[int] = Query(1, ge=1)):
    """Gets all the questions on the site."""
    return await db.get_questions(page)


@app.get('/api/v1/question/{question_id}', response_model=QuestionOut, tags=['question'])
async def get_question(
        request: Request,
        question_id: int = Path(..., ge=1),
):
    """Gets specific question from the site."""
    user_hash = get_user_hash(request)
    return await db.get_question(user_hash, question_id)


@app.get('/api/v1/questions/{question_id}/answers', response_model=Answers, tags=['answer'])
async def get_answers(
        request: Request,
        question_id: int = Path(..., ge=1),
        page: Optional[int] = Query(1, ge=1)
):
    """Gets the answers to a set of questions identified in id."""
    user_hash = get_user_hash(request)
    return await db.get_answers(user_hash, question_id, page)


@app.get('/api/v1/{post_type}/{post_id}/comments', response_model=Comments, tags=['comment'])
async def get_comments(post_type: PostTypeQA, post_id: int, request: Request, page: Optional[int] = 1):
    """Gets the comments on a set of questions and answers."""
    user_hash = get_user_hash(request)
    return await db.get_comments(user_hash, post_type, post_id, page)


@app.post('/api/v1/questions/add', response_model=ResponseID, tags=['question'])
async def add_question(question: QuestionIn):
    """Create a new question."""
    return await db.create_question(question)


@app.post('/api/v1/questions/{question_id}/answers/add', response_model=ResponseID, tags=['answer'])
async def add_answer(question_id: int, answer: AnswerIn):
    """Create a new answer on the given question."""
    return await db.create_answer(question_id, answer)


@app.post('/api/v1/{post_type}/{post_id}/comments/add', response_model=ResponseID, tags=['comment'])
async def add_comment(post_type: PostTypeQA, post_id: int, comment: CommentIn):
    """Create a new comment."""
    return await db.create_comment(post_type, post_id, comment)


@app.post('/api/v1/{post_type}/{post_id}/{action}', response_model=ResponseSuccess, tags=['vote'])
async def vote(post_type: PostType, post_id: int, action: VoteType, request: Request):
    """Upvotes an post."""
    user_hash = get_user_hash(request)
    return {'success': await db.set_vote(post_type.value, post_id, action, user_hash)}


@app.post('/api/v1/{post_type}/{post_id}/{action}/undo', response_model=ResponseSuccess, tags=['vote'])
async def undo_vote(post_type: PostType, post_id: int, action: VoteType, request: Request):
    """Undoes an upvote on an post."""
    user_hash = get_user_hash(request)
    return {'success': await db.set_vote(post_type.value, post_id, action, user_hash, True)}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=80, reload=True)
