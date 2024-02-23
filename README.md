# Zenskar Task

[Link](https://zenskar.notion.site/Zenskar-Assignment-Back-End-Engineer-Intern-c2b28fa7ed0247008197c09d10ff8532) for the task

## Setup

0. Make sure you have docker and python (virtualenv) installed

1. Navigate to the directory, make a virtual python environment and install the requirements:

```sh
virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

2. Create a `.env` file in the root of this directory, a sample one being given in the [`.env.sample`](./.env.sample) file. Get the Stripe api key. For getting the Stripe webhook secret, goto #7. Preferably, don't touch any environment variables starting with `PSQL_`. If you do, make sure to change the same in the [`postgres.docker.yaml`](./postgres.docker.yaml) file as well :p

3. Start the PostgreSQL database using docker:

```sh
docker compose -f postgres.docker.yaml up
```

4. Run the FastAPI server:

```sh
uvicorn server:app --reload
```

5. Start the ZeroMQ consumer:

```sh
python3 consumer.py
```

6. TCP tunneling via [ngrok](https://ngrok.com/):

```sh
ngrok http 8000
```

7. Copy the tunneled url from ngrok. Go to the [Stripe webhook dashboard](https://dashboard.stripe.com/test/webhooks) and add a new endpoint. Paste the copied ngrok url and add `/api/v1/endpoint/stripe` in front of it. Select `customer.created` event to listen to and add the endpoint. Grab the webhook secret and paste it in the `.env` file mentioned in #2 and then restart the FastAPI server.

## Operations

0. Make sure the server is running by sending a post request to `http://localhost:8000/api/v1/health`

1. Send a POST request to `http://localhost:8000/api/v1/task/create/customer`. A sample cURL command for the same is:

```sh
curl -X POST "http://127.0.0.1:8000/api/v1/task/create/customer" -H "accept: application/json" -H "Content-Type: application/json" -d '{"id": "489703215467608", "email": "adit@example.com", "name": "adit"}'
```

2. Alternatively, you can also [add a user on Stripe](https://dashboard.stripe.com/test/customers) directly. I'm using Stripe in testing mode.
