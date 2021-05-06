from enum import Enum
from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class ResponseID(BaseModel):
    id: int


class ResponseSuccess(BaseModel):
    success: bool


class PostTypeQA(str, Enum):
    question = "question"
    answer = "answer"


class PostType(str, Enum):
    question = "question"
    answer = "answer"
    comment = "comment"


class VoteType(str, Enum):
    upvote = "upvote"
    downvote = "downvote"


class QuestionIn(BaseModel):
    author: str
    title: str
    body: str
    tags: Optional[str] = None


class AnswerIn(BaseModel):
    author: str
    body: str


class CommentIn(BaseModel):
    author: str
    body: str


class QuestionOut(BaseModel):
    id: int
    author: str
    title: str
    body: str
    tags: Optional[str] = None
    created_at: datetime
    score: int
    score_data: Optional[bool] = None


class AnswerOut(BaseModel):
    id: int
    question_id: int
    author: str
    body: str
    created_at: datetime
    score: int
    score_data: Optional[bool] = None


class CommentOut(BaseModel):
    id: int
    question_id: Optional[int]
    answer_id: Optional[int]
    author: str
    body: str
    created_at: datetime
    score: int
    score_data: Optional[bool] = None


class VoteOut(BaseModel):
    id: int
    question_id: Optional[int]
    answer_id: Optional[int]
    comment_id: Optional[int]
    user_hash: str
    like: bool
