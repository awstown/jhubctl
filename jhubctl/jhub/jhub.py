from ..utils import kubectl, helm
from traitlets.config import Configurable
from traitlets import (
    Unicode,
    default
)

class Hub(Configurable):
    """JupyterHub.
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
        """Create a jupyterhub deployment on the cluster."""
        helm(
            "upgrade",
            "--install",
            self.release,
            "jupyterhub/jupyterhub",
            namespace=self.namespace,
            version=version,
        )
