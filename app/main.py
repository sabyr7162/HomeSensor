from fastapi import FastAPI, HTTPException
from sqlalchemy import *

from database import initialize_database
from routers import router 
from fastapi.staticfiles import StaticFiles

app = FastAPI(title='HomeSensor app')
app.include_router(router)
initialize_database()



app.mount("/", StaticFiles(directory="static", html=True), name="static")