from ..base import Provider

class MockProvider(Provider):
    
    provider_source = Unicode(u'mock')
    provider_alias = Unicode(u'mock')
    cluster_name = Unicode(u'')

    def check_if_cluster_is_deployed(self):
        """Returns True if the cluster is deployed and available.
        """
        return True

    def deploy(self):
        """Deploy a cluster configured for running Jupyterhub
        deployments on this provider.
        """
        pass

    def teardown(self):
        """Teardown a cluster running on this provider.
        """
        pass

    def get_authorized_users_config(self):
        """Get yaml describing authorized users for the cluster.
        """
        return None

    def get_storage_config(self):
        """Get yaml describing storage on cluster.
        """
        return None

    def get_kubectl_config(self):
        """Get yaml describing the kubeconfig for this cluster.
        """
        return None
