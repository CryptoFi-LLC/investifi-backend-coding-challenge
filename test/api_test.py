import uuid

from fastapi.testclient import TestClient

from test.helpers import InvestifiTestCase
from src.api import app
from src.model import User, RecurringOrder, RecurringOrderCurrencyEnum, RecurringOrderFrequencyEnum


USER_ID = uuid.uuid4()

class TestHelloWorldRoute(InvestifiTestCase):
    """
    Example of how to write a integration test with FastApi in a dockerized container.
    NOTE: Make sure to have your classes inherit from InvestifiTestCase in order to take
    advantage of a predefined test suite framework
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = TestClient(app)
        cls.url = "/"

    def test_hello_world_route(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"hello": "world"})


"""
TODO [OPTIONAL]
Write more tests for your work. These can be unit tests for specfic classes or
integration tests that actually make api calls like the example above.
"""

class TestModels(InvestifiTestCase):
    # These are not actually needed since pydantic already does test coverate.
    # This is mostly just for quick personal sanity check/reference during development.
    
    def test_user_model(self):
        user_dict = {'hash_key': f'User#{USER_ID}',
                     'info': {'first_name': 'Alex',
                              'last_name': 'Vansteel',
                              'account_number': '123456789',
                              'routing_number': '987654321'}}
        
        user: User = User(**user_dict)
        
        self.assertEqual(user.hash_key, user_dict['hash_key'])
        self.assertEqual(user.range_key, 'details')
        self.assertEqual(user.info.first_name, user_dict['info']['first_name'])
        self.assertEqual(user.info.last_name, user_dict['info']['last_name'])
        self.assertEqual(user.info.account_number, user_dict['info']['account_number'])
        self.assertEqual(user.info.routing_number, user_dict['info']['routing_number'])
        
    def test_recurring_order(self):
        recurring_order_dict = {'hash_key': f'User#{USER_ID}',
                                'currency': RecurringOrderCurrencyEnum.BTC,
                                'frequency': RecurringOrderFrequencyEnum.DAILY,
                                'amount': 1000}
        
        recurring_order: RecurringOrder = RecurringOrder(**recurring_order_dict)
        
        self.assertEqual(recurring_order.hash_key, recurring_order_dict['hash_key'])
        self.assertIsNotNone(recurring_order.range_key)
        self.assertEqual(recurring_order.currency, recurring_order_dict['currency'])
        self.assertEqual(recurring_order.frequency, recurring_order_dict['frequency'])
        self.assertEqual(recurring_order.amount, recurring_order_dict['amount'])
        

class TestRecurringOrdersRoutes(InvestifiTestCase):
        
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = TestClient(app)
        cls.url = "/recurring-orders"
        
    def test_post_recurring_orders_route(self):
        body = {'hash_key': f'User#{USER_ID}',
                'currency': RecurringOrderCurrencyEnum.BTC,
                'frequency': RecurringOrderFrequencyEnum.DAILY,
                'amount': 1000}
        
        response = self.client.post(self.url, json=body)
        self.assertEqual(response.status_code, 200)
        
    def test_post_recurring_orders_zero_amount(self):
        body = {'hash_key': f'User#{USER_ID}',
                'currency': RecurringOrderCurrencyEnum.BTC,
                'frequency': RecurringOrderFrequencyEnum.DAILY,
                'amount': 0}
        
        response = self.client.post(self.url, json=body)
        print(response.json())
        self.assertEqual(response.status_code, 422)
        msg = response.json()['detail'][0].get('msg')
        self.assertEqual(msg, 'ensure this value is greater than 0')
        
    def test_post_recurring_orders_duplicate(self):
        # ideally, I would take the time to set up fixtures in a conftest.py and pre-populate the tabels
        body = {'hash_key': f'User#{USER_ID}',
                'currency': RecurringOrderCurrencyEnum.BTC,
                'frequency': RecurringOrderFrequencyEnum.DAILY,
                'amount': 1000}
        
        response = self.client.post(self.url, json=body)
        self.assertEqual(response.status_code, 200)
        
        body = {'hash_key': f'User#{USER_ID}',
                'currency': RecurringOrderCurrencyEnum.BTC,
                'frequency': RecurringOrderFrequencyEnum.DAILY,
                'amount': 1000}
        
        response = self.client.post(self.url, json=body)
        self.assertEqual(response.status_code, 422)
        
    def test_get_recurring_orders(self):
        body = {'hash_key': f'User#{USER_ID}',
                'currency': RecurringOrderCurrencyEnum.BTC,
                'frequency': RecurringOrderFrequencyEnum.DAILY,
                'amount': 1000}
        self.client.post(self.url, json=body)
        
        body = {'hash_key': f'User#{USER_ID}',
                'currency': RecurringOrderCurrencyEnum.ETH,
                'frequency': RecurringOrderFrequencyEnum.BI_MONTHLY,
                'amount': 10000}
        self.client.post(self.url, json=body)
        
        response = self.client.get(f'{self.url}/{USER_ID}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.content), 2)
        