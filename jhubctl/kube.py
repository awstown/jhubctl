import os
import jinja2
import subprocess
from pathlib import Path

from .utils import get_template_path, get_config_path

TEMPLATE_DIR = get_template_path()

def write_kube_config(
    cluster_name,
    endpoint_url,
    ca_cert):
    """Write a kubectl config file to ~/.kube"""
    # Load kubeconfig template.
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    TEMPLATE_FILE = "kubeconfig.yaml.template"
    template = template_env.get_template(TEMPLATE_FILE)

    # Fill template with given parameters.
    output_text = template.render(
        endpoint_url=endpoint_url,
        ca_cert=ca_cert,
        cluster_name=cluster_name
    )

    # Write configuration to .kube directory.
    config_path = f'{Path.home()}/.kube/kubeconfig-{cluster_name}'
    with open(config_path, 'w') as ofile:
        ofile.writelines(output_text)

    return config_path


def kubectl(*args, config_yaml=None, **options):
    """Runs a kubectl command and returns the stdout as a string
    """
    line = ["kubectl"]
    for key, value in options.items():
        if len(key) == 1:
            lines += [f"-{key}", value]
        else:
            lines += [f"--{key}", value]

    # Add yaml string as input to command
    if config_yaml is not None:
        line = [config_yaml, "|"] + line + ["-f", "-"]

    output = subprocess.run(line)
    return output.stdout.decode('utf-8')


def helm(*args, config_yaml=None, **options):
    """Runs a helm command and returns the stdout as a string
    """
    line = ["helm"]
    for key, value in options.items():
        if len(key) == 1:
            lines += [f"-{key}", value]
        else:
            lines += [f"--{key}", value]

    # Add yaml string as input to command
    if config_yaml is not None:
        line = [config_yaml, "|"] + line + ["-f", "-"]

    output = subprocess.run(line)
    return output.stdout.decode('utf-8')


class KubernetesCluster(object):

    def __init__(self, kubectl_config):
        self.kubectl_config = kubectl_config

    def set_auth(self, auth_yaml):
        """Set the auth_group for Kubernetes cluster from the cluster provider."""
        kubectl('apply', config_yaml=auth_yaml)

    def set_storage(self, storage_yaml):
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
        helm('init', serviceaccount='tiller')

        # Secure helm
        kubectl('patch', 'deployment', 'tiller-deploy', 
            namespace='kube-system', 
            type='json',
            patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command",'
                  '"value": ["/tiller", "--listen=localhost:44134"]}]')

    def export_kubectl(self):
        """"""

    @property
    def context(self):
        return kubectl("config", "get-context")
