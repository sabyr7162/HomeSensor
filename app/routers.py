from fastapi import APIRouter, HTTPException, Depends, Form, Header, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session 
from pwdlib import PasswordHash
import hashlib 
from datetime import datetime, timezone, timedelta


from database import get_db
from security import create_token, token_verify
from schemas import *
from crud import *


password_hash = PasswordHash.recommended()

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/users/login')


@router.post('/users', status_code=200)
def register(body: UserRegisterRequest, session: Session = Depends(get_db)):
    # check email regex
    print(body.email)
    if find_user(session, body.email):
       raise HTTPException(status_code='403', detail='user by this email already registered')
    
    hashed_password = password_hash.hash(body.password)
    data = body.model_dump()
    data['hashed_password'] = hashed_password
    data.pop('password')
    data['created_at'] = datetime.now(timezone.utc)
    # create user, add to db
    result = create_user(session, data)
    user_id = result.inserted_primary_key[0]

    return {
        "status": "success",
        "message": "User registered successfully",
        "user_id": user_id}


@router.post('/users/login', status_code=200)
def login(username: str = Form(...), 
        password: str = Form(...), 
        session: Session = Depends(get_db)):
    # check if user in database
    data = find_user(session, username)
    if not data or not password_hash.verify(password, data.hashed_password):
        raise HTTPException(status_code=404, detail="Invalid login or password")
    user_id = data['id']
    token = create_token(user_id)
    return {'access_token': token, 'token_type': 'bearer'}


@router.get('/users', status_code=200)
def get_me(token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)):
    payload = token_verify(token)
    user_id = payload.get('sub')
    data = find_user_by_id(session, user_id)
    return data


@router.delete('/users', status_code=200)
def delete_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)):
    payload = token_verify(token)
    user_id = payload.get('sub')
    result = remove_user(session, user_id)
    if not result:
        raise HTTPException(status_code=404, detail='User not found')
    return {'status': 'success'}


@router.post('/users/device', status_code=201)
def add_device(body: DeviceRegisterRequest, session: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = token_verify(token)
    user = payload.get('sub')
    data = body.model_dump()
    data['user_id'] = user

    # create token 
    data['token'] = hashlib.sha256(data['device_id'].encode()).hexdigest()
    data['created_at'] = datetime.now(timezone.utc)
    result = create_device(session, data)
    return {
        "status": "success",
        "message": "Device registered successfully",
        "device_id": data['device_id'],
        "token": data['token'] }


@router.delete('/users/device/{device_id}', status_code=200)
def delete_device(device_id: int, token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)):
    payload = token_verify(token)
    user_id = payload.get('sub')
    result = remove_device(session, device_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"status": "success"}



@router.get('/users/device/', status_code=200)
def get_devices(token: str = Depends(oauth2_scheme), session: Session = Depends(get_db)):
    payload = token_verify(token)
    devices = find_devices(session, payload.get('sub'))
    return {'devices': devices}


@router.get('/users/device/{device_id}', status_code=200)
def get_device(device_id: int, 
               token: str = Depends(oauth2_scheme), 
               session: Session = Depends(get_db)
               ):
    payload = token_verify(token)
    user_id = payload.get('sub')
    device = find_device_by_id(session, device_id)

    if not device or device['user_id'] != int(user_id):
        raise HTTPException(status_code=404, detail='Device not found')
    return device
 
# get measurements from device
@router.post('/user/device/measurements', status_code=200)
def recieve_measurements(
    body: MeasurementsPostRequest, 
    session: Session = Depends(get_db),
    x_device_token: str = Header(...)):
    device = find_device_token(session, x_device_token)
    if not device:
        raise HTTPException(status_code=403, detail="Access denied")
    data = body.model_dump()
    data.pop('id', None)
    data['timestamp'] = datetime.now(timezone.utc)
    data['device_id'] = device['id']
    data['received_at'] = datetime.now(timezone.utc)
    result = add_measurements(session, data)
    return {"status": "success"}


# get measuremnts from db 
@router.get('/user/device/{device_id}/measurements')
def get_measurements(
    device_id: int,
    period: str = Query("24h", description="Filter period: 1h, 24h, 7d, 30d"),
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_db)):

    device = find_device_by_id(session, device_id)
    payload = token_verify(token)
    user_id = payload.get('sub')
    
    if not device or device['user_id'] != int(user_id):
        raise HTTPException(status_code=404, detail="Device not found or access denied")

    now = datetime.now(timezone.utc)
    match period: 
        case '1h':
            cutoff = now - timedelta(hours=1)
        case '24h':
            cutoff = now - timedelta(days=1)
        case '7d':
            cutoff = now - timedelta(days=7)
        case '30d':
            cutoff = now - timedelta(days=30)
        case _:
            cutoff = now - timedelta(days=1)

    measurements = find_measurements(session, device_id, cutoff)
    return [dict(row) for row in reversed(measurements)]
    

# get latests measurements from database     
@router.get('/user/device/{device_id}/measurements/latest')
def get_device_status(device_id: int, session: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    payload = token_verify(token)
    device = find_device_by_id(session, device_id)
    user_id = payload.get('sub')
    if not device or device['user_id'] != int(user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    latest = get_recent_measurement(session, device_id)
    if not latest:
        raise HTTPException(status_code=404, detail='No measurements found')
    return dict(latest)