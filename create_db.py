import asyncio

import asyncpg

from config import DB_AUTH


async def connect_or_create(args):
    try:
        conn = await asyncpg.connect(**args)
    except asyncpg.exceptions.ConnectionDoesNotExistError or asyncpg.InvalidCatalogNameError:
        sys_conn = await asyncpg.connect(
            database='template1',
            user=args['user'],
            host=args['host'],
            port=args['port'],
            password=args['password'],
        )
        user = args['user']
        database = args['database']
        await sys_conn.execute(
            f'CREATE DATABASE "{database}" OWNER "{user}"'
        )
        await sys_conn.close()
        conn = await asyncpg.connect(**args)
    return conn


async def create_tables(conn):
    await conn.execute(f'''
create table questions
(
    id         serial                  not null
        constraint questions_pk
            primary key,
    author     text                    not null,
    title      text                    not null,
    body       text                    not null,
    tags       text,
    created_at timestamp default now() not null,
    score      integer   default 0     not null
);

alter table questions
    owner to postgres;

create unique index questions_id_uindex
    on questions (id);
''')
    await conn.execute(f'''
create table answers
(
    id          serial                  not null
        constraint answers_pk
            primary key,
    question_id integer                 not null
        constraint answers_questions_id_fk
            references questions
            on delete cascade,
    author      text                    not null,
    body        text                    not null,
    created_at  timestamp default now() not null,
    score       integer   default 0     not null
);

alter table answers
    owner to postgres;

create unique index answers_id_uindex
    on answers (id);
''')
    await conn.execute(f'''
create table comments
(
    id          serial                  not null
        constraint comments_pk
            primary key,
    question_id integer
        constraint comments_questions_id_fk
            references questions
            on delete cascade,
    answer_id   integer
        constraint comments_answers_id_fk
            references answers
            on delete cascade,
    author      text                    not null,
    body        text                    not null,
    created_at  timestamp default now() not null,
    score       integer   default 0     not null
);

alter table comments
    owner to postgres;

create unique index comments_id_uindex
    on comments (id);
''')
    await conn.execute(f'''
create table votes
(
    id          serial  not null
        constraint votes_pk
            primary key,
    question_id integer
        constraint votes_questions_id_fk
            references questions
            on delete cascade,
    answer_id   integer
        constraint votes_answers_id_fk
            references answers
            on delete cascade,
    comment_id  integer
        constraint votes_comments_id_fk
            references comments
            on delete cascade,
    user_hash   text    not null,
    upvote      boolean not null
);

alter table votes
    owner to postgres;

create unique index votes_id_uindex
    on votes (id);
''')


async def main():
    conn = await connect_or_create(DB_AUTH)
    await create_tables(conn)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
