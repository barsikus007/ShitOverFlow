from datetime import datetime, timezone

import humanize
from fastapi.encoders import jsonable_encoder
from sqlmodel import select, func, desc, or_
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Question, Answer, Comment, Post, Vote
from schema import AnswerOut, CommentOut, QuestionOut, VoteType, PostType


async def prepare_comments(db: AsyncSession, user_hash, comments: list[Comment]) -> list[CommentOut]:
    comments_out = []
    for comment in comments:
        comment_out = CommentOut(**comment.dict())
        comment_score: bool | None = (await db.exec(
            select(Vote.upvote)
            .where(Vote.comment_id == comment.id, Vote.user_hash == user_hash))).first()  # type: ignore
        comment_out.score_data = comment_score
        comment_out.human_time = humanize.naturaltime(comment_out.created_at, when=datetime.now(timezone.utc))
        comments_out.append(comment_out)
    return comments_out


async def search_questions(db: AsyncSession, q, page=1):
    """SQL search"""
    per_page = 10
    questions: list[Question] = (await db.exec(
        select(Question)
            .where(or_(Question.title.ilike(f'%{q}%'), Question.body.ilike(f'%{q}%')))  # type: ignore
            .order_by(desc(Question.created_at)))).all()  # type: ignore
            # .offset((page - 1) * per_page).limit(per_page)
    count = len(questions)
    questions_out: list[QuestionOut] = []
    for question in questions[(page - 1) * per_page:per_page + (page - 1) * per_page]:
        question_out = QuestionOut(**question.dict())
        question_out.answers_count =  len((await db.execute(
            select(Answer)
                .where(Answer.question_id == question.id))).all())
        questions_out.append(question_out)
    return {
        'questions': questions_out,
        'count': count,
    }


async def get_question(db: AsyncSession, user_hash, question_id):
    question = await db.get(Question, question_id)
    if not question:
        return
    question_out = QuestionOut(**question.dict())
    question_score: bool | None = (await db.exec(
        select(Vote.upvote)
        .where(Vote.question_id == question_id, Vote.user_hash == user_hash))).first()  # type: ignore
    question_comments: list[Comment] = (await db.exec(
        select(Comment)
            .where(Comment.question_id == question_id)
            .order_by(Comment.created_at).limit(5))).all()  # type: ignore
    cnt_comments = len((await db.exec(select(Comment).where(Comment.question_id == question_id) )).all())  # type: ignore
    question_out.score_data = question_score
    question_comments_out = await prepare_comments(db, user_hash, question_comments)
    question_out.comments = question_comments_out
    question_out.comments_count = cnt_comments
    question_out.human_time = humanize.naturaltime(question_out.created_at, when=datetime.now(timezone.utc))
    return question_out


async def get_questions(db: AsyncSession, page) -> dict[str, list[QuestionOut] | int]:
    """SQL get questions with offset of (page-1)*10 or 30"""
    question_rows: list[Question] = (await db.exec(
        select(Question).order_by(desc(Question.id)).offset((page-1) * 10).limit(10))).all()  # type: ignore
    questions: list[QuestionOut] = []
    for question in question_rows:
        question_out = QuestionOut(**question.dict())
        question_out.answers_count =  len((await db.execute(
            select(Answer)
                .where(Answer.question_id == question.id))).all())
        questions.append(question_out)
    count: int = (await db.exec(
        select(func.count()).select_from(select(Question).subquery()))).one()  # type: ignore
    return {
        'questions': questions,
        'count': count,
    }


async def get_answers(db: AsyncSession, user_hash, question_id, page) -> dict[str, list[AnswerOut] | int]:
    """SQL get answers with offset of (page-1)*10 or 30"""
    answers: list[Answer] = (await db.exec(
        select(Answer)
            .where(Answer.question_id == question_id)
            .order_by(Answer.created_at)
            .offset((page-1) * 10).limit(10))).all()  # type: ignore
    answers_out: list[AnswerOut] = []
    for answer in answers:
        answer_out = AnswerOut(**answer.dict())
        answer_score: bool | None = (await db.exec(
            select(Vote.upvote)
                .where(Vote.answer_id == answer.id, Vote.user_hash == user_hash))).first()  # type: ignore
        answer_comments: list[Comment] = (await db.exec(
            select(Comment)
                .where(Comment.answer_id == answer.id)
                .order_by(Comment.created_at).limit(5))).all()  # type: ignore
        cnt_comments =  len((await db.exec(
            select(Comment)
                .where(Comment.answer_id == answer.id) )).all())  # type: ignore
        answer_out.score_data = answer_score
        print(f'{answer_comments=}')
        answer_comments_out = await prepare_comments(db, user_hash, answer_comments)
        answer_out.comments = answer_comments_out
        answer_out.comments_count = cnt_comments
        answer_out.human_time = humanize.naturaltime(answer_out.created_at, when=datetime.now(timezone.utc))
        answers_out.append(answer_out)
    count: int = (await db.exec(
        select(func.count()).select_from(select(Answer).where(Answer.question_id == question_id).subquery())  # type: ignore
    )).one()  # type: ignore
    return {
        'answers': answers_out,
        'count': count,
    }


async def get_comments(db: AsyncSession, user_hash, post_type, post_id, limit=None):
    """SQL get comments by post_type and post_id with offset of (page-1)*5"""
    if post_type == PostType.question:
        post_type_type = Comment.question_id
    elif post_type == PostType.answer:
        post_type_type = Comment.answer_id
    else:
        raise ValueError
    comments: list[Comment] = (await db.exec(
        select(Comment)
            .where(post_type_type == post_id)
            .order_by(Comment.created_at)
            .limit(limit))).all()  # type: ignore
    comments_out = await prepare_comments(db, user_hash, comments)
    count: int = (await db.exec(
        select(func.count()).select_from(select(Comment).where(post_type_type == post_id).subquery())  # type: ignore
    )).one()  # type: ignore
    return {
        'comments': comments_out,
        'count': count,
    }


async def create_question(db: AsyncSession, question: Question) -> Question:
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


async def create_answer(db: AsyncSession, answer: Answer) -> Answer:
    db.add(answer)
    await db.commit()
    await db.refresh(answer)
    return answer


async def create_comment(db: AsyncSession, comment: Comment):
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def update_post(db: AsyncSession, post_type: PostType, post_id: int, fields: dict):
    """SQL update post with id"""
    if post_type == PostType.question:
        obj_db = await db.get(Question, post_id)
    elif post_type == PostType.answer:
        obj_db = await db.get(Answer, post_id)  # type: ignore
    elif post_type == PostType.comment:
        obj_db = await db.get(Comment, post_id)  # type: ignore
    else:
        raise ValueError('Unknown post type')
    obj_data = jsonable_encoder(obj_db)
    for field in obj_data:
        if field in fields:
            setattr(obj_db, field, fields[field])
    db.add(obj_db)
    await db.commit()
    await db.refresh(obj_db)
    return obj_db


async def delete_post(db: AsyncSession, post_type: PostType, post_id: int):
    """SQL delete post with id"""
    if post_type == PostType.question:
        obj = await db.get(Question, post_id)
    elif post_type == PostType.answer:
        obj = await db.get(Answer, post_id)  # type: ignore
    elif post_type == PostType.comment:
        obj = await db.get(Comment, post_id)  # type: ignore
    else:
        raise ValueError('Unknown post type')
    if obj:
        await db.delete(obj)
        await db.commit()
    return bool(obj)


async def set_vote(db: AsyncSession, post_type, post_id, action, user_hash, undo=False):
    if post_type == PostType.question:
        post_type_id = 'question_id'
        post_type_type = Vote.question_id
        obj_type = Question
    elif post_type == PostType.answer:
        post_type_id = 'answer_id'
        post_type_type = Vote.answer_id
        obj_type = Answer  # type: ignore
    elif post_type == PostType.comment:
        post_type_id = 'comment_id'
        post_type_type = Vote.comment_id
        obj_type = Comment  # type: ignore
    else:
        raise ValueError

    if action == VoteType.upvote:
        action = True
    elif action == VoteType.downvote:
        action = False
    else:
        raise ValueError

    increment = action * 1 + (not action) * -1

    vote: Vote | None = (await db.exec(
        select(Vote)
            .where(post_type_type == post_id, Vote.user_hash == user_hash))).one_or_none()  # type: ignore
    if not vote:
        if undo:
            return False
        vote = Vote(
            user_hash=user_hash,
            upvote=action,
            **{post_type_id: post_id})
        post: Post = await db.get(obj_type, post_id)  # type: ignore
        post.score += increment
        db.add(vote)
        db.add(post)
        await db.commit()
        return True

    if not undo:
        return False
    if vote.upvote == action:
        await db.delete(vote)
        post: Post = await db.get(obj_type, post_id)  # type: ignore
        post.score -= increment
        db.add(post)
        await db.commit()
        return True
    return False
