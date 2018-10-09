import os
import jinja2
import subprocess
from pathlib import Path
from .utils import fill_template, external_cli


kubectl = external_cli("kubectl")
helm = external_cli("helm")


class KubernetesCluster(object):
    """Setup Kubernetes cluster.

    1. Writes a kubeconfig.
    2. Add the path KUBECONFIG in your Bash profile
    """
    def __init__(
        self, 
        context_name):
        self.context_name = context_name

    def setup(
        self,
        kube_yaml,
        auth_yaml,
        storage_yaml):
        """Setup the kubernetes cluster."""
        self.setup_kubeconfig(kube_yaml)
        self.setup_auth(auth_yaml)
        self.setup_storage(storage_yaml)
        self.setup_helm()

    def teardown(self):
        kubectl('delete', 'namespace', self.context_name)

    def check_kubeconfig(self):
        """Check that a kubeconfig exists for this cluster."""


    def setup_kubeconfig(self, kube_yaml):
        """Write a kubectl config file to ~/.kube"""
        # Write configuration to .kube directory.
        config_path = f'{Path.home()}/.kube/config-{self.context_name}'

        with open(config_path, 'w') as ofile:
            ofile.writelines(kube_yaml)

        os.environ['KUBECONFIG'] = config_path

        self.set_context()

    def export_kubeconfig(self):
        """Write kubeconfig to path."""
        line = f'export KUBECONFIG=$KUBECONFIG:$HOME/.kube/config-{self.context_name}'
        raise Exception("Not implemented.")

    def set_context(self):
        """Set the kubectl context."""
        print(kubectl('config', 'use-context', self.context_name))

    def setup_auth(self, auth_yaml):
        """Set the auth_group for Kubernetes cluster from the cluster provider."""
        kubectl('apply', config_yaml=auth_yaml)

    def setup_storage(self, storage_yaml):
        """Set the storage class for the Kubernetes cluster."""
        kubectl('apply', config_yaml=storage_yaml)

    def setup_helm(self):
        # Set up a ServiceAccount for tiller
        kubectl('create', 'serviceaccount', 'tiller', namespace='kube-system')

        # Give the service account full permissions to manage the cluster.
        kubectl('create', 'clusterrolebinding', 'tiller', 
            clusterrole='cluster-admin', 
            serviceaccount='kube-system:tiller'
        )

        # Initialize helm and tiller.
        helm('init', '--service-account', 'tiller')

        # Secure helm
        kubectl('patch', 'deployment', 'tiller-deploy', 
            namespace='kube-system', 
            type='json',
            patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command",'
                  '"value": ["/tiller", "--listen=localhost:44134"]}]')

    def setup_jupyterhub(self):
        """Install Jupyterhub."""
        # Add the jupyterhub repo.
        helm('repo', 'add', 'jupyterhub', 'https://jupyterhub.github.io/helm-chart/')

        # Update the repo
        helm('repo', 'update')

    def create_hub(self, hub_name, version='0.7.0'):
        """Create a hub"""
        # Get and random hex string.
        hex_str = subprocess.getoutput("openssl rand -hex 32")

        # Create a release.
        helm('upgrade', 
            install=hub_name, 
            namespace='default',
            version=version,
            set=f'proxy.secretToken={hex_str}'
        )

    def delete_hub(self, hub_name):
        """Delete hub."""
        helm('delete', hub_name, '--purge')

    def list_hubs(self):
        """List hubs."""
        helm('list', namespace='default')
