import os
import click
import logging
import click_log

from . import aws
from . import kube
from . import hub

from .teardown import (
    teardown_jupyterhub_role,
    teardown_jupyterhub_vpc,
    teardown_jupyterhub_cluster,
    teardown_ondemand_workers,
    teardown_spot_instances
)

# Configure logging
logger = logging.getLogger(__name__)
click_log.basic_config(logger)

@click.group()
@click_log.simple_verbosity_option(logger)
def cli():
    """jhubctl controls multiple Jupyterhub/EKS clusters."""

@cli.group()
@click_log.simple_verbosity_option(logger)
def create():
    """Create an EKS Jupyterhub cluster."""

@create.command("cluster")
@click.argument("cluster_name")
def create_cluster(cluster_name):
    """Create an Jupyterhub/EKS cluster.
    """

    # Deploy the role.
    role_name = f"{cluster_name}-role"
    vpc_name = f"{cluster_name}-vpc"
    cluster_name = f"{cluster_name}-cluster"
    workers_name = f"{cluster_name}-ondemand-workers"
    spot_instances_name = f"{cluster_name}-spot-nodes"
    utilities_name = f"{cluster_name}-utilities"


    with click.progressbar(length=9, label=f"Creating {cluster_name}...") as bar:

        # 1. Create role.
        role = aws.deploy_eks_role(role_name)
        bar.update(1)

        # 2. Create VPC.
        security_groups, subnet_ids, vpc_ids = aws.deploy_vpc(vpc_name) 
        bar.update(2)

        # 3. Create cluster
        endpoint_url, ca_cert = aws.deploy_cluster(
            cluster_name=cluster_name,
            security_groups=security_groups,
            subnet_ids=subnet_ids,
            vpc_ids=vpc_ids
        )
        bar.update(3)

        # 4. Create workers.
        node_arn, node_instance_profile, node_instance_role, node_security_group = aws.deploy_ondemand_workers(
            workers_name,
            cluster_name,
            security_groups,
            subnet_ids,
            vpc_ids
        )
        bar.update(4)

        # 5. Create spot instances
        aws.deploy_spot_instances(
            spot_instances_name,
            cluster_name,
            subnet_ids,
            node_instance_profile,
            node_instance_role,
            node_security_group
        )
        bar.update(5)

        # 6. Setup utilities.
        efs_id = aws.deploy_utilities_stack(
            utilities_name,
            cluster_name,
            subnet_ids,
            node_security_group
        )
        bar.update(6)

        # Generate aws-auth-cm.yaml and apply to cluster.
        aws.write_auth_cm(node_arn)

        # 
        aws.write_efs_profivisioner(
            cluster_name,
            efs_id
        )
        bar.update(7)

        # Configure Kubectl
        kubectl_config_path = kube.write_kube_config(
            cluster_name,
            endpoint_url,
            ca_cert
        )

        os.environ["KUBECONFIG"] = kubectl_config_path

        kube.deploy_kube()
        bar.update(8)

        hub.deploy_jupyterhub()
        bar.update(9)



@cli.group()
@click_log.simple_verbosity_option(logger)
def delete():
    """Delete an EKS Jupyterhub cluster."""


@delete.command("cluster")
@click.argument("cluster_name")
def delete_cluster(cluster_name):
    """"""
    # Deploy the role.
    role_name = f"{cluster_name}-role"
    vpc_name = f"{cluster_name}-vpc"
    cluster_name = f"{cluster_name}-cluster"
    workers_name = f"{cluster_name}-ondemand-workers"
    spot_instances_name = f"{cluster_name}-spot-nodes"
    utilities_name = f"{cluster_name}-utilities"

    with click.progressbar(length=5, label=f"Delete {cluster_name}...") as bar:

        # 1. Teardown role.
        teardown_jupyterhub_role(role_name)
        bar.update(1)

        # 2. Teardown VPC
        teardown_jupyterhub_vpc(vpc_name)
        bar.update(2)

        # 3. Teardown Cluster
        teardown_jupyterhub_cluster(cluster_name)
        bar.update(3)

        # 4. Teardown Workers
        teardown_ondemand_workers(workers_name)
        bar.update(4)

        # 5. Teardown spot instances
        teardown_spot_instances(spot_instances_name)
        bar.update(5)




@cli.group()
@click_log.simple_verbosity_option(logger)
def describe():
    """Show details of a specific Jupyterhub deployment."""


@cli.command("list")
def list_clusters():
    pass