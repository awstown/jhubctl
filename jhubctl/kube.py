import os
import jinja2
import subprocess
from pathlib import Path

from .utils import get_template_path, get_config_path

TEMPLATE_DIR = get_template_path()

def kubectl(*args, **kwargs):
    """Construct a kubectl subprocess."""
    return subprocess.check_call(('kubectl',) + args, **kwargs)


def helm(*args, **kwargs):
    """Construct a helm subprocess."""
    return subprocess.check_call(('helm',) + args, **kwargs)


def write_kube_config(
        cluster_name,
        endpoint_url,
        ca_cert
    ):
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


def write_auth_cm(node_arn, admins):
    """
    """
    # Get admins
    admins = iam.get_group(GroupName="admin")["Users"]

    ## Apply ARN of instance role of worker nodes and apply to cluster
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    TEMPLATE_FILE = "aws-auth-cm.yaml.template"

    template = template_env.get_template(TEMPLATE_FILE)
    output_text = template.render(arn=node_arn, users=admins)

    return output_text

    
def write_efs_profivisioner(
    cluster_name,
    efs_id
    ):
    """
    """
    ## Apply fs-id, region, and clusterName to efs-provisioner
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    template_file = "efs-provisioner.yaml.template"
    template = template_env.get_template(template_file)

    # Fill template
    output_text = template.render(
        clusterName=cluster_name,
        region=boto3.Session().region_name,
        efsSystemId=efs_id)

    return output_text


def deploy_kube(
    cluster_name,
    node_arn,
    admins,
    efs_id
    ):
    """Use kubectl to deploy jupyterhub.
    """
    # Set the KUBECONFIG for this cluster
    kube_config_path = f'{Path.home()}/.kube/kubeconfig-{cluster_name}'
    os.environ["KUBECONFIG"] = kube_config_path

    # apply aws authentication configuration map
    authentication_map = write_auth_cm(node_arn, admins)
    subprocess.check_call([authentication_map, "|", "kubectl", "apply", "-f", "-"])

    # Create storage class.
    try:
        config_file = os.path.join(get_config_path(), "storageclass.yaml")
        kubectl("apply", "-f", config_file)
    except:
        kubectl("delete", "storageclass", "gp2")

    try:
        kubectl('--namespace', 'kube-system',
                'create', 'serviceaccount', 'tiller')
    except:
        kubectl('-n', 'kube-system', 'get', 'serviceaccount', 'tiller')

    try:
        kubectl('create', 'clusterrolebinding', 'tiller',
                '--clusterrole=cluster-admin', '--serviceaccount=kube-system:tiller')
    except:
        kubectl('get', 'clusterrolebinding', 'tiller')

    # Inititalize Helm/Tiller for the cluster
    helm('init', '--service-account', 'tiller')

    # apply aws authentication configuration map
    subprocess.check_call(
        [authentication_map, '|', 'kubectl', '-n', 'kube-system', 'apply', '-f', 'efs-provisioner.yaml'])
