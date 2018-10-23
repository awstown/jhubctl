from ..utils import SubclassError
from traitlets.config import Configurable
from traitlets import (
    Unicode
)

class Provider(Configurable):
    """Base class for cloud providers supporting Kubernetes.
    """

    provider_type = Unicode(help="Provider type")
    provider_alias = Unicode(help="Simple alias pointing to this provider.")
    cluster_name = Unicode(help="Name of cluster.")

    def __init__(self, name, **traits):
        self.name = name
        super().__init__(**traits)

    def check_if_cluster_is_deployed(self):
        """Returns True if the cluster is deployed and available.
        """
        raise SubclassError

    def create(self):
        """Deploy a cluster configured for running Jupyterhub
        deployments on this provider.
        """
        raise SubclassError

    def delete(self):
        """Teardown a cluster running on this provider.
        """
        raise SubclassError

    def get_authorized_users_config(self):
        """Get yaml describing authorized users for the cluster.
        """
        raise SubclassError

    def get_storage_config(self):
        """Get yaml describing storage on cluster.
        """
        raise SubclassError

    def get_kubectl_config(self):
        """Get yaml describing the kubeconfig for this cluster.
        """
        raise SubclassError
