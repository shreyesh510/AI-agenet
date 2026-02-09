from fastapi import FastAPI, Request
from mainAgent import mainAgent


app = FastAPI()

@app.get("/")
def hello():
    return {"message": "fast api app is running"}

# @app.post("/chat")
# def chat_endpoint(request: dict):
#     user_message = request.get("message", "")
#     # Here you would typically process the message and generate a response
#     response_message = f"Received your message: {user_message}"
#     return {"response": response_message}

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("query", "")

    response = mainAgent(query) or {"response": f"Received your query: {query}"}
    print("Response:", response)
    return response
