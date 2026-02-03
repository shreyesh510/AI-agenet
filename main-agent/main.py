from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "fast api app is running"}
