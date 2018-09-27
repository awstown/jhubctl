import os
import boto3
import botocore
import jinja2
import json
import subprocess
import logging
from pathlib import Path

from .provider import Provider, update_progress

from ..utils import (
    get_config_path,
    get_kube_path,
    get_template_path,
    read_config_file, 
    read_param_file,
)

client = boto3.client('cloudformation')
waiter = client.get_waiter('stack_create_complete')
cf = boto3.resource('cloudformation')
iam = boto3.client('iam')

# Constants
ROLE_TEMPLATE_URL = "https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-service-role.yaml"
VPC_TEMPLATE_URL = "https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-vpc-sample.yaml"
NODE_TEMPLATE_URL = "https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-nodegroup.yaml"


class ResourceDoesNotExistError(Exception):
    """Resource does not exist."""


def raise_if_does_not_exist(resource):
    if does_resource_exist(resource) is False:
        raise ResourceDoesNotExistError


def get_stack_value(stack, key):
    for output in stack.outputs:
        if output['OutputKey'] == key:
            return output['OutputValue']


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
        logging.info(
            f"{role_name} not found. Creating a new role name {role_name}.\n")

        # Create stack
        stack = cf.create_stack(
            StackName=f'{role_name}',
            TemplateURL=ROLE_TEMPLATE_URL,
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

        logging.info(
            f"{vpc_name} already exists. No need to create a new one.")

    except:

        logging.info(
            f"{vpc_name} does not exist. Creating a new VPC named {vpc_name}.")

        stack = cf.create_stack(
            StackName=f"{vpc_name}",
            TemplateURL=VPC_TEMPLATE_URL,
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


def deploy_eks_cluster(
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

        logging.info(
            f"{cluster_name} already exists. No need to create a new one.")

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

        logging.info(
            f"{workers_name} already exists. No need to create a new one.")

    except:

        logging.info(f"{workers_name} not found. Creating new workers.")
        stack = cf.create_stack(
            StackName=f'{workers_name}',
            TemplateURL=NODE_TEMPLATE_URL,
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

        logging.info(
            f"{spot_instances_name} already exists. No need to create new ones.")

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


def teardown_stack(stack_name):
    """Teardown a stack."""
    try:
        logging.info(f"Checking that {stack_name} exists.\n")

        stack = cf.Stack(f"{stack_name}")
        raise_if_does_not_exist(stack)
        response = client.delete_stack(
            StackName=stack_name
        )
        logging.info(f"{stack_name} deleted.\n")

    except aws.ResourceDoesNotExistError:
        logging.info(f"{stack_name} does not exist.\n")


class AWS_EKS(Provider):
    """AWS EKS Cluster.

    Parameters
    ----------
    name : str
        Name of the cluster.
    """
    def __init__(self, name):
        super(AWS_EKS, self).__init__(name)

        self.role_name = f"{name}-role"
        self.vpc_name = f"{name}-vpc"
        self.workers_name = f"{name}-ondemand-workers"
        self.spot_instances_name = f"{name}-spot-nodes"
        self.utilities_name = f"{name}-utilities"

        self._security_groups = None
        self._subnet_ids = None
        self._vpc_ids = None
        self._endpoint_url = None
        self._ca_cert = None
        self._node_arn = None
        self._node_instance_profile = None
        self._node_instance_role = None
        self._node_security_group = None
        self._efs_ids = None


    # ------ STill need to write protect for these attributes ------
    @property
    def security_groups(self):
        return self._security_groups

    @property
    def subnet_ids(self):
        return self._subnet_ids

    @property
    def vpc_ids(self):
        return self._vpc_ids

    @property
    def endpoint_url(self):
        return self._endpoint_url

    @property
    def ca_cert(self):
        return self._ca_cert

    @property
    def node_arn(self):
        return self._node_arn

    @property
    def node_instance_profile(self):
        return self._node_instance_profile

    @property
    def node_instance_role(self):
        return self._node_instance_role

    @property
    def node_security_group(self):
        return self._node_security_group

    @property
    def efs_ids(self):
        return self._efs_ids

    def deploy_cluster(self, progressbar=True):
        """Deploy an AWS EKS instance configured for JupyterHub deployments.
        """
        if progressbar:
            self.reset_progressbar(length=6)

        # 1. Create role.
        self.deploy_eks_role()

        # 2. Create VPC.
        self.deploy_vpc()

        # 3. Create cluster
        self.deploy_eks_cluster()

        # 4. Create workers.
        self.deploy_onedemand_workers()

        # 5. Create spot instances
        self.deploy_spot_instances()

        # 6. Setup utilities.
        self.deploy_utilities_stack()

    @update_progress
    def deploy_eks_role(self):
        deploy_eks_role(self.role_name)

    @update_progress
    def deploy_vpc(self):
        # 2. Create VPC.
        (self._security_groups,
         self._subnet_ids,
         self._vpc_ids) = deploy_vpc(self.vpc_name)

    @update_progress
    def deploy_eks_cluster(self):
        self._endpoint_url, self._ca_cert = deploy_eks_cluster(
            cluster_name=self.cluster_name,
            security_groups=self.security_groups,
            subnet_ids=self.subnet_ids,
            vpc_ids=self.vpc_ids
        )

    @update_progress
    def deploy_onedemand_workers(self):
        (self._node_arn,
         self._node_instance_profile,
         self._node_instance_role,
         self._node_security_group) = deploy_ondemand_workers(
            self.workers_name,
            self.cluster_name,
            self.security_groups,
            self.subnet_ids,
            self.vpc_ids
        )

    @update_progress
    def deploy_spot_instances(self):
        deploy_spot_instances(
            self.spot_instances_name,
            self.cluster_name,
            self.subnet_ids,
            self.node_instance_profile,
            self.node_instance_role,
            self.node_security_group
        )

    @update_progress
    def deploy_utilities_stack(self):
        self._efs_id = deploy_utilities_stack(
            self.utilities_name,
            self.cluster_name,
            self.subnet_ids,
            self.node_security_group
        )

    def teardown_cluster(self, progressbar=True):
        """Teardown an AWS EKS cluster."""
        if progressbar:
            self.reset_progressbar(length=6)
        self.teardown_stack(self.utilities_name)
        self.teardown_stack(self.spot_instances_name)
        self.teardown_stack(self.workers_name)
        self.teardown_stack(self.cluster_name)
        self.teardown_stack(self.vpc_name)
        self.teardown_stack(self.role_name)


    @update_progress
    def teardown_stack(self, stack_name):
        teardown_stack(stack_name)
