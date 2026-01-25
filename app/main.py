from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.schemas import IResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/openapi.json"
)

from fastapi.exceptions import HTTPException

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=IResponse.error(code=exc.status_code, message=exc.detail).model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error for debugging
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content=IResponse.error(code=500, message=f"Internal Server Error: {str(exc)}").model_dump()
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=IResponse.error(code=422, message="Validation Error", data=exc.errors()).model_dump()
    )

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    if settings.DASHSCOPE_API_KEY:
        print(f"DEBUG: DASHSCOPE_API_KEY is loaded (starts with {settings.DASHSCOPE_API_KEY[:4]}...)")
    else:
        print("DEBUG: DASHSCOPE_API_KEY is NOT loaded! Please check your .env file.")

@app.get("/")
def root():
    return {"message": "Welcome to CanIMake API", "status": "running"}
