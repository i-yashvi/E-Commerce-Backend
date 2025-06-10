from fastapi import FastAPI
from .core.database import Base, engine
from app.auth.models import User
from app.auth.routes import router as auth_router
from app.products.routes import admin_router as admin_product_router
from app.products.routes import public_router as public_product_router
from app.cart.routes import router as cart_router


app = FastAPI(title="E-commerce backend using FastAPI")  # Instance of fastapi

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(admin_product_router)
app.include_router(public_product_router)
app.include_router(cart_router)


@app.get("/")
async def root():
    return {"message": "API is connected to the database!"}
