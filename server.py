import os
import dotenv
import fastapi
import psycopg2
import pydantic
import stripe
import zmq

# Loading environment variables
dotenv.load_dotenv()
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# PostgreSQL
db_config = {
    "dbname": os.getenv("PSQL_DB"),
    "user": os.getenv("PSQL_USER"),
    "password": os.getenv("PSQL_PASSWORD"),
    "host": "127.0.0.1",
    "port": os.getenv("PSQL_PORT"),
}
sql_connection = psycopg2.connect(**db_config)

# ZeroMQ
context: zmq.Context = zmq.Context()
zmq_socket = context.socket(zmq.PUSH)
zmq_socket.connect("tcp://localhost:5555")

# FastAPI
app: fastapi.FastAPI = fastapi.FastAPI()


# Health check
@app.get("/api/v1/health")
async def health():
    return "App is running!", 200


class CreateUserTaskRequest(pydantic.BaseModel):
    id: str
    name: str
    email: str


# Endpoint for creating ZeroMQ job that creates customer
@app.post("/api/v1/task/create/customer")
async def outward_sync(user: CreateUserTaskRequest):
    if not user.id or not user.name or not user.email:
        raise fastapi.HTTPException(status_code=400, detail="Invalid payload")
    zmq_socket.send_json(user.model_dump())
    return "OK", 200


# Endpoint for stripe
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
        customer_id = event.data.object.get("id")
        customer_name = event.data.object.get("name")
        customer_email = event.data.object.get("email")

        cursor = sql_connection.cursor()
        cursor.execute(
            """
            INSERT INTO customer (id, name, email)
            VALUES (%s, %s, %s)
                        """,
            (customer_id, customer_name, customer_email),
        )
        sql_connection.commit()

    return fastapi.Response(status_code=200)
