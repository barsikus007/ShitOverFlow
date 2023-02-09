from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field


base_author = Field('name', min_length=2, max_length=64)
base_body = Field('text', min_length=3, max_length=4096)


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
    author: str = base_author
    body: str = base_body


class QuestionIn(BaseModel):
    author: str = base_author
    title: str = Field('header', min_length=3, max_length=1024)
    body: str = base_body
    tags: str | None = Field('tags', min_length=1, max_length=1024)


class AnswerIn(BaseModel):
    question_id: int
    author: str = base_author
    body: str = base_body


class CommentOut(BaseModel):
    id: int = 1
    question_id: int | None = 1
    answer_id: int | None = 1
    author: str = 'name'
    body: str = 'text'
    created_at: datetime
    human_time: str | None = None
    score: int = 0
    score_data: bool | None = None


class QuestionOut(BaseModel):
    id: int = 1
    author: str = 'name'
    title: str = 'header'
    body: str = 'text'
    tags: str | None = None
    created_at: datetime
    human_time: str | None = None
    score: int = 0
    score_data: bool | None = None
    comments: list[CommentOut] | None
    comments_count: int | None
    answers_count: int | None


class AnswerOut(BaseModel):
    id: int = 1
    question_id: int = 1
    author: str = 'name'
    body: str = 'text'
    created_at: datetime
    human_time: str | None = None
    score: int = 0
    score_data: bool | None = None
    comments: list[CommentOut] = []
    comments_count: int = 10


class VoteOut(BaseModel):
    id: int = 1
    question_id: int | None = 1
    answer_id: int | None = 1
    comment_id: int | None = 1
    user_hash: str
    like: bool


class Comments(BaseModel):
    comments: list[CommentOut]
    count: int = 10


class Questions(BaseModel):
    questions: list[QuestionOut]
    count: int = 10


class Answers(BaseModel):
    answers: list[AnswerOut]
    count: int = 10
