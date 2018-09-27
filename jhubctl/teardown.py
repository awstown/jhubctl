import boto3
import logging

#from . import aws

## Note: the following functions are just placeholders. More checking
#        is needed to prevent bad teardown requests.


def teardown_jupyterhub_role(role_name):
    """Teardown an EKS role and remove from resource list."""
    # Deploy the role.
    try:
        logging.info(f"Checking that {role_name} exists.\n")

        stack = aws.cf.Stack(f"{role_name}")
        aws.raise_if_does_not_exist(stack)
        response = aws.client.delete_stack(
            StackName=role_name
        )
        logging.info(f"{role_name} deleted.\n")

    except aws.ResourceDoesNotExistError:
        logging.info(f"{role_name} does not exist.\n")


def teardown_jupyterhub_vpc(vpc_name):
    """Teardown VPC and remove from the cloudformation resource list."""
    # Deploy the role.
    try:
        logging.info(f"Checking that {vpc_name} exists.\n")

        stack = aws.cf.Stack(f"{vpc_name}")
        aws.raise_if_does_not_exist(stack)
        response = aws.client.delete_stack(
            StackName=vpc_name
        )
        logging.info(f"{vpc_name} deleted.\n")

    except aws.ResourceDoesNotExistError:
        logging.info(f"{vpc_name} does not exist.\n")


def teardown_jupyterhub_cluster(cluster_name):
    """Teardown a EKS cluster and remove from cloudformation list."""
    # Deploy the role.
    try:
        logging.info(f"Checking that {cluster_name} exists.\n")

        stack = aws.cf.Stack(f"{cluster_name}")
        aws.raise_if_does_not_exist(stack)
        response = aws.client.delete_stack(
            StackName=cluster_name
        )
        logging.info(f"{cluster_name} deleted.\n")

    except aws.ResourceDoesNotExistError:
        logging.info(f"{cluster_name} does not exist.\n")


def teardown_ondemand_workers(workers_name):
    """Teardown a EKS cluster and remove from cloudformation list."""
    # Deploy the role.
    try:
        logging.info(f"Checking that {workers_name} exists.\n")

        stack = aws.cf.Stack(f"{workers_name}")
        aws.raise_if_does_not_exist(stack)
        response = aws.client.delete_stack(
            StackName=workers_name
        )
        logging.info(f"{workers_name} deleted.\n")

    except aws.ResourceDoesNotExistError:
        logging.info(f"{workers_name} does not exist.\n")


def teardown_spot_instances(spot_instance_name):
    """Teardown spot instances and remove from cloudformation list."""
    # Deploy the role.
    try:
        logging.info(f"Checking that {spot_instance_name} exists.\n")

        stack = aws.cf.Stack(f"{spot_instance_name}")
        aws.raise_if_does_not_exist(stack)
        response = aws.client.delete_stack(
            StackName=spot_instance_name
        )
        logging.info(f"{spot_instance_name} deleted.\n")

    except aws.ResourceDoesNotExistError:
        logging.info(f"{spot_instance_name} does not exist.\n")


def teardown_utilities(utilities_name):
    """Teardown spot instances and remove from cloudformation list."""
    # Deploy the role.
    try:
        logging.info(f"Checking that {utilities_name} exists.\n")

        stack = aws.cf.Stack(f"{utilities_name}")
        aws.raise_if_does_not_exist(stack)
        response = aws.client.delete_stack(
            StackName=utilities_name
        )
        logging.info(f"{utilities_name} deleted.\n")

    except aws.ResourceDoesNotExistError:
        logging.info(f"{utilities_name} does not exist.\n")
