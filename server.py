from fastapi import FastAPI,  HTTPException
from pydantic import BaseModel
import zmq

context: zmq.Context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://localhost:5555")

app: FastAPI = FastAPI()

class CreateUserTaskRequest(BaseModel):
    id: int
    name: str
    email: str

@app.post("/api/v1/task/create/customer")
async def create_customer_task(user: CreateUserTaskRequest):
    if not user.id or not user.name or not user.email:
        raise HTTPException(status_code=400, detail="Invalid payload")
    socket.send_json(user.model_dump())
    return "OK", 200