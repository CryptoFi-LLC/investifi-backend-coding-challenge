import os
import uuid

from abc import abstractmethod
from dyntastic import Dyntastic
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
from typing import Optional, ClassVar, Dict


class DynamoDbModelBase(Dyntastic):
    __table_region__ = os.environ.get("AWS_REGION")
    __table_host__ = os.environ.get("DYNAMO_ENDPOINT")
    __hash_key__ = "hash_key"
    __range_key__ = "range_key"

    @property
    @abstractmethod
    def __table_name__(self):  # over-ride this on each implementing class
        pass

    hash_key: str = Field(default=None, title="DynamoDB Partition Key")
    range_key: str = Field(default=None, title="DynamoDB Sort Key")


"""TODO
Architect a data structure for storing user's recurring orders. Two tables have already been setup for you,
User and RecurringOrder. It is up to you how you want to structure the data, so feel free to use both tables
or only one based on your strategy.

Don't forget to checkout the full requirements in the README or in api.py as those will pertain relevant information that
will apply to this file.
"""


class UserInfo(BaseModel):
    first_name: str
    last_name: str
    
    account_number: str
    routing_number: str


class User(DynamoDbModelBase):
    __table_name__ = "User"
    
    entity_name: ClassVar[str] = 'User'
    
    hash_key_prefix: ClassVar[str] = f'{entity_name}#'
    range_key_const: ClassVar[str] = 'details'
    
    range_key: str = Field(range_key_const, const=True)
    
    info: Optional[UserInfo]

    # Safety measure to format `hash_key` on class creation
    # so it accepts either the full User#{uuid} or just uuid
    @validator('pk', pre=True, check_fields=False, allow_reuse=True)
    def _generate_user_hash_key(cls, value: str):
        return f'{cls.hash_key_prefix}{value.split("#")[-1]}'


class RecurringOrderCurrencyEnum(str, Enum):
    BTC = 'BTC'  # Bitcoin
    ETH = 'ETH'  # Ethereum


class RecurringOrderFrequencyEnum(str, Enum):
    DAILY = 'DAILY'
    BI_MONTHLY = 'BI_MONTHLY'
    

class RecurringOrder(DynamoDbModelBase):
    __table_name__ = "RecurringOrder"
    entity_name: ClassVar[str] = 'RecurringOrder'
    
    hash_key_prefix: ClassVar[str] = f'{User.entity_name}#'
    range_key_prefix: ClassVar[str] = f'{entity_name}#'
    
    currency: RecurringOrderCurrencyEnum
    frequency: RecurringOrderFrequencyEnum
    amount: int = Field(gt=0)  # USD currenty int 1000 -> $10.00 to prevent rounding error issues and follow how most cores handle money values
    
    class Config:
        use_enum_values = True 
    
    # Safety measure to format `hash_key` on class creation
    # so it accepts either the full User#{uuid} or just uuid
    @validator('hash_key', pre=True, check_fields=False)
    def _format_recurring_order_hash_key(cls, value):
        return f'{cls.hash_key_prefix}{value.split("#")[-1]}'

    # Generates `range_key` on creation of new RecurringOrder
    # ignores if validating existing
    # uses root_validator to have access to other fields
    @root_validator(pre=True)
    def _generate_uuids(cls, values: Dict):
        if not values.get('range_key'):
            values['range_key'] = f'{cls.range_key_prefix}{uuid.uuid4()}#{values.get("currency")}#{values.get("frequency")}'
        return values
