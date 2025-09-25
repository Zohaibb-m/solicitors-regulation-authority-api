from app.router import router
from fastapi import FastAPI
import uvicorn

app = FastAPI()
app.include_router(router)

def handler(event, context):
    return app

@app.get("/")
def read_root():
    return {"message": "Welcome to the Solicitors Regulation Authority API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8800)