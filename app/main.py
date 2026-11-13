from fastapi import FastAPI, HTTPException
from sqlalchemy import *

from routers import router 

app = FastAPI(title='HomeSensor app')
app.include_router(router)

