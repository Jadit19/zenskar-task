# **Two-Way Integrations:**

This is an exercise to test your comfort level with Python, code structure & quality and rudimentary experience with APIs, databases and queues.

The objective of this exercise is to simulate a product that you are building that has a simple customer catalog (think of it as a simple customer table) and build a two-way integration with a customer catalog in an external service - Stripe in this case. The two-way sync should be near real-time so that a customer added/edited on one system propagates to the other system within a few seconds. The goal is to build this in a way such that you can add other integrations with the customer catalog, and other integrations with other catalogs (like, say, an invoice catalog) in the future.

# **Requirements**:

- Create a simple customer table with columns (ID, name, email) in any SQL based relational database of your choice (Postgres, MySQL, SQLite). The ID in this table is specific to your own product and not related to any identifier on any external systems.

- Create a free test account on Stripe.

- Setup Kafka locally. This should be fairly straightforward using their docker container. You can install it natively instead if that’s more up your alley. You only need to use this as a simple queuing system and not worry about any of its advanced functionality. You can use some other queueing system like RabbitMQ/ZeroMQ if you like instead.

- Implement outward sync from your product to the list of customers in your stripe test account. Any changes to the customer entries on your system should reflect in your Stripe account. You can make changes to the customers in your product either via an API or via a web interface whatever is convenient. Changes made to your system should be added to the queue. Create a worker that pops events from this queue and makes the corresponding updates in Stripe.

- Implement inward sync from the customers on Stripe to the customer list in your product. You can do these one of two ways:
  
  - Poll the customer list every 5-10 seconds to get the list of updates since the last processed update and send these to the queue. Process these events as above.
  
  - Create an API server on your local machine and expose it as a webhook to Stripe using something like Ngrok or Localtunnel. Stripe will send events to this webhook which you can use to sync your product’s customer catalog.

- Create a plan for adding a second integration with Salesforce's customer catalog to your product's customer catalog. You don't need to build this out, but you will have to detail a plan in words on how your code will be extended to support this additional integration. The code that you write for the Stripe integration should be easily extendible to this use case.

- How can the above integrations with your product's customer catalog be extended to support other systems within your product? For example - the invoice catalog. You don’t have to implement this part either, just a description of your approach in words is enough.
