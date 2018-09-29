from .kube import KubernetesCluster

class Deployment(object):
    """Deployment class.
    """
    def __init__(self, name, ProviderClass):
        self.provider = ProviderClass(name)


    def deploy_cluster(self):


    def setup_kubernetes():
        self.kubernetes.setup(
            self.provider.
        )