from app.router import router
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Solicitors Regulation Authority API"}

