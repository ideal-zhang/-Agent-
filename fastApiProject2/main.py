from fastapi import FastAPI
from routers import news, users, favorite, history
from fastapi.middleware.cors import CORSMiddleware
from utils.expection_handles import register_exception_handler
app = FastAPI()
register_exception_handler(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 运行的源
    allow_credentials=True,# 运行携带cookie
    allow_methods=["*"],   # 运行的请求方法
    allow_headers=["*"]    # 运行的请求头
)

@app.get("/")
async def root():
    return {"message": "Hello World123"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)

app.include_router(history.router)
