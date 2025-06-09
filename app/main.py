from fastapi import FastAPI
from .core.database import Base, engine
from app.auth.models import User
from app.auth.routes import router as auth_router

app = FastAPI(title="E-commerce backend using FastAPI")  # Instance of fastapi

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

@app.get("/")
async def root():
    return {"message": "API is connected to the database!"}

""" class Blog(BaseModel):
    title: str
    body: str
    
@app.get('/')  # @app - path function decorator
def greet():  # path operation function
    return {'data': {'name': 'Yashvi'}}

@app.get('/about')
def about():
    return {'data': 'About Page!'}

@app.post('/add')
def create(request: Blog):
    return request """
