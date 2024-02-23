import os
import dotenv
import fastapi
import pydantic
import stripe
import zmq

dotenv.load_dotenv()
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

context: zmq.Context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://localhost:5555")

app: fastapi.FastAPI = fastapi.FastAPI()


class CreateUserTaskRequest(pydantic.BaseModel):
    id: str
    name: str
    email: str


@app.get("/api/v1/health")
async def health():
    return "App is running!", 200


@app.post("/api/v1/task/create/customer")
async def outward_sync(user: CreateUserTaskRequest):
    if not user.id or not user.name or not user.email:
        raise fastapi.HTTPException(status_code=400, detail="Invalid payload")
    socket.send_json(user.model_dump())
    return "OK", 200


@app.post("/api/v1/endpoint/stripe")
async def inward_sync(req: fastapi.Request):
    sig_header = req.headers.get("stripe-signature")
    data = await req.body()

    event: stripe.Event = None
    try:
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET,
            api_key=STRIPE_API_KEY,
        )
    except ValueError as e:
        raise fastapi.HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except stripe.error.SignatureVerificationError as e:
        raise fastapi.HTTPException(
            status_code=400, detail=f"Error verifying webhook signature: {e}"
        )

    if event.type == "customer.created":
        name = event.data.object.get("name")
        email = event.data.object.get("email")
        _id = event.data.object.get("id")
        print(_id, name, email)

    return fastapi.Response(status_code=200)
