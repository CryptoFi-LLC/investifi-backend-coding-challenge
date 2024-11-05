import boto3
import os
import unittest

from docker.scripts.setup_db_tables import DbSetup

"""
NOTE: You will most likely not need to edit this file.
Test suite helpers.  These setup a framework for writing unittests with a live database and deleting
test data in between test runs.
"""


def ensure_using_aws_test_keys(func):
    """
    This decorator is a safe guard to ensure that when running the test suite we are using
    fake AWS access keys. This is needed due to the fact the test suite resets the database's
    data after each test class has completed running
    """

    def wrapper_func(*args, **kwargs):
        AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
        AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
        if (
            AWS_ACCESS_KEY_ID != "testing123"
            or AWS_SECRET_ACCESS_KEY != "supersecretkey"
        ):
            raise Exception("YOU MUST RUN TESTS IN DOCKER LOCAL ENV")

        func(*args, **kwargs)
        # Do something after the function.

    return wrapper_func


class InvestifiTestCase(unittest.TestCase):
    @classmethod
    @ensure_using_aws_test_keys
    def setUpClass(cls):
        cls._purge_all_tables()
        db_setup = DbSetup()
        db_setup.run()

    @classmethod
    @ensure_using_aws_test_keys
    def tearDownClass(cls):
        cls._purge_all_tables()

    @classmethod
    @ensure_using_aws_test_keys
    def _purge_all_tables(cls):
        cls.dynamodb = boto3.resource(
            "dynamodb",
            endpoint_url=os.environ["DYNAMO_ENDPOINT"],
            region_name=os.environ["AWS_REGION"],
        )

        tables = cls.dynamodb.tables.all()
        for table in tables:
            # This is safe guard to ensure we are not pointed at an AWS environment
            # and are using the amazon/dynamodb-local image in the docker-compose file
            if "ddblocal" not in table.table_arn:
                raise Exception("YOU MUST RUN TESTS IN DOCKER LOCAL ENV")
            table.delete()
