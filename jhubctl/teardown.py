import boto3
import logging


from . import aws
from .utils import (
    get_stack_value,
    raise_if_does_not_exist,
    ResourceDoesNotExistError
)

def teardown_jupyterhub_role(role_name):
    """Teardown EKS."""
    # Deploy the role.
    try:
        logging.info(f"Checking that {role_name} exists.\n")

        stack = aws.cf.Stack(f"{role_name}")
        raise_if_does_not_exist(stack)
        response = aws.client.delete_stack(
            StackName=role_name
        )
        aws.waiter.wait(StackName=stack.name)
        logging.info(f"{role_name} deleted.\n")

    except ResourceDoesNotExistError:
        logging.info(f"{role_name} does not exist.\n")


def teardown_jupyterhub_vpc(vpc_name):
    """"""
    # Deploy the role.
    try:
        logging.info(f"Checking that {vpc_name} exists.\n")

        stack = aws.cf.Stack(f"{vpc_name}")
        raise_if_does_not_exist(stack)
        response = aws.client.delete_stack(
            StackName=vpc_name
        )
        aws.waiter.wait(StackName=stack.name)
        logging.info(f"{vpc_name} deleted.\n")

    except ResourceDoesNotExistError:
        logging.info(f"{vpc_name} does not exist.\n")
