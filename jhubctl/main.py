import click

from .utils import kubectl, helm
from .deploy import (
    deploy_jupyterhub_role,
    deploy_jupyterhub_vpc,
    deploy_jupyterhub_cluster,
    deploy_ondemand_workers,
    deploy_spot_instances,
    deploy_utilities_stack,
    deploy_efs_profivisioner,
    write_auth_cm,
    write_kube_config
)

@click.group()
def cli():
    """jhubctl controls multiple Jupyterhub/EKS clusters."""

@cli.group()
def create():
    """Create resources for EKS Jupyterhub clusters."""

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

    # Create role.
    role = deploy_jupyterhub_role(role_name)

    # Create VPC.
    security_groups, subnet_ids, vpc_ids = deploy_jupyterhub_vpc(vpc_name) 

    # Create cluster
    endpoint_url, ca_cert = deploy_jupyterhub_cluster(
        cluster_name=cluster_name,
        security_groups=security_groups,
        subnet_ids=subnet_ids,
        vpc_ids=vpc_ids
    )

    # Create workers.
    node_arn, node_instance_profile, node_instance_role, node_security_group = deploy_ondemand_workers(
        workers_name,
        cluster_name,
        security_groups,
        subnet_ids,
        vpc_ids
    )

    # Create spot instances
    deploy_spot_instances(
        spot_instances_name,
        cluster_name,
        subnet_ids,
        node_instance_profile,
        node_instance_role,
        node_security_group
    )

    # Write kubectl configuration file.
    write_kube_config(
        cluster_name,
        endpoint_url,
        ca_cert
    )
    
    # Generate aws-auth-cm.yaml and apply to cluster.
    admins, aws_auth_fname = write_auth_cm(
        node_arn, 
    )

    efs_id = deploy_utilities_stack(
        utilities_name,
        cluster_name,
        subnet_ids,
        node_security_group
    )

    # apply aws authentication configuratio map
    kubectl("apply", "-f", "aws-auth-cm.yaml")

    # Create storage class.
    try:
        kubectl("apply", "-f", "storageclass.yaml")
    except:
        kubectl("delete", "storageclass", "gp2")

    try:
        kubectl('--namespace', 'kube-system', 'create', 'serviceaccount', 'tiller')
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

    deploy_efs_profivisioner(
        cluster_name,
        efs_id
    )
