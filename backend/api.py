from fastapi import APIRouter, Request, Path, Query, Depends
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

import crud
from db import get_db
from schema import ResponseID, ResponseSuccess
from schema import VoteType, PostType, PostTypeQA
from schema import QuestionIn, AnswerIn, CommentIn
from schema import QuestionOut
from schema import Questions, Answers, Comments
from models import Answer, Comment, Question
from utils import get_user_hash
from config import settings


api_router = APIRouter(prefix=settings.API_V1_STR)


@api_router.get('/search/questions', response_model=Questions, tags=['question'])
async def search_questions(q: str, dbs: AsyncSession = Depends(get_db)):
    """Gets all the questions on the site."""
    return await crud.search_questions(dbs, q)


@api_router.get('/questions', response_model=Questions, tags=['question'])
async def get_questions(
        page: int | None = Query(1, ge=1),
        dbs: AsyncSession = Depends(get_db),
):
    """Gets all the questions on the site."""
    return await crud.get_questions(dbs, page)


@api_router.get('/question/{question_id}', response_model=QuestionOut, tags=['question'])
async def get_question(
        request: Request,
        question_id: int = Path(..., ge=1),
        dbs: AsyncSession = Depends(get_db),
):
    """Gets specific question from the site."""
    user_hash = get_user_hash(request)
    return await crud.get_question(dbs, user_hash, question_id)


@api_router.get('/questions/{question_id}/answers', response_model=Answers, tags=['answer'])
async def get_answers(
        request: Request,
        question_id: int = Path(..., ge=1),
        page: int | None = Query(1, ge=1),
        dbs: AsyncSession = Depends(get_db),
):
    """Gets the answers to a set of questions identified in id."""
    user_hash = get_user_hash(request)
    return await crud.get_answers(dbs, user_hash, question_id, page)


@api_router.get('/{post_type}/{post_id}/comments', response_model=Comments, tags=['comment'])
async def get_comments(
        post_type: PostTypeQA,
        post_id: int,
        request: Request,
        count: int | None = None,
        dbs: AsyncSession = Depends(get_db),
):
    """Gets the comments on a set of questions and answers."""
    user_hash = get_user_hash(request)
    return await crud.get_comments(dbs, user_hash, post_type, post_id, count)


@api_router.post('/questions/add', response_model=ResponseID, tags=['question'])
async def add_question(question: QuestionIn, dbs: AsyncSession = Depends(get_db)):
    """Create a new question."""
    return await crud.create_question(dbs, Question(**question.dict()))


@api_router.post('/questions/{question_id}/answers/add', response_model=ResponseID, tags=['answer'])
async def add_answer(
        answer: AnswerIn,
        dbs: AsyncSession = Depends(get_db),
):
    """Create a new answer on the given question."""
    return await crud.create_answer(dbs, Answer(**answer.dict()))


@api_router.post('/{post_type}/{post_id}/comments/add', response_model=ResponseID, tags=['comment'])
async def add_comment(
        post_type: PostTypeQA,
        post_id: int,
        comment: CommentIn,
        dbs: AsyncSession = Depends(get_db),
):
    """Create a new comment."""
    comment_db = Comment(**comment.dict())
    if post_type == PostTypeQA.question:
        comment_db.question_id = post_id
    elif post_type == PostTypeQA.answer:
        comment_db.answer_id = post_id
    else:
        raise ValueError
    return await crud.create_comment(dbs, comment_db)


@api_router.post('/{post_type}/{post_id}/{action}', response_model=ResponseSuccess, tags=['vote'])
async def vote(
        post_type: PostType,
        post_id: int,
        action: VoteType,
        request: Request,
        dbs: AsyncSession = Depends(get_db),
):
    """Upvote a post."""
    user_hash = get_user_hash(request)
    return {'success': await crud.set_vote(dbs, post_type.value, post_id, action, user_hash)}


@api_router.post('/{post_type}/{post_id}/{action}/undo', response_model=ResponseSuccess, tags=['vote'])
async def undo_vote(
        post_type: PostType,
        post_id: int,
        action: VoteType,
        request: Request,
        dbs: AsyncSession = Depends(get_db),
):
    """Undoes an upvote on a post."""
    user_hash = get_user_hash(request)
    return {'success': await crud.set_vote(dbs, post_type.value, post_id, action, user_hash, True)}


@api_router.patch('/{post_type}/{post_id}', response_model=ResponseSuccess, tags=['other'])
async def edit_post(
        admin_token: str,
        fields: dict[str, int | str],
        post_type: PostType = Path(...),
        post_id: int = Path(..., ge=1),
        dbs: AsyncSession = Depends(get_db),
):
    """Remove specific post from the site."""
    if admin_token != settings.SECRET_KEY:
        raise HTTPException(status_code=403, detail='Incorrect token')
    return {'success': await crud.update_post(dbs, post_type, post_id, fields)}


@api_router.delete('/{post_type}/{post_id}', response_model=ResponseSuccess, tags=['other'])
async def delete_post(
        admin_token: str,
        post_type: PostType = Path(...),
        post_id: int = Path(..., ge=1),
        dbs: AsyncSession = Depends(get_db),
):
    """Remove specific post from the site."""
    if admin_token != settings.SECRET_KEY:
        raise HTTPException(status_code=403, detail='Incorrect token')
    return {'success': await crud.delete_post(dbs, post_type, post_id)}
