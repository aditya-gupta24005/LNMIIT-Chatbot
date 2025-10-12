from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Message(BaseModel):
    message: str

@app.post("/chat")
def chat_endpoint(msg: Message):
    user_input = msg.message
    # Dummy response (replace with your model/logic)
    return {"response": f"You said: {user_input}"}

