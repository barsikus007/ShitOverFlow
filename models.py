from enum import Enum
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field


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


class CommentIn(BaseModel):
    author: str = Field('name', min_length=2, max_length=64)
    body: str = Field('text', min_length=3)


class QuestionIn(BaseModel):
    author: str = Field('name', min_length=2, max_length=64)
    title: str = Field('header')
    body: str = Field('text', min_length=3)
    tags: Optional[str] = None


class AnswerIn(BaseModel):
    author: str = Field('name', min_length=2, max_length=64)
    body: str = Field('text', min_length=3)


class CommentOut(BaseModel):
    id: int = 1
    question_id: Optional[int] = 1
    answer_id: Optional[int] = 1
    author: str = 'name'
    body: str = 'text'
    created_at: datetime
    score: int = 0
    score_data: Optional[bool] = None


class QuestionOut(BaseModel):
    id: int = 1
    author: str = 'name'
    title: str = 'header'
    body: str = 'text'
    tags: Optional[str] = None
    created_at: datetime
    score: int = 0
    score_data: Optional[bool] = None
    comments: Optional[List[CommentOut]]
    comments_count: Optional[int]


class AnswerOut(BaseModel):
    id: int = 1
    question_id: int = 1
    author: str = 'name'
    body: str = 'text'
    created_at: datetime
    score: int = 0
    score_data: Optional[bool] = None
    comments: List[CommentOut]
    comments_count: int = 10


class VoteOut(BaseModel):
    id: int = 1
    question_id: Optional[int] = 1
    answer_id: Optional[int] = 1
    comment_id: Optional[int] = 1
    user_hash: str
    like: bool


class Comments(BaseModel):
    comments: List[CommentOut]
    count: int = 10


class Questions(BaseModel):
    questions: List[QuestionOut]
    count: int = 10


class Answers(BaseModel):
    answers: List[AnswerOut]
    count: int = 10
