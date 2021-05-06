import asyncio

import asyncpg
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

    async def search_questions(self, q):
        """SQL search"""
        res = await self.query_fetch(
            f"SELECT * FROM questions WHERE title ILIKE '%{q}%' ORDER BY id DESC FETCH NEXT 10 ROWS ONLY",
            []
        )
        return res if res else None

    async def get_question(self, user_hash, question_id):
        """SQL get questions with offset of (page-1)*10 or 30"""
        res = await self.query_fetch(
            'SELECT * FROM questions WHERE id=$1',
            [question_id]
        )
        for result in res:
            res_2 = await self.query_fetch(
                'SELECT upvote FROM votes WHERE question_id=$1 AND user_hash=$2',
                [question_id, user_hash]
            )
            res_3 = await self.query_fetch(
                'SELECT * FROM comments WHERE question_id=$1',
                [result['id']]
            )
            result['score_data'] = res_2[0]['upvote'] if res_2 else None
            result['comments'] = res_3

        return res[0] if res else None

    async def get_questions(self, page):
        """SQL get questions with offset of (page-1)*10 or 30"""
        res = await self.query_fetch(
            'SELECT * FROM questions ORDER BY id DESC OFFSET $1 FETCH NEXT 10 ROWS ONLY',
            [(page-1) * 10]
        )
        for result in res:
            res_2 = await self.query_fetch(
                'SELECT * FROM answers WHERE question_id=$1',
                [result['id']]
            )
            result['answers_count'] = len(res_2)
        return res if res else None

    async def get_answers(self, user_hash, question_id, page):
        """SQL get answers with offset of (page-1)*10 or 30"""
        res = await self.query_fetch(
            'SELECT * FROM answers WHERE question_id=$1 ORDER BY created_at OFFSET $2 FETCH NEXT 10 ROWS ONLY',
            [question_id, (page-1) * 10]
        )
        for result in res:
            res_2 = await self.query_fetch(
                'SELECT upvote FROM votes WHERE answer_id=$1 AND user_hash=$2',
                [result['id'], user_hash]
            )
            res_3 = await self.query_fetch(
                'SELECT * FROM comments WHERE question_id=$1',
                [result['id']]
            )
            result['score_data'] = res_2[0]['upvote'] if res_2 else None
            result['comments'] = res_3
        return res

    async def get_comments(self, user_hash, post_type, post_id, page):
        """SQL get comments by post_type and post_id with offset of (page-1)*5"""
        if post_type == PostType.question:
            post_type_id = 'question_id'
        elif post_type == PostType.answer:
            post_type_id = 'answer_id'
        else:
            raise ValueError
        res = await self.query_fetch(
            f'SELECT * FROM comments WHERE {post_type_id}=$1 ORDER BY id OFFSET $2 FETCH NEXT 5 ROWS ONLY',
            [post_id, (page-1) * 10]
        )
        # print(res)
        for result in res:
            res_2 = await self.query_fetch(
                'SELECT upvote FROM votes WHERE comment_id=$1 AND user_hash=$2',
                [result['id'], user_hash]
            )
            result['score_data'] = res_2[0]['upvote'] if res_2 else None
        return res if res else None

    async def create_question(self, question: QuestionIn):
        res = await self.query_fetch(
            'INSERT INTO questions(author, title, body, tags) VALUES ($1, $2, $3, $4) RETURNING ID',
            [question.author, question.title, question.body, question.tags]
        )
        return res[0] if res else None

    async def create_answer(self, question_id, answer: AnswerIn):
        res = await self.query_fetch(
            'INSERT INTO answers(question_id, author, body) VALUES ($1, $2, $3) RETURNING ID',
            [question_id, answer.author, answer.body]
        )
        return res[0] if res else None

    async def create_comment(self, post_type, post_id, comment: CommentIn):
        if post_type == PostTypeQA.question:
            post_type_id = 'question_id'
        else:
            post_type_id = 'answer_id'
        res = await self.query_fetch(
            f'INSERT INTO comments({post_type_id}, author, body) VALUES ($1, $2, $3) RETURNING ID',
            [post_id, comment.author, comment.body]
        )
        return res[0] if res else None

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
        res = await self.query_fetch(
            f'SELECT * FROM votes WHERE {post_type_id}=$1 AND user_hash=$2',
            [post_id, user_hash]
        )
        if not undo:
            if res:
                if res[0]['upvote'] == action:
                    return False
                await self.query_fetch(
                    f'UPDATE votes SET upvote=$1 WHERE id=$2',
                    [action, res[0]['id']]
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
            if res:
                if res[0]['upvote'] == action:
                    await self.query_fetch(
                        f'DELETE FROM votes WHERE user_hash=$1',
                        [user_hash]
                    )
                    await self.query_fetch(
                        f'UPDATE {post_type_id[:-3] + "s"} SET score=score-$1 WHERE id=$2',
                        [action * 1 + (not action) * -1, post_id]
                    )
                    return True
            return False
