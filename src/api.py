import boto3

from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException

from src.model import User, RecurringOrder, RecurringOrderFrequencyEnum, RecurringOrderCurrencyEnum


recurring_order_table = RecurringOrder.__table_name__


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


@app.get("/recurring-orders/{user_id}")
def get_recurring_orders(user_id: str):
    """
    TODO
    # Requirements:
    # The GET route should accept a User ID and return only said users recurring orders
    # if no ID is provided, an error should be raised.
    """
    
    dynamodb_client = boto3.client('dynamodb')

    key_condition_expression = 'hash_key=:hash_key'
    filter_expression = 'not contains(:range_key, range_key)'
    expression_values = {':hash_key': {'S': f'User#{user_id}'},
                         ':range_key': {'S': 'details'}}

    dynamodb_response = dynamodb_client.query(
        TableName=recurring_order_table,
        KeyConditionExpression=key_condition_expression,
        FilterExpression=filter_expression,
        ExpressionAttributeValues=expression_values,
    )
    
    if recurring_orders := dynamodb_response.get('Items'):
        return recurring_orders
    else:
        raise HTTPException(status_code=404, detail=str('no recurring orders found'))


@app.post("/recurring-orders")
def post_recurring_orders(recurring_order: RecurringOrder):
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
    
    dynamodb_client = boto3.client('dynamodb')
    
    # low cost and fast query on index to see if recording for user with the currency and frequency pair 
    key_condition_expression = f'hash_key=:hash_key AND contains(:range_key, {recurring_order.currency}) AND contains(:range_key, {recurring_order.frequency})'
    expression_values = {':hash_key': {'S': recurring_order.hash_key},
                         ':range_key': {'S': recurring_order.range_key}}

    dynamodb_response = dynamodb_client.query(
        TableName=recurring_order_table,
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_values,
    )
    
    if recurring_order := dynamodb_response.get('Item'):
      raise HTTPException(status_code=422, detail='record already exists for user and currency')
    else:
        try:
            dynamodb_client.put(Item=recurring_order.dict())
        except ClientError as e:
            raise HTTPException(status=500, detail=str(e))
            
    return recurring_order
