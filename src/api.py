from fastapi import FastAPI


app = FastAPI(
    title="Investifi Backend Coding Challenge",
)


@app.get("/")
def hello_world():
    """
    NOTE: This is route is used as an example for the test suite
    No action needed here
    """
    return {"hello": "world"}


@app.get("/recurring-orders")
def get_recurring_orders():
    """
    TODO
    # Requirements:
    # The GET route should accept a User ID and return only said users recurring orders
    # if no ID is provided, an error should be raised.
    """
    return {}


@app.post("/recurring-orders")
def post_recurring_orders():
    """
    TODO
    Requirements:
    The POST route should create a recurring order for a user
    A recurring order can be for only BTC or ETH
    A recurring order must have a concept of Frequency. Only Daily or Bi-Monthly frequencies is allowed
    A User can only have 1 recurring order for a given Crypto/Frequency i.e. BTC/Daily
    A recurring order must have a USD amount greater than 0
    A recurring order needs to be associated with a specifc user.
    """
    return {}
