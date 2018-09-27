import subprocess
from .utils import get_kube_path


# class JupyterHubDeployment(object):

#     def __init__(self, hub_name, cluster_name):
#         self.hub_name = hub_name
#         self.cluster_name = cluster_name

#     def 


# def init_helm():


def deploy_hub(cluster_name):
    """"""
    # Get and random hex string.
    hex_str = subprocess.getoutput("openssl rand -hex 32")

    # Write hex string to file.
    helm("")


    hub_yaml = f'proxy:\n  secretToken: "{hex_str}"'
    hub_yaml_file = f"{cluster_name}-jupyterhub"
    hub_yaml_path = get_kube_path(hub_yaml_file)
    with open(hub_yaml_path, "w") as f:
        f.write(hub_yaml)

