from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "fast api app is running"}

@app.post("/chat")
def chat_endpoint(request: dict):
    user_message = request.get("message", "")
    # Here you would typically process the message and generate a response
    response_message = f"Received your message: {user_message}"
    return {"response": response_message}