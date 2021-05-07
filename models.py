from enum import Enum
from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class ResponseID(BaseModel):
    id: int


class ResponseSuccess(BaseModel):
    success: bool


class PostTypeQA(str, Enum):
    question = 'question'
    answer = 'answer'


class PostType(str, Enum):
    question = 'question'
    answer = 'answer'
    comment = 'comment'


class VoteType(str, Enum):
    upvote = 'upvote'
    downvote = 'downvote'


class QuestionIn(BaseModel):
    author: str = 'name'
    title: str = 'header'
    body: str = 'text'
    tags: Optional[str] = None


class AnswerIn(BaseModel):
    author: str = 'name'
    body: str = 'text'


class CommentIn(BaseModel):
    author: str = 'name'
    body: str = 'text'


class QuestionOut(BaseModel):
    id: int = 1
    author: str = 'name'
    title: str = 'header'
    body: str = 'text'
    tags: Optional[str] = None
    created_at: datetime
    score: int = 0
    score_data: Optional[bool] = None


class AnswerOut(BaseModel):
    id: int = 1
    question_id: int = 1
    author: str = 'name'
    body: str = 'text'
    created_at: datetime
    score: int = 0
    score_data: Optional[bool] = None


class CommentOut(BaseModel):
    id: int = 1
    question_id: Optional[int] = 1
    answer_id: Optional[int] = 1
    author: str = 'name'
    body: str = 'text'
    created_at: datetime
    score: int = 0
    score_data: Optional[bool] = None


class VoteOut(BaseModel):
    id: int = 1
    question_id: Optional[int] = 1
    answer_id: Optional[int] = 1
    comment_id: Optional[int] = 1
    user_hash: str
    like: bool
