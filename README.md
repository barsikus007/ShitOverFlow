# ShitOverFlow
Shitcoded in 2 days StackOverflow clone. Updated and slightly refactored after 2 years just for fun.
## Start
- Install docker and docker-compose
- Copy .env.example to .env and modify it
- Unomment acme.caserver line in docker-compose file or use .env to specify your domain and email
- Run
```bash
docker compose up -d --build
```
## Migrate data from previous schema and truncate long unvalidated strings
(Interval is for Moscow time zone)
```sql
ALTER TABLE answer
    ALTER COLUMN created_at 
    TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC';
UPDATE answer SET created_at = created_at - interval '3 hours';
ALTER TABLE comment
    ALTER COLUMN created_at 
    TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC';
UPDATE comment SET created_at = created_at - interval '3 hours';
ALTER TABLE question
    ALTER COLUMN created_at 
    TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC';
UPDATE question SET created_at = created_at - interval '3 hours';

UPDATE question SET title = SUBSTRING(title, 1, 1024) WHERE LENGTH(title) > 1024;
UPDATE question SET tags = SUBSTRING(tags, 1, 1024) WHERE LENGTH(tags) > 1024;

UPDATE question SET body = SUBSTRING(body, 1, 4096) WHERE LENGTH(body) > 4096;
UPDATE comment SET body = SUBSTRING(body, 1, 4096) WHERE LENGTH(body) > 4096;
UPDATE answer SET body = SUBSTRING(body, 1, 4096) WHERE LENGTH(body) > 4096;

UPDATE question SET author = SUBSTRING(author, 1, 1024) WHERE LENGTH(author) > 1024;
UPDATE comment SET author = SUBSTRING(author, 1, 1024) WHERE LENGTH(author) > 1024;
UPDATE answer SET author = SUBSTRING(author, 1, 1024) WHERE LENGTH(author) > 1024;
```
