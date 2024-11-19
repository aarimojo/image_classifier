from app.auth import router as auth_router
from app.feedback import router as feedback_router
from app.model import router as model_router
from app.user import router as user_router
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="Image Prediction API", version="0.0.1")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Route not found",
                "message": f"The requested path '{request.url.path}' does not exist",
                "status_code": 404
            }
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)}
    )

app.include_router(auth_router.router)
app.include_router(model_router.router)
app.include_router(user_router.router)
app.include_router(feedback_router.router)
