import subprocess
from .utils import get_kube_path


def deploy_hub(cluster_name):
    """"""
    # Get and random hex string.
    hex_str = subprocess.getoutput("openssl rand -hex 32")
    hub_yaml = f'proxy:\n  secretToken: "{hex_str}"'


class JupyterHub(object):

    def __init__(self, release_name):
        self.release_name = release_name

    def create(self):
        """"""
        
    def teardown(self):
        """"""