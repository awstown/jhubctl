import jinja2
from pathlib import Path

from .utils import get_template_dir

TEMPLATE_DIR = get_template_dir()


def kubectl(*args, **kwargs):
    return subprocess.check_call(('kubectl',) + args, **kwargs)


def helm(*args, **kwargs):
    return subprocess.check_call(('helm',) + args, **kwargs)


def write_kube_config(
        cluster_name,
        endpoint_url,
        ca_cert
    ):
    """
    """
    template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)
    TEMPLATE_FILE = "kubeconfig.yaml.template"
    template = template_env.get_template(TEMPLATE_FILE)

    output_text = template.render(
        endpoint_url=endpoint_url,
        ca_cert=ca_cert,
        cluster_name=cluster_name
    )

    config_path = f'{Path.home()}/.kube/kubeconfig-{cluster_name}'
    with open(config_path, 'w') as ofile:
        ofile.writelines(output_text)

    return config_path


def deploy_kube():
    """Use kubectl to deploy jupyterhub.
    """
    # apply aws authentication configuratio map
    kubectl("apply", "-f", "aws-auth-cm.yaml")

    # Create storage class.
    try:
        config_file = os.path.join(get_config_dir(), "storageclass.yaml")
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
    kubectl('-n', 'kube-system', 'apply', '-f', 'efs-provisioner.yaml')
