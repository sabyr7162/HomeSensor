from fastapi import HTTPException
from datetime import datetime, timedelta, timezone

import jwt


SECRET_KEY = 'fk;lkajfiqjwirhnvnkjrioqjwoirjklasmfm454124jhhjh5534u8hdjksn'
ALGORITHM = 'HS256'



def create_token(id):
    data = {
        'sub': str(id),
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def token_verify(credentials):
    try:
        payload = jwt.decode(
            credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid or expired token')
    return payload