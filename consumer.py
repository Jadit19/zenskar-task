import os
import dotenv
import stripe
import zmq

dotenv.load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")

context: zmq.Context = zmq.Context()
zmq_socket = context.socket(zmq.PULL)
zmq_socket.bind("tcp://127.0.0.1:5555")

while True:
    message: dict = zmq_socket.recv_json()
    if not set(["id", "name", "email"]).issubset(message.keys()):
        continue

    try:
        customer: stripe.Customer = stripe.Customer.create(
            id=message.get("id"), name=message.get("name"), email=message.get("email")
        )
    except Exception as e:
        pass