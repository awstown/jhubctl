import os
import boto3
import botocore
import jinja2
import json
import subprocess
import logging
from pathlib import Path

from ..provider import Provider, update_progress

from ...utils import (
    read_config_file, 
    read_param_file,
    fill_template
)

CLIENT = boto3.client('cloudformation')
WAITER = CLIENT.get_waiter('stack_create_complete')
CLOUDFORMATION = boto3.resource('cloudformation')
IAM = boto3.client('iam')
EKS = boto3.client('eks')

# Constants
ROLE_TEMPLATE_URL = "https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-service-role.yaml"
VPC_TEMPLATE_URL = "https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-vpc-sample.yaml"
NODE_TEMPLATE_URL = "https://amazon-eks.s3-us-west-2.amazonaws.com/cloudformation/2018-08-30/amazon-eks-nodegroup.yaml"


class ResourceDoesNotExistError(Exception):
    """Resource does not exist."""


def raise_if_does_not_exist(resource):
    if does_resource_exist(resource) is False:
        raise ResourceDoesNotExistError


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


def get_stack(name):
    """Get stack from AWS's cloud formation."""
    try:
        stack = CLOUDFORMATION.Stack(f"{name}")
        WAITER.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)
        return stack
    except ResourceDoesNotExistError:
        raise ResourceDoesNotExistError("This stack doesn't exist yet.")


def get_stack_value(stack, key):
    """Get metadata value from a cloudformation stack."""
    for output in stack.outputs:
        if output['OutputKey'] == key:
            return output['OutputValue']


def deploy_eks_role(role_name):
    """Create an EKS Role on AWS for Jupyterhub Deployments with Kubernetes.

    Parameters
    ----------
    name : str 
        Name an EKS role.
    """
    # Deploy the role.
    try:
        logging.info(f"Checking to see if a {role_name} exists.\n")

        stack = CLOUDFORMATION.Stack(f"{role_name}")
        raise_if_does_not_exist(stack)

        logging.info(f"{role_name} found. No need to create a new one.\n")

    except ResourceDoesNotExistError:
        
        logging.info(
            f"{role_name} not found. Creating a new role name {role_name}.\n")

        # Create stack
        stack = CLOUDFORMATION.create_stack(
            StackName=f'{role_name}',
            TemplateURL=ROLE_TEMPLATE_URL,
            Capabilities=[
                'CAPABILITY_NAMED_IAM',
            ]
        )
        # Wait for role to be created.
        WAITER.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{role_name} succesfully created.")


def deploy_vpc(vpc_name):
    """
    
    Parameter
    ---------
    name : str 
        Name assigned to virtual private cloud (VPC).
    """
    try:
        logging.info(f"Checking if {vpc_name} already exists.")

        stack = CLOUDFORMATION.Stack(f"{vpc_name}")
        raise_if_does_not_exist(stack)

        logging.info(
            f"{vpc_name} already exists. No need to create a new one.")

    except:

        logging.info(
            f"{vpc_name} does not exist. Creating a new VPC named {vpc_name}.")

        stack = CLOUDFORMATION.create_stack(
            StackName=f"{vpc_name}",
            TemplateURL=VPC_TEMPLATE_URL,
            Parameters=read_param_file("aws", "vpc.json"),
        )
        WAITER.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{vpc_name} successfully created")


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
    """
    try:
        logging.info(f"Checking if {cluster_name} already exists.")

        # Get stack.
        stack = CLOUDFORMATION.Stack(f'{cluster_name}')
        WAITER.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(
            f"{cluster_name} already exists. No need to create a new one.")

    except:
        logging.info(f"{cluster_name} does not exist. creating a new one.")

        # Create a new stack.
        stack = CLOUDFORMATION.create_stack(
            StackName=f'{cluster_name}',
            TemplateBody=read_config_file("aws", "cluster.yaml"),
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
        WAITER.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{cluster_name} successfully created")


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
    """
    try:
        logging.info(f"Checking if {workers_name} already exists.")

        stack = CLOUDFORMATION.Stack(f'{workers_name}')
        WAITER.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(
            f"{workers_name} already exists. No need to create a new one.")

    except:

        logging.info(f"{workers_name} not found. Creating new workers.")
        stack = CLOUDFORMATION.create_stack(
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
            ] + read_param_file("aws", "ondemand-nodes.json"),
            Capabilities=[
                'CAPABILITY_IAM'
            ]
        )
        WAITER.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(f"{workers_name} successfully created")


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
    """
    try:
        logging.info(f"Checking if {spot_instances_name} already exists.")
        stack = CLOUDFORMATION.Stack(f'{spot_instances_name}')
        WAITER.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

        logging.info(
            f"{spot_instances_name} already exists. No need to create new ones.")

    except:

        logging.info(f"{spot_instances_name} not found. Creating new.")
        stack = CLOUDFORMATION.create_stack(
            StackName=f'{spot_instances_name}',
            TemplateBody=read_config_file("aws", "spot-nodes.yaml"),
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
        WAITER.wait(StackName=stack.name)
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
        stack = CLOUDFORMATION.Stack(utilities_name)
        WAITER.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)

    except:
        stack = CLOUDFORMATION.create_stack(
            StackName=utilities_name,
            TemplateBody=read_config_file("aws", "utilities.yaml"),
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
        WAITER.wait(StackName=stack.name)
        raise_if_does_not_exist(stack)


def teardown_stack(stack_name):
    """Teardown a stack."""
    try:
        logging.info(f"Checking that {stack_name} exists.\n")

        stack = CLOUDFORMATION.Stack(f"{stack_name}")
        raise_if_does_not_exist(stack)
        response = CLIENT.delete_stack(
            StackName=stack_name
        )
        logging.info(f"{stack_name} deleted.\n")

    except ResourceDoesNotExistError:
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

    # ---------- Attributes -------------
    # 
    # -----------------------------------    
     
    @property
    def security_groups(self):
        return get_stack_value(self.vpc_stack, "SecurityGroups")

    @property
    def subnet_ids(self):
        return get_stack_value(self.vpc_stack, "SubnetIds")

    @property
    def vpc_ids(self):
        return get_stack_value(self.vpc_stack, "VpcID")

    @property
    def endpoint_url(self):
        response = EKS.describe_cluster(name=self.cluster_name)
        return response['cluster']['endpoint']

    @property
    def ca_cert(self):
        response = EKS.describe_cluster(name=self.cluster_name)
        return response['cluster']['certificateAuthority']['data']

    @property
    def node_arn(self):
        return get_stack_value(self.workers_stack, "NodeInstanceRole")

    @property
    def node_instance_profile(self):
        return self.workers_stack.Resource('NodeInstanceProfile').physical_resource_id

    @property
    def node_instance_role(self):
        return self.workers_stack.Resource('NodeInstanceRole').physical_resource_id

    @property
    def node_security_group(self):
        return self.workers_stack.Resource('NodeSecurityGroup').physical_resource_id

    @property
    def efs_id(self):
        return get_stack_value(self.utilities_stack, 'efsId')

    @property
    def admins(self):
        """Admins of the cluster."""
        return IAM.get_group(GroupName="admin")["Users"]

    # ---------- Stacks -----------------
    # Cloud formation stacks.
    # -----------------------------------

    @property
    def role_stack(self):
        return get_stack(self.role_name)

    @property
    def vpc_stack(self):
        return get_stack(self.vpc_name)

    @property
    def workers_stack(self):
        return get_stack(self.workers_name)

    @property
    def spot_instances_stack(self):
        return get_stack(self.spot_instances_name)

    @property
    def utilities_stack(self):
        return get_stack(self.utilities_name)

    # ---------- Methods -----------------
    # 
    # -----------------------------------


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
        deploy_vpc(self.vpc_name)

    @update_progress
    def deploy_eks_cluster(self):
        deploy_eks_cluster(
            cluster_name=self.cluster_name,
            security_groups=self.security_groups,
            subnet_ids=self.subnet_ids,
            vpc_ids=self.vpc_ids
        )

    @update_progress
    def deploy_onedemand_workers(self):
        deploy_ondemand_workers(
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
        deploy_utilities_stack(
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

    def get_auth_yaml(self):
        """"""
        return fill_template(
            "aws-auth-cm.yaml.template",
            arn=self.node_arn,
            users=self.admins
        )
    def get_storage_yaml(self):
        """"""
        return fill_template(
            "efs-provisioner.yaml.template",
            clusterName=self.cluster_name,
            region=boto3.Session().region_name,
            efsSystemId=self.efs_id
        )
