import os
import click
import logging
import click_log

from . import providers
from . import kube
from . import hub

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
@click.option("--provider", default="AWS_EKS", help="Cloud provider to use.")
def delete_cluster(cluster_name):
    """"""
    """Create an Jupyterhub/EKS cluster."""
    # Load provider class.
    Provider = getattr(providers, provider)
    # Deploy cluster on provider.
    provider = Provider(cluster_name)
    provider.teardown_cluster()


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
