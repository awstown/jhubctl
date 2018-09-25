import os
import boto3
import botocore
import jinja2
import json
import subprocess
import logging
from pathlib import Path

from . import env
from .utils import (
    get_config_path,
    get_kube_path,
    get_template_path,
    get_deployment_path,
    read_config_file, 
    read_param_file,
)

client = boto3.client('cloudformation')
waiter = client.get_waiter('stack_create_complete')
cf = boto3.resource('cloudformation')
iam = boto3.client('iam')


class ResourceDoesNotExistError(Exception):
    """Resource does not exist."""


def does_resource_exist(resource):
    """Use boto3 to check if a resource exists."""
    try:
        resource.load()
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError':
            return False
        else:
            raise e


def raise_if_does_not_exist(resource):
    if does_resource_exist(resource) is False:
        raise ResourceDoesNotExistError


def get_stack_value(stack, key):
    for output in stack.outputs:
        if output['OutputKey'] == key:
            return output['OutputValue']


def deploy_eks_role(role_name):
    """Create an EKS Role on AWS for Jupyterhub Deployments with Kubernetes.

    Parameters
    ----------
    name : str 
        Name an EKS role.

    Return
    ------
    role_arn : str
    """ 
    # Deploy the role.
    try:
        logging.info(f"Checking to see if a {role_name} exists.\n")

        stack = cf.Stack(f"{role_name}")
        raise_if_does_not_exist(stack)

        logging.info(f"{role_name} found. No need to create a new one.\n")
    except ResourceDoesNotExistError:
        logging.info(f"{role_name} not found. Creating a new role name {role_name}.\n")

        # Create stack
        stack = cf.create_stack(
            StackName=f'{role_name}',
            TemplateURL=env.ROLE_TEMPLATE_URL,
            Capabilities=[
                'CAPABILITY_NAMED_IAM',
            ]
        )
        # Wait for role to be created.
        waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{role_name} succesfully created.")

    role_arn = get_stack_value(stack, "RoleArn")

    return role_arn


def deploy_vpc(vpc_name):
    """
    
    Parameter
    ---------
    name : str 
        Name assigned to virtual private cloud (VPC).

    Returns
    -------
    security_groups: 

    subnet_ids : 

    vpc_ids : 
    """
    try:
        logging.info(f"Checking if {vpc_name} already exists.")

        stack = cf.Stack(f"{vpc_name}")
        raise_if_does_not_exist(stack)

        logging.info(f"{vpc_name} already exists. No need to create a new one.")

    except:

        logging.info(f"{vpc_name} does not exist. Creating a new VPC named {vpc_name}.")

        stack = cf.create_stack(
            StackName=f"{vpc_name}",
            TemplateURL=env.VPC_TEMPLATE_URL,
            Parameters=read_param_file("vpc.json"),
        )
        waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{vpc_name} successfully created")

    # Rip out necessary data for moving forward.
    security_groups = get_stack_value(stack, 'SecurityGroups')
    subnet_ids = get_stack_value(stack, 'SubnetIds')
    vpc_ids = get_stack_value(stack, 'VpcId')

    return security_groups, subnet_ids, vpc_ids


def deploy_cluster(
    cluster_name,
    security_groups,
    subnet_ids,
    vpc_ids):
    """Deploy an EKS cluster.

    Parameters
    ----------
    name : str
        Name of cluster.

    Returns
    -------
    
    """
    try:
        logging.info(f"Checking if {cluster_name} already exists.")
        
        # Get stack.
        stack = cf.Stack(f'{cluster_name}')
        waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{cluster_name} already exists. No need to create a new one.")

    except:
        logging.info(f"{cluster_name} does not exist. creating a new one.")

        # Create a new stack.
        stack = cf.create_stack(
            StackName=f'{cluster_name}',
            TemplateBody=read_config_file("cluster.yaml"),
            Parameters=[
                {
                    "ParameterKey": "ClusterName",
                    "ParameterValue": cluster_name
                },
                {
                    "ParameterKey": "ControlPlaneSecurityGroup",
                    "ParameterValue": security_groups
                },
                {
                    "ParameterKey": "Subnets",
                    "ParameterValue": subnet_ids
                },
            ]
        )
        waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{cluster_name} successfully created")

    # Get response from eks.
    client = boto3.client('eks')
    response = client.describe_cluster(
        name=cluster_name
    )
    endpoint_url = response['cluster']['endpoint']
    ca_cert = response['cluster']['certificateAuthority']['data']

    return endpoint_url, ca_cert



def deploy_ondemand_workers(
    workers_name,
    cluster_name,
    security_groups,
    subnet_ids,
    vpc_ids):
    """
    Parameters
    ----------
    name : str
        Name of cluster.

    security_groups : 

    subnet_ids : 

    vpc_ids : 

    Returns
    -------
    node_arn : 

    node_instance_profile : 

    node_instance_role :

    node_security_group : 
    """
    try:
        logging.info(f"Checking if {workers_name} already exists.")

        stack = cf.Stack(f'{workers_name}')
        waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{workers_name} already exists. No need to create a new one.")

    except:

        logging.info(f"{workers_name} not found. Creating new workers.")
        stack = cf.create_stack(
            StackName=f'{workers_name}',
            TemplateURL=env.NODE_TEMPLATE_URL,
            Parameters=[
                {
                    "ParameterKey": "ClusterName",
                    "ParameterValue": cluster_name
                },
                {
                    "ParameterKey": "ClusterControlPlaneSecurityGroup",
                    "ParameterValue": security_groups
                },
                {
                    "ParameterKey": "Subnets",
                    "ParameterValue": subnet_ids
                },
                {
                    "ParameterKey": "VpcId",
                    "ParameterValue": vpc_ids
                },
            ] + read_param_file("ondemand-nodes.json"),
            Capabilities=[
                'CAPABILITY_IAM'
            ]
        )
        waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{workers_name} successfully created")

    node_arn = get_stack_value(stack, 'NodeInstanceRole')
    node_instance_profile = stack.Resource(
        'NodeInstanceProfile').physical_resource_id
    node_instance_role = stack.Resource(
        'NodeInstanceRole').physical_resource_id
    node_security_group = stack.Resource(
        'NodeSecurityGroup').physical_resource_id

    return (
        node_arn,
        node_instance_profile,
        node_instance_role,
        node_security_group
    )


def deploy_spot_instances(
    spot_instances_name,
    cluster_name,
    subnet_ids,
    node_instance_profile,
    node_instance_role,
    node_security_group):
    """
    Parameter
    ---------
    spot_instances_name : 

    cluster_name : 

    security_groups : 

    subnet_ids : 

    vpc_ids : 

    Returns
    -------
    """
    try:
        logging.info(f"Checking if {spot_instances_name} already exists.")
        stack = cf.Stack(f'{spot_instances_name}')
        waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{spot_instances_name} already exists. No need to create new ones.")

    except:

        logging.info(f"{spot_instances_name} not found. Creating new.")
        stack = cf.create_stack(
            StackName=f'{spot_instances_name}',
            TemplateBody=read_config_file("spot-nodes.yaml"),
            Parameters=[
                {
                    "ParameterKey": "ClusterName",
                    "ParameterValue": cluster_name
                },
                {
                    "ParameterKey": "Subnets",
                    "ParameterValue": subnet_ids
                },
                {
                    "ParameterKey": "NodeInstanceProfile",
                    "ParameterValue": node_instance_profile
                },
                {
                    "ParameterKey": "NodeInstanceRole",
                    "ParameterValue": node_instance_role
                },
                {
                    "ParameterKey": "NodeSecurityGroup",
                    "ParameterValue": node_security_group
                },
            ],
        )
        waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{spot_instances_name} successfully created.")



def deploy_utilities_stack(
    utilities_name,
    cluster_name,
    subnet_ids,
    node_security_group,
    ):
    """
    """
    try:
        stack = cf.Stack(utilities_name)
        waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

    except:
        stack = cf.create_stack(
            StackName=utilities_name, 
            TemplateBody=read_config_file("utilities.yaml"),
            Parameters=[
                {
                    "ParameterKey": "Subnets",
                    "ParameterValue": subnet_ids
                },
                {
                    "ParameterKey": "NodeSecurityGroup",
                    "ParameterValue": node_security_group
                }
            ]
        )
        waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

    efs_id = get_stack_value(stack, 'efsId')
    return efs_id


def write_auth_cm(node_arn):
    """
    """
    # Get admins
    admins = iam.get_group(GroupName="admin")["Users"]

    ## Apply ARN of instance role of worker nodes and apply to cluster
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    TEMPLATE_FILE = "aws-auth-cm.yaml.template"

    template = template_env.get_template(TEMPLATE_FILE)
    output_text = template.render(arn=node_arn, users=admins)

    auth_fname = 'aws-auth-cm.yaml'
    auth_path = os.path.join(get_deployment_path(), authfname)
    with open(auth_fname, 'w') as ofile:
        ofile.writelines(output_text)

    return admins, auth_fname


def write_efs_profivisioner(
    cluster_name,
    efs_id
    ):
    """
    """
    ## Apply fs-id, region, and clusterName to efs-provisioner
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "efs-provisioner.yaml.template"
    template = template_env.get_template(template_file)

    # Fill template
    output_text = template.render(
        clusterName=cluster_name,
        region=boto3.Session().region_name,
        efsSystemId=efs_id)

    # Write to config directory.
    fname = 'efs-provisioner.yaml'
    path = os.path.join(get_deployment_path(), fname)
    with open(path, 'w') as ofile:
        ofile.writelines(output_text)

