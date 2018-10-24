
from ..utils import kubectl, helm
from traitlets.config import Configurable
from traitlets import (
    Unicode,
    default
)

class HubList(Configurable):
    """JupyterHub.
    """
    def initialize(self):
        """Initialize JupyterHub."""
        

    def create(self, name):
        """Create a jupyterhub deployment on the cluster."""

    def get(self):
        """Get all jupyterHubs.
        """
        