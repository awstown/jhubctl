import os
import boto3
import jinja2
import json
import subprocess
import logging
from pathlib import Path

from . import aws
from . import env
from .utils import (
    kubectl,
    helm,
    get_config_dir,
    get_stack_value, 
    get_template_dir, 
    read_config_file, 
    read_param_file,
    raise_if_does_not_exist,
    ResourceDoesNotExistError
)

TEMPLATE_DIR = get_template_dir()

def deploy_jupyterhub_role(role_name):
    """Create an EKS Role on AWS for Jupyterhub Deployments with Kubernetes.

    Parameters
    ----------
    name : str 
        Name of jupyterhub role.

    Return
    ------
    role_arn : str
    """ 
    # Deploy the role.
    try:
        logging.info(f"Checking to see if a {role_name} exists.\n")

        stack = aws.cf.Stack(f"{role_name}")
        raise_if_does_not_exist(stack)

        logging.info(f"{role_name} found. No need to create a new one.\n")
    except ResourceDoesNotExistError:
        logging.info(f"{role_name} not found. Creating a new role name {role_name}.\n")

        # Create stack
        stack = aws.cf.create_stack(
            StackName=f'{role_name}',
            TemplateURL=env.ROLE_TEMPLATE_URL,
            Capabilities=[
                'CAPABILITY_NAMED_IAM',
            ]
        )
        # Wait for role to be created.
        aws.waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{role_name} succesfully created.")

    role_arn = get_stack_value(stack, "RoleArn")

    return role_arn


def deploy_jupyterhub_vpc(vpc_name):
    """
    
    Parameter
    ---------
    name : str 
        Name of Jupyterhub vpc.

    Returns
    -------
    security_groups: 

    subnet_ids : 

    vpc_ids : 
    """
    try:
        logging.info(f"Checking if {vpc_name} already exists.")

        stack = aws.cf.Stack(f"{vpc_name}")
        raise_if_does_not_exist(stack)

        logging.info(f"{vpc_name} already exists. No need to create a new one.")

    except:

        logging.info(f"{vpc_name} does not exist. Creating a new VPC named {vpc_name}.")

        stack = aws.cf.create_stack(
            StackName=f"{vpc_name}",
            TemplateURL=env.VPC_TEMPLATE_URL,
            Parameters=read_param_file("vpc.json"),
        )
        aws.waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{vpc_name} successfully created")

    # Rip out necessary data for moving forward.
    security_groups = get_stack_value(stack, 'SecurityGroups')
    subnet_ids = get_stack_value(stack, 'SubnetIds')
    vpc_ids = get_stack_value(stack, 'VpcId')

    return security_groups, subnet_ids, vpc_ids


def deploy_jupyterhub_cluster(
    cluster_name,
    security_groups,
    subnet_ids,
    vpc_ids):
    """Deploy a jupyterhub cluster.

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
        stack = aws.cf.Stack(f'{cluster_name}')
        aws.waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{cluster_name} already exists. No need to create a new one.")

    except:
        logging.info(f"{cluster_name} does not exist. creating a new one.")

        # Create a new stack.
        stack = aws.cf.create_stack(
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
        aws.waiter.wait(StackName=stack.name)
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

        stack = aws.cf.Stack(f'{workers_name}')
        aws.waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{workers_name} already exists. No need to create a new one.")

    except:

        logging.info(f"{workers_name} not found. Creating new workers.")
        stack = aws.cf.create_stack(
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
        aws.waiter.wait(StackName=stack.name)
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
        stack = aws.cf.Stack(f'{spot_instances_name}')
        aws.waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{spot_instances_name} already exists. No need to create new ones.")

    except:

        logging.info(f"{spot_instances_name} not found. Creating new.")
        stack = aws.cf.create_stack(
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
        aws.waiter.wait(StackName=stack.name)
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
        stack = aws.cf.Stack(utilities_name)
        aws.waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

    except:
        stack = aws.cf.create_stack(
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
        aws.waiter.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

    efs_id = get_stack_value(stack, 'efsId')
    return efs_id


def write_kube_config(
    cluster_name,
    endpoint_url,
    ca_cert):
    """
    """
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    TEMPLATE_FILE = "kubeconfig.yaml.template"
    template = template_env.get_template(TEMPLATE_FILE)

    output_text = template.render(
        endpoint_url=endpoint_url,
        ca_cert=ca_cert,
        cluster_name=cluster_name)

    config_path = f'{Path.home()}/.kube/kubeconfig-{cluster_name}'
    with open(config_path, 'w') as ofile:
        ofile.writelines(output_text)

    return config_path


def write_auth_cm(node_arn):
    """
    """
    # Get admins
    admins = aws.iam.get_group(GroupName="admin")["Users"]

    ## Apply ARN of instance role of worker nodes and apply to cluster
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    TEMPLATE_FILE = "aws-auth-cm.yaml.template"

    template = template_env.get_template(TEMPLATE_FILE)
    output_text = template.render(arn=node_arn, users=admins)

    auth_fname = 'aws-auth-cm.yaml'
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

    output_text = template.render(clusterName=cluster_name,
                                 region=boto3.Session().region_name,
                                 efsSystemId=efs_id)

    with open('efs-provisioner.yaml', 'w') as ofile:
        ofile.writelines(output_text)


def deploy_hub():
    """Use kubectl to deploy jupyterhub.
    """

    # apply aws authentication configuratio map
    kubectl("apply", "-f", "aws-auth-cm.yaml")

    # Create storage class.
    try:
        config_file = os.path.join(get_config_dir(), "storageclass.yaml")
        kubectl("apply", "-f", config_file)
    except:
        kubectl("delete", "storageclass", "gp2")

    try:
        kubectl('--namespace', 'kube-system',
                'create', 'serviceaccount', 'tiller')
    except:
        kubectl('-n', 'kube-system', 'get', 'serviceaccount', 'tiller')

    try:
        kubectl('create', 'clusterrolebinding', 'tiller',
                '--clusterrole=cluster-admin', '--serviceaccount=kube-system:tiller')
    except:
        kubectl('get', 'clusterrolebinding', 'tiller')

    # Inititalize Helm/Tiller for the cluster
    helm('init', '--service-account', 'tiller')
    kubectl('-n', 'kube-system', 'apply', '-f', 'efs-provisioner.yaml')

    kubectl()