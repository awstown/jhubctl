
from ..utils import kubectl, helm
from traitlets.config import Configurable
from traitlets import (
    Unicode,
    default
)

from .single import Hub

class HubList(Configurable):
    """JupyterHub.
    """

    def create(self, name):
        """Create a jupyterhub deployment on the cluster."""
        hub = Hub(namespace=name)
        hub.create()

    def get(self, name=None):
        """List all jupyterHubs.
        """
        
    def delete(self, name):
        """Delete Hub from Kubernetes Cluster
        """
        hub = Hub(namespace=name)
        hub.delete()
