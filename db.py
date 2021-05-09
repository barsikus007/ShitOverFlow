import asyncio

import asyncpg
import humanize
from models import VoteType, PostType, PostTypeQA
from models import QuestionIn, AnswerIn, CommentIn


class Database:
    """
    Database wrapper
    """

    def __init__(self, auth):
        self.auth = auth
        self.conn = None
        'postgres'
        '8XZzEQjT2C7MxZBK8XZzEQjT2C7MxZBK'

    async def create_connection(self):
        if self.conn is None:
            self.conn = await asyncpg.connect(**self.auth)
        return self.conn

    async def query_fetch(self, sql, parameters=None):
        conn = await self.create_connection()
        while True:
            try:
                if parameters is None:
                    ans = await conn.fetch(sql)
                else:
                    ans = await conn.fetch(sql, *parameters)
                ret = [dict(_) for _ in ans]
                return ret
            except Exception as e:
                if 'another operation is in progress' in str(e):
                    await asyncio.sleep(1)
                else:
                    raise e

    async def search_questions(self, q, page=1):
        """SQL search"""
        questions_1 = await self.query_fetch(
            f"SELECT * FROM questions WHERE title ILIKE '%{q}%' ORDER BY id DESC"
        )
        questions_2 = await self.query_fetch(
            f"SELECT * FROM questions WHERE body ILIKE '%{q}%' ORDER BY id DESC"
        )
        questions = [*questions_1, *questions_2]
        questions = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in questions)]
        count = len(questions)
        questions = questions[(page - 1) * 10: page * 10]
        for question in questions:
            answers_count = await self.query_fetch(
                'SELECT count(*) FROM answers WHERE question_id=$1',
                [question['id']]
            )
            question['answers_count'] = answers_count[0]['count']
        return {
            'questions': questions[:10],
            'count': count,
        }

    async def update_post(self, post_type: PostType, post_id, fields):
        """SQL update post with id"""
        query = []
        for param, value in fields.items():
            query.append(f"{param}='{value}'")
        ssq = f'UPDATE {post_type.value}s SET {", ".join(query)} WHERE id=$1 RETURNING true'
        result = await self.query_fetch(
            ssq,
            [post_id]
        )
        return result[0]['bool'] if result else False

    async def delete_post(self, post_type: PostType, post_id):
        """SQL delete post with id"""
        result = await self.query_fetch(
            f'DELETE FROM {post_type.value}s WHERE id=$1 RETURNING true',
            [post_id]
        )
        return result[0]['bool'] if result else False

    async def get_question(self, user_hash, question_id):
        """SQL get questions with offset of (page-1)*10 or 30"""
        question = await self.query_fetch(
            'SELECT * FROM questions WHERE id=$1',
            [question_id]
        )
        question = question[0] if question else []
        question_score = await self.query_fetch(
            'SELECT upvote FROM votes WHERE question_id=$1 AND user_hash=$2',
            [question_id, user_hash]
        )
        question_comments = await self.query_fetch(
            'SELECT * FROM comments WHERE question_id=$1 ORDER BY created_at FETCH NEXT 5 ROWS ONLY',
            [question['id']]
        )
        cnt_comments = await self.query_fetch(
            'SELECT count(*) FROM comments WHERE question_id=$1',
            [question['id']])
        question['score_data'] = question_score[0]['upvote'] if question_score else None
        question['comments'] = question_comments
        for comment in question_comments:
            comment_score = await self.query_fetch(
                'SELECT upvote FROM votes WHERE comment_id=$1 AND user_hash=$2',
                [comment['id'], user_hash]
            )
            comment['score_data'] = comment_score[0]['upvote'] if comment_score else None
        question['comments_count'] = cnt_comments[0]['count']
        question['human_time'] = humanize.naturaltime(question['created_at'])
        return question

    async def get_questions(self, page):
        """SQL get questions with offset of (page-1)*10 or 30"""
        questions = await self.query_fetch(
            'SELECT * FROM questions ORDER BY id DESC OFFSET $1 FETCH NEXT 10 ROWS ONLY',
            [(page-1) * 10]
        )
        for question in questions:
            answers_count = await self.query_fetch(
                'SELECT count(*) FROM answers WHERE question_id=$1',
                [question['id']]
            )
            question['answers_count'] = answers_count[0]['count']
        cnt = await self.query_fetch(
            'SELECT count(*) FROM questions',
            [])
        return {
            'questions': questions,
            'count': cnt[0]['count']
        }

    async def get_answers(self, user_hash, question_id, page):
        """SQL get answers with offset of (page-1)*10 or 30"""
        answers = await self.query_fetch(
            'SELECT * FROM answers WHERE question_id=$1 ORDER BY created_at OFFSET $2 FETCH NEXT 10 ROWS ONLY',
            [question_id, (page-1) * 10]
        )
        for answer in answers:
            answer_score = await self.query_fetch(
                'SELECT upvote FROM votes WHERE answer_id=$1 AND user_hash=$2',
                [answer['id'], user_hash]
            )
            answer_comments = await self.query_fetch(
                'SELECT * FROM comments WHERE answer_id=$1 ORDER BY created_at FETCH NEXT 5 ROWS ONLY',
                [answer['id']]
            )

            cnt_comments = await self.query_fetch(
                'SELECT count(*) FROM comments WHERE answer_id=$1',
                [answer['id']])
            answer['score_data'] = answer_score[0]['upvote'] if answer_score else None
            answer['comments'] = answer_comments
            for comment in answer_comments:
                comment_score = await self.query_fetch(
                    'SELECT upvote FROM votes WHERE comment_id=$1 AND user_hash=$2',
                    [comment['id'], user_hash]
                )
                comment['score_data'] = comment_score[0]['upvote'] if comment_score else None
            answer['comments_count'] = cnt_comments[0]['count']
            answer['human_time'] = humanize.naturaltime(answer['created_at'])
        cnt = await self.query_fetch(
            'SELECT count(*) FROM answers WHERE question_id=$1',
            [question_id])
        return {
            'answers': answers,
            'count': cnt[0]['count']
        }

    async def get_comments(self, user_hash, post_type, post_id, count=None):
        """SQL get comments by post_type and post_id with offset of (page-1)*5"""
        if post_type == PostType.question:
            post_type_id = 'question_id'
        elif post_type == PostType.answer:
            post_type_id = 'answer_id'
        else:
            raise ValueError
        sql_part = 'FETCH NEXT $2 ROWS ONLY' if count is not None else ''
        sql_list = [post_id, count] if count is not None else [post_id]
        comments = await self.query_fetch(
            f'SELECT * FROM comments WHERE {post_type_id}=$1 ORDER BY created_at {sql_part}',
            sql_list
        )
        for comment in comments:
            comment_score = await self.query_fetch(
                'SELECT upvote FROM votes WHERE comment_id=$1 AND user_hash=$2',
                [comment['id'], user_hash]
            )
            comment['score_data'] = comment_score[0]['upvote'] if comment_score else None
        cnt = await self.query_fetch(
            f'SELECT count(*) FROM comments WHERE {post_type_id}=$1',
            [post_id])
        return {
            'comments': comments,
            'count': cnt[0]['count']
        }

    async def create_question(self, question: QuestionIn):
        question_id = await self.query_fetch(
            'INSERT INTO questions(author, title, body, tags) VALUES ($1, $2, $3, $4) RETURNING id',
            [question.author, question.title, question.body, question.tags]
        )
        return question_id[0] if question_id else None

    async def create_answer(self, question_id, answer: AnswerIn):
        answer_id = await self.query_fetch(
            'INSERT INTO answers(question_id, author, body) VALUES ($1, $2, $3) RETURNING id',
            [question_id, answer.author, answer.body]
        )
        return answer_id[0] if answer_id else None

    async def create_comment(self, post_type, post_id, comment: CommentIn):
        if post_type == PostTypeQA.question:
            post_type_id = 'question_id'
        else:
            post_type_id = 'answer_id'
        comment_id = await self.query_fetch(
            f'INSERT INTO comments({post_type_id}, author, body) VALUES ($1, $2, $3) RETURNING id',
            [post_id, comment.author, comment.body]
        )
        return comment_id[0] if comment_id else None

    async def set_vote(self, post_type, post_id, action, user_hash, undo=False):
        if post_type == PostType.question:
            post_type_id = 'question_id'
        elif post_type == PostType.answer:
            post_type_id = 'answer_id'
        else:
            post_type_id = 'comment_id'
        if action == VoteType.upvote:
            action = True
        elif action == VoteType.downvote:
            action = False
        else:
            raise ValueError
        vote = await self.query_fetch(
            f'SELECT * FROM votes WHERE {post_type_id}=$1 AND user_hash=$2',
            [post_id, user_hash]
        )
        if not undo:
            if vote:
                return False
                await self.query_fetch(
                    f'UPDATE votes SET upvote=$1 WHERE id=$2',
                    [action, vote[0]['id']]
                )
                await self.query_fetch(
                    f'UPDATE {post_type_id[:-3]+"s"} SET score=score+$1 WHERE id=$2',
                    [action * 1 + (not action) * -1, post_id]
                )
                return True
            await self.query_fetch(
                f'INSERT INTO votes({post_type_id}, user_hash, upvote) VALUES ($1, $2, $3)',
                [post_id, user_hash, action]
            )
            await self.query_fetch(
                f'UPDATE {post_type_id[:-3]+"s"} SET score=score+$1 WHERE id=$2',
                [action * 1 + (not action) * -1, post_id]
            )
            return True
        else:
            if vote:
                if vote[0]['upvote'] == action:
                    await self.query_fetch(
                        f'DELETE FROM votes WHERE id=$2 AND user_hash=$1',
                        [user_hash, vote[0]['id']]
                    )
                    await self.query_fetch(
                        f'UPDATE {post_type_id[:-3] + "s"} SET score=score-$1 WHERE id=$2',
                        [action * 1 + (not action) * -1, post_id]
                    )
                    return True
            return False
