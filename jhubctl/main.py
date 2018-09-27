import os
import click
import logging
import click_log

from . import providers
from . import kube
from . import hub

from .teardown import (
    teardown_jupyterhub_role,
    teardown_jupyterhub_vpc,
    teardown_jupyterhub_cluster,
    teardown_ondemand_workers,
    teardown_spot_instances,
    teardown_utilities
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
@click.option("--provider", default="AWS_EKS", help="Cloud provider to use.")
@click_log.simple_verbosity_option(logger)
def create_cluster(cluster_name, provider):
    """Create an Jupyterhub/EKS cluster."""
    # Load provider class.
    Provider = getattr(providers, provider)
    # Deploy cluster on provider.
    provider = Provider(cluster_name)
    provider.deploy_cluster()


@create.command("hub")
@click.argument("hub_name")
@click.option("--cluster", help="Cluster to use. Otherwise, will use the default kubectl env.")
@click_log.simple_verbosity_option(logger)
def create_hub(hub_name, cluster):
    """"""
    hub.deploy_jupyterhub()


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

        # 5. Teardown spot instances
        teardown_utilities(utilities_name)
        bar.update(6)



@cli.group()
@click_log.simple_verbosity_option(logger)
def describe():
    """Show details of a specific Jupyterhub deployment."""


@cli.command("list")
def list_clusters():
    pass

@cli.group()
@click_log.simple_verbosity_option(logger)
def config():
    """Export kubeconfig file to home dir..."""

@config.command("export-kubeconfig")
@click.argument("cluster_name")
def export_kubeconfig(cluster_name):
    """Exports kubeconfig for cluster_name to ~/.kube/kubeconfig-<cluster_name>
    """
