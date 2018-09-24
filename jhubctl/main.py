import click
import logging
import click_log

from .utils import kubectl, helm
from .deploy import (
    deploy_jupyterhub_role,
    deploy_jupyterhub_vpc,
    deploy_jupyterhub_cluster,
    deploy_ondemand_workers,
    deploy_spot_instances,
    deploy_utilities_stack,
    write_auth_cm,
    write_kube_config,
    write_efs_profivisioner
)

from .teardown import (
    teardown_jupyterhub_role,
    teardown_jupyterhub_vpc
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

    with click.progressbar(length=3) as bar:

        # 1. Create role.
        role = deploy_jupyterhub_role(role_name)
        bar.update(1)

        # 2. Create VPC.
        security_groups, subnet_ids, vpc_ids = deploy_jupyterhub_vpc(vpc_name) 
        bar.update(2)

        # 3. Create cluster
        endpoint_url, ca_cert = deploy_jupyterhub_cluster(
            cluster_name=cluster_name,
            security_groups=security_groups,
            subnet_ids=subnet_ids,
            vpc_ids=vpc_ids
        )
        bar.update(3)

    # # Create workers.
    # node_arn, node_instance_profile, node_instance_role, node_security_group = deploy_ondemand_workers(
    #     workers_name,
    #     cluster_name,
    #     security_groups,
    #     subnet_ids,
    #     vpc_ids
    # )

    # # Create spot instances
    # deploy_spot_instances(
    #     spot_instances_name,
    #     cluster_name,
    #     subnet_ids,
    #     node_instance_profile,
    #     node_instance_role,
    #     node_security_group
    # )

    # # Write kubectl configuration file.
    # write_kube_config(
    #     cluster_name,
    #     endpoint_url,
    #     ca_cert
    # )
    
    # # Generate aws-auth-cm.yaml and apply to cluster.
    # admins, aws_auth_fname = write_auth_cm(
    #     node_arn, 
    # )

    # efs_id = deploy_utilities_stack(
    #     utilities_name,
    #     cluster_name,
    #     subnet_ids,
    #     node_security_group
    # )

    # # apply aws authentication configuratio map
    # kubectl("apply", "-f", "aws-auth-cm.yaml")

    # # Create storage class.
    # try:
    #     kubectl("apply", "-f", "storageclass.yaml")
    # except:
    #     kubectl("delete", "storageclass", "gp2")

    # try:
    #     kubectl('--namespace', 'kube-system', 'create', 'serviceaccount', 'tiller')
    # except:
    #     kubectl('-n', 'kube-system', 'get', 'serviceaccount', 'tiller')

    # try:
    #     kubectl('create', 'clusterrolebinding', 'tiller',
    #             '--clusterrole=cluster-admin', '--serviceaccount=kube-system:tiller')
    # except:
    #     kubectl('get', 'clusterrolebinding', 'tiller')

    # # Inititalize Helm/Tiller for the cluster
    # helm('init', '--service-account', 'tiller')

    # kubectl('-n', 'kube-system', 'apply', '-f', 'efs-provisioner.yaml')

    # write_efs_profivisioner(
    #     cluster_name,
    #     efs_id
    # )

    # kubectl('-n', 'utilities', 'apply', '-f', 'efs-provisioner.yaml')


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

    with click.progressbar(length=3, label=f"Delete {cluster_name}...") as bar:

        # 1. Teardown role.
        teardown_jupyterhub_role(role_name)
        bar.update(1)

        # 2. Teardown VPC
        teardown_jupyterhub_vpc(vpc_name)
        bar.update(2)
