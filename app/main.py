from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, SecurityScheme as SecuritySchemeModel
from fastapi.openapi.utils import get_openapi
from .core.database import Base, engine
from .core.exceptions import custom_http_exception_handler, unhandled_exception_handler
from app.core.logger import logger
from app.auth.models import User
from app.auth.routes import router as auth_router
from app.products.routes import admin_router as admin_product_router
from app.products.routes import public_router as public_product_router
from app.cart.routes import router as cart_router
from app.orders.routes import order_router as order_router
from app.orders.routes import checkout_router as checkout_router
 

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("E-commerce backend starting up.")  # Startup code
    yield
    logger.info("E-commerce backend shutting down.")  # Shutdown code


app = FastAPI(  # Instance of fastapi
    title="E-commerce backend using FastAPI",
    lifespan=lifespan
) 

app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(admin_product_router)
app.include_router(public_product_router)
app.include_router(cart_router)
app.include_router(order_router)
app.include_router(checkout_router)


@app.get("/")
async def root():
    return {"message": "API is connected to the database!"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="E-Commerce Backend APIs",
        version="1.0.0",
        description="NucleusTeq Python Training Project",
        routes=app.routes,
    )

    if "components" not in openapi_schema:
        openapi_schema["components"] = {}

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
