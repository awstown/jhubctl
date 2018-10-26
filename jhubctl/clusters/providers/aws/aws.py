import os
import boto3
import botocore
import jinja2
import json
import subprocess
import logging
import pathlib

import tqdm

from traitlets import (
    Unicode,
    default
)
from ..base import Provider
from ....utils import get_template


CLIENT = boto3.client('cloudformation')
CREATE_WAITER = CLIENT.get_waiter('stack_create_complete')
DELETE_WAITER = CLIENT.get_waiter('stack_delete_complete')
CLOUDFORMATION = boto3.resource('cloudformation')
IAM = boto3.client('iam')
EKS = boto3.client('eks')


def stack_exists(name):
    """Use boto3 to check if a resource exists."""
    try:
        CLIENT.describe_stacks(StackName=name)
        return True
    except:
        return False


def get_stack(name):
    """Get stack from AWS's cloud formation."""
    stack_exists(name)
    stack = CLOUDFORMATION.Stack(f"{name}")
    return stack
 

def create_stack(
        stack_name,
        stack_template_path,
        parameters=None,
        capabilities=None
    ):
    # Create stack if it does not exist.
    if stack_exists(stack_name) is False:
        # Create stack
        options = {}
        if parameters is not None:
            options.update(Parameters=parameters)
        if capabilities is not None:
            options.update(Capabilities=capabilities)

        stack = CLOUDFORMATION.create_stack(
            StackName=stack_name,
            TemplateBody=get_template(stack_template_path),
            **options
        )
        # Wait for response.
        CREATE_WAITER.wait(StackName=stack.name)


def get_stack_value(stack, key):
    """Get metadata value from a cloudformation stack."""
    for output in stack.outputs:
        if output['OutputKey'] == key:
            return output['OutputValue']


def define_parameters(**parameters):
    """Get a list of parameters to pass to AWS boto call."""
    params = []
    for key, value in parameters.items():
        param = dict(ParameterKey=key, ParameterValue=value)
        params.append(param)
    return params


class AwsEKS(Provider):
    """AWS EKS configured for launching JupyterHub deployments."""
    # ------------------------------------------------------------------------
    # Configurable options
    # ------------------------------------------------------------------------

    provider_source = Unicode('Amazon Web Services EKS')
    provider_alias = Unicode('aws')

    @default('template_dir')
    def _default_template_dir(self):
        cwd = pathlib.Path(__file__).parent
        template_dir = cwd.joinpath('templates')
        return str(template_dir)

    # AWS Role NAme
    role_name = Unicode(
        help="AWS Role."
    ).tag(config=True)

    @default('role_name')
    def _default_role_name(self):
        return f'{self.name}-role'

    # Virtual private cloud name
    vpc_name = Unicode(
        help="Name of the virtual private cloud used by this deployment."
    ).tag(config=True)

    @default('vpc_name')
    def _default_vpc_name(self):
        return f'{self.name}-vpc'
        
    # Name of EKS cluster.
    cluster_name = Unicode(
        help="Name of the cluster"
    ).tag(config=True)

    @default('cluster_name')
    def _default_cluster_name(self):
        return f'{self.name}-cluster'

    # Name of node groups
    node_group_name = Unicode(
        help="Name of the node group setup to deploy jupyterhub instances."
    ).tag(config=True)

    @default('node_group_name')
    def _default_node_group_name(self):
        return f'{self.name}-node-group'

    spot_nodes_name = Unicode(
        help="Name of the spot nodes stack"
    ).tag(config=True)

    @default('spot_nodes_name')
    def _default_spot_nodes(self):
        return f'{self.name}-spot-nodes'

    utilities_name = Unicode(
        help="Name of the utilities stack"
    ).tag(config=True)

    @default('utilities_name')
    def _default_utilities_name(self):
        return f'{self.name}-utilities'

    # ------------------------------------------------------------------------
    # Provider Attributes
    # ------------------------------------------------------------------------

    @property
    def security_groups(self):
        return get_stack_value(self.vpc_stack, "SecurityGroups")

    @property
    def subnet_ids(self):
        return get_stack_value(self.vpc_stack, "SubnetIds")

    @property
    def vpc_ids(self):
        return get_stack_value(self.vpc_stack, "VpcId")

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
        return get_stack_value(self.node_group_stack, "NodeInstanceRole")

    @property
    def node_instance_profile(self):
        return self.node_group_stack.Resource('NodeInstanceProfile').physical_resource_id

    @property
    def node_instance_role(self):
        return self.node_group_stack.Resource('NodeInstanceRole').physical_resource_id

    @property
    def node_security_group(self):
        return self.node_group_stack.Resource('NodeSecurityGroup').physical_resource_id

    @property
    def efs_id(self):
        return get_stack_value(self.utilities_stack, 'efsId')

    @property
    def admins(self):
        """Admins of the cluster."""
        return IAM.get_group(GroupName="admin")["Users"]

    # ------------------------------------------------------------------------
    # Stacks
    # ------------------------------------------------------------------------

    @property
    def role_stack(self):
        return get_stack(self.role_name)

    @property
    def vpc_stack(self):
        return get_stack(self.vpc_name)

    @property
    def node_group_stack(self):
        return get_stack(self.node_group_name)

    @property
    def spot_nodes_stack(self):
        return get_stack(self.spot_nodes_name)

    @property
    def utilities_stack(self):
        return get_stack(self.utilities_name)

    @property
    def kube_user_data(self):
        """Extra data to pass to the kubectl user for this cluster.
        
        This can be used to map extra data to clusters in the kubeconf file.
        """
        return {
            'exec': {
                'apiVersion': 'client.authentication.k8s.io/v1alpha1',
                'command': 'aws-iam-authenticator',
                'args': ["token", "-i", f"{self.cluster_name}"]
            }
        }

    # ------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------

    def create(self):
        """Deploy a cluster on Amazon's EKS Service configured
        for Jupyterhub Deployments.
        """
        steps = [
            (self.create_role, (), {}),
            (self.create_vpc, (), {}),
            (self.create_cluster, (), {}),
            (self.create_node_group, (), {}),
            (self.create_spot_nodes, (), {}),
            (self.create_utilities, (), {}),
        ]
        # Execute creation.
        for step in tqdm.tqdm(steps, ncols=70):
            method, args, kwargs = step
            method(*args, **kwargs)

    def delete(self):
        """Delete a running cluster."""
        stacks = [
            self.utilities_name,
            self.spot_nodes_name,
            self.node_group_name,
            self.cluster_name,
            self.vpc_name,
            self.role_name
        ]
        # Execute creation.
        for stack in tqdm.tqdm(stacks, ncols=70):
            self.delete_stack(stack)

    def get_auth_config(self):
        """Return the Authorization Config Map (in yaml format) 
        for this cluster.
        """
        return self.get_template(
            'amazon-auth-cm.yaml',
            arn=self.node_arn,
            users=self.admins
        )

    def get_storage_config(self):
        """Return the Storage configuration (in yaml format) 
        for this cluster.
        """
        return self.get_template('amazon-storage-class.yaml')

    def get_template(self, template_name, **parameters):
        """Pull templates from the AWS templates folder"""
        template_path = pathlib.Path(self.template_dir).joinpath(template_name)
        return get_template(template_path, **parameters)

    def delete_stack(self, stack_name):
        """Teardown a stack."""
        get_stack(stack_name)
        CLIENT.delete_stack(
            StackName=stack_name
        )
        DELETE_WAITER.wait(StackName=stack_name)

    def create_stack(
        self, 
        stack_name,
        stack_template_name,
        parameters=None,
        capabilities=None
        ):
        """Create a stack using Amazon's Cloud formation"""
        # Build template_path
        stack_template_path = pathlib.Path(
            self.template_dir).joinpath(stack_template_name)

        # Create stack
        create_stack(
            stack_name,
            stack_template_path,
            parameters=parameters,
            capabilities=capabilities
        )

    def create_role(self):
        """Create an EKS Role configured to create JupyterHub Deployments
        on an EKS Provider.
        """
        self.create_stack(
            self.role_name,
            'amazon-eks-service-role.yaml',
            capabilities=['CAPABILITY_NAMED_IAM']
        )

    def create_vpc(self):
        """Create a virtual private cloud on Amazon's Web services configured
        for deploying JupyterHubs.
        """
        self.create_stack(
            self.vpc_name,
            'amazon-eks-vpc.yaml',
            parameters=define_parameters(
                VpcBlock="10.42.0.0/16",
                Subnet01Block="10.42.1.0/24",
                Subnet02Block="10.42.2.0/24",
                Subnet03Block="10.42.3.0/24"
            )
        )

    def create_cluster(self):
        """Creates a cluster on Amazon EKS .
        """
        self.create_stack(
            self.cluster_name,
            'amazon-eks-cluster.yaml',
            parameters=define_parameters(
                ClusterName=self.cluster_name,
                ControlPlaneSecurityGroup=self.security_groups,
                Subnets=self.subnet_ids
            )
        )

    def create_node_group(self):
        """Create on-demand node group on Amazon EKS.
        """
        self.create_stack(
            self.node_group_name,
            'amazon-eks-nodegroup.yaml',
            capabilities=['CAPABILITY_IAM'],
            parameters=define_parameters(
                ClusterName=self.cluster_name,
                ClusterControlPlaneSecurityGroup=self.security_groups,
                Subnets=self.subnet_ids,
                VpcId=self.vpc_ids,
                KeyName=self.ssh_key_name,
                NodeAutoScalingGroupMaxSize="1",
                NodeVolumeSize="100",
                NodeImageId="ami-0a54c984b9f908c81",
                NodeGroupName=f"{self.name} OnDemand Nodes"
            )
        )

    def create_spot_nodes(self):
        """Create spot nodes.
        """
        self.create_stack(
            self.spot_nodes_name,
            'amazon-spot-nodes.yaml',
            parameters=define_parameters(
                ClusterName=self.cluster_name,
                Subnets=self.subnet_ids,
                NodeInstanceProfile=self.node_instance_profile,
                NodeInstanceRole=self.node_instance_role,
                NodeSecurityGroup=self.node_security_group,

            )
        )

    def create_utilities(self):
        """Create utitilies stack.
        """
        self.create_stack(
            self.utilities_name,
            'amazon-utilities.yaml',
            parameters=define_parameters(
                Subnets=self.subnet_ids,
                NodeSecurityGroup=self.node_security_group
            )
        )
