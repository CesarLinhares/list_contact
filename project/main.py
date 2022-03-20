import uvicorn
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from src.routes.router import route

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exception):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder({"status": '1004', 'validation_error': exception}),
    )


app.include_router(route)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="localhost",
        port=5656,
    )
