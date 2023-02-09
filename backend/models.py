from datetime import datetime

from sqlmodel import SQLModel, Field, Column, DateTime, func, Integer, ForeignKey


__all__ = ["Question", "Answer", "Comment", "Vote"]


class Base(SQLModel):
    id: int | None = Field(primary_key=True)
    created_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now()))


class Post(Base):
    author: str
    body: str
    score: int = Field(default=0, sa_column_kwargs={"server_default": "0"})


class Question(Post, table=True):
    title: str
    tags: str = Field(nullable=True)


class Answer(Post, table=True):
    question_id: int = Field(sa_column=Column(Integer, ForeignKey("question.id", ondelete="CASCADE"), nullable=False))


class Comment(Post, table=True):
    # TODO type and id fields insted of question_id, answer_id
    question_id: int = Field(sa_column=Column(Integer, ForeignKey("question.id", ondelete="CASCADE")))
    answer_id: int = Field(sa_column=Column(Integer, ForeignKey("answer.id", ondelete="CASCADE")))


class Vote(Base, table=True):
    user_hash: str
    upvote: bool
    # TODO type and id fields insted of question_id, answer_id, comment_id
    question_id: int = Field(sa_column=Column(Integer, ForeignKey("question.id", ondelete="CASCADE")))
    answer_id: int = Field(sa_column=Column(Integer, ForeignKey("answer.id", ondelete="CASCADE")))
    comment_id: int = Field(sa_column=Column(Integer, ForeignKey("comment.id", ondelete="CASCADE")))
