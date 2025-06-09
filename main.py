from fastapi import FastAPI

app = FastAPI()  # Instance of fastapi


@app.get('/')
def greet():
    return {'data': {'name': 'Yashvi'}}


@app.get('/about')
def about():
    return {'data': 'About Page!'}
