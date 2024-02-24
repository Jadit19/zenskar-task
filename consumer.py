import os
import dotenv
import stripe
import zmq

dotenv.load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")
ZMQ_STRIPE_TOPIC = "ZMQ_STRIPE"

context: zmq.Context = zmq.Context()
zmq_stripe_socket = context.socket(zmq.SUB)
zmq_stripe_socket.bind("tcp://127.0.0.1:5555")
zmq_stripe_socket.subscribe(ZMQ_STRIPE_TOPIC)

poller = zmq.Poller()
poller.register(zmq_stripe_socket, zmq.POLLIN)

while True:
    events: dict = dict(poller.poll(timeout=100))

    if zmq_stripe_socket not in events:
        continue

    topic: str = zmq_stripe_socket.recv_string()
    message: dict = zmq_stripe_socket.recv_json()

    if topic != ZMQ_STRIPE_TOPIC:
        continue

    if not set(["id", "name", "email"]).issubset(message.keys()):
        continue

    try:
        customer: stripe.Customer = stripe.Customer.create(
            id=message.get("id"), name=message.get("name"), email=message.get("email")
        )
    except Exception as e:
        pass
