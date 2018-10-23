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
        SingleHub()

    def get(self):
        """Get all jupyterHubs.
        """
        helm


class SingleHub(Configurable):
    """Single instance of a JupyterHub deployment.
    """

    helm_repo = Unicode(
        u'https://jupyterhub.github.io/helm-chart/',
        help="Jupyterhub Helm Chart repo."
    ).tag(config=True)

    release = Unicode(
        help="Release name"
    ).tag(config=True)

    version = Unicode(
        u'0.7.0',
        help='Helm Chart for Jupyterhub release.'
    ).tag(config=True)

    namespace = Unicode(
        help="Name of the namespace"
    ).tag(config=True)

    def create(self):
        """Create a single instance of notebook."""
        helm(
            "upgrade",
            "--install",
            self.release,
            "jupyterhub/jupyterhub",
            namespace=self.namespace,
            version=self.version,
        )

    def delete(self):
        """Delete a Jupyterhub"""

    
