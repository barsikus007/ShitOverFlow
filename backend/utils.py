from hashlib import md5

from fastapi import Request
from fastapi.exceptions import HTTPException


def get_user_hash(request: Request):
    if user_agent := request.headers.get('user-agent', None):
        return md5(f'{request.client.host}{user_agent}'.encode()).hexdigest()
    else:
        raise HTTPException(status_code=403, detail='Invalid user agent')
