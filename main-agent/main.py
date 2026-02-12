from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from mainAgent import mainAgent
from auth_routes import router as auth_router
from cron_job import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(lifespan=lifespan)

# Register OAuth2 routes
app.include_router(auth_router)


@app.get("/")
def hello():
    return {"message": "fast api app is running"}


@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("query", "")
    history = data.get("history", None)

    response = mainAgent(query, history) or {"response": f"Received your query: {query}"}
    print("Response:", response)
    return response
