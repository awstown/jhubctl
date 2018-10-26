import pathlib
from ...utils import SubclassError
from traitlets.config import Configurable
from traitlets import (
    Unicode,
    Dict,
    default
)

class Provider(Configurable):
    """Base class for Kubernetes Cluster providers.

    To create a new provider, inherit this class and 
    replace the folowing traits and methods with the 
    logic that is appropriate for the provider.

    We recommend creating a new folder for that provider
    where all templates can be grouped.
    """
    # Specific type of the provider
    provider_type = Unicode(help="Provider type")

    # An alias for the provider. No spaces or hyphens. Underscores instead.
    provider_alias = Unicode(help="Simple alias pointing to this provider.")

    # 
    cluster_name = Unicode(help="Name of cluster.")

    # Path to templates for this provider.
    template_dir = Unicode(
        help="Path to template"
    ).tag(config=True)

    ssh_key_name = Unicode(
        help='User SSH key name'
    ).tag(config=True)

    @property
    def kube_user_data(self):
        """Extra data to pass to the kubectl user for this cluster.
        
        This can be used to map extra data to clusters in the kubeconf file.
        """
        return None

    def __init__(self, name, **traits):
        self.name = name
        super().__init__(**traits)

    def check_if_cluster_is_deployed(self):
        """Returns True if the cluster is deployed and available.
        """
        raise SubclassError("Must be implemented in a subclass.")

    def create(self):
        """Deploy a cluster configured for running Jupyterhub
        deployments on this provider.
        """
        raise SubclassError("Must be implemented in a subclass.")

    def delete(self):
        """Teardown a cluster running on this provider.
        """
        raise SubclassError("Must be implemented in a subclass.")

    def get_auth_config(self):
        """Get yaml describing authorized users for the cluster.
        """
        raise SubclassError("Must be implemented in a subclass.")

    def get_storage_config(self):
        """Get yaml describing storage on cluster.
        """
        raise SubclassError("Must be implemented in a subclass.")
