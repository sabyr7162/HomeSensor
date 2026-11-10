from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlalchemy.orm import Session 
import jwt
from datetime import datetime, timezone, timedelta
from sqlalchemy import select

from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, Boolean, BigInteger, JSON
from database import metadata

from database import get_db

router = APIRouter()

password_hash = PasswordHash.recommended()
SECRET_KEY = 'fk;lkajfiqjwirhnvnkjrioqjwoirjklasmfm454124jhhjh5534u8hdjksn'
ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login')



users = Table(
    'users',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('email', String, unique=True),
    Column('hashed_password', String),
    Column('created_at', DateTime)
)

devices = Table(
    'devices', 
    metadata, 
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('device_id', String, unique=True),
    Column('name', String),
    Column('user_id', Integer, ForeignKey(users.id), nullable=False),
    Column('token', String, unique=True, nullable=False),
    Column('status', Boolean, nullable=False, default=True),
    Column('created_at', DateTime)
)

measurements = Table(
    'measurements', 
    metadata, 
    Column('id', BigInteger, primary_key=True, autoincrement=True),
    Column('device_id', Integer, ForeignKey(devices.id), nullable=True),
    Column('timestamp', DateTime, index=True),
    Column('metrics', JSON),
    Column('received_at', DateTime)
)



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


class UserRegisterRequest(BaseModel):
    email: str
    password: str

class UserLoginRequest(BaseModel):
    email: str
    password: str

class DeviceRegisterRequest(BaseModel):
    device_id: str
    name: str
    status: bool

# find user by email/login
def find_user(session, email):
    query = select(users).where(users.email == email)
    result = session.execute(query).mappings().first
    return result

# create user 
def create_user(sesion, data):
    query = users.insert().values(data)
    result = sesion.execute(query)
    sesion.commit()
    return result


@router.post('/users', status_code=200)
def register(body: UserRegisterRequest, session: Session = Depends(get_db)):

    # check email regex
    if find_user(session, body.email):
        raise HTTPException(status_code='403', detail='user by this email already registered')
    
    hashed_password = password_hash.hash(body.password)
    data = body.model_dump()
    data['hashed_password'] = hashed_password
    data.pop('password')

    # create user, add to db
    result = create_user(data)
    user_id = result.inserted_primary_key[0]

    return user_id


@router.post('/users/login', status_code=200)
def login(body: UserLoginRequest, session: Session = Depends(get_db)):
    # check if user in database
    data = find_user(session, body.email)
    if not data or not password_hash.verify(body.password, data.hashed_password):
        raise HTTPException(status_code=404, detail="Invalid login or password")
    user_id = data['id']
    token = create_token(user_id)
    return {'access_token': token, 'token_type': 'bearer'}


def add_device(session, data):
    query = devices.insert().values(data)
    result = session.execute(query)
    session.commit
    return result 

@router.post('/users/device')
def add_device(body: DeviceRegisterRequest, session: Session = Depends(get_db)):
    
