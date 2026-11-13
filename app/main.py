from fastapi import FastAPI, HTTPException
from sqlalchemy import *

from database import initialize_database
from routers import router 

app = FastAPI(title='HomeSensor app')
app.include_router(router)
initialize_database()

