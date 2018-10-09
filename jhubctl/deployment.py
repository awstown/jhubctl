from . import providers
from .kube import KubernetesCluster

class Deployment(object):
    """Deployment class.
    """
    def __init__(self, name, provider_name):
        self.name = name
        self.provider_name = provider_name
        
        # Get provider object.
        Provider = getattr(providers, self.provider_name)
        self.provider = Provider(self.name)

        # Attach kubernetes to the deployment.
        self.kube = KubernetesCluster(self.name)

    def deploy(self):
        self.setup_cluster()
        self.setup_kubernetes()
        
    def setup_cluster(self):
        self.provider.deploy_cluster()

    def setup_kubernetes(self):
        """"""
        # Setup kubernetes.
        self.kube.setup(
            self.provider.get_kube_yaml(),
            self.provider.get_auth_yaml(),
            self.provider.get_storage_yaml()
        )

    def teardown(self):
        self.kube.teardown()
        self.provider.teardown_cluster()

    
    def create_hub(self, hub_name):
        self.kube.create_hub(hub_name)
