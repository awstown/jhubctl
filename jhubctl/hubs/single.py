import secrets

from jhubctl.utils import helm, kubectl
from traitlets.config import Configurable
from traitlets import Unicode

class Hub(Configurable):
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
        help="Name of the Kubernetes namespace."
    )

    def __init__(self, namespace, **traits):
        self.namespace = namespace
        super().__init__(**traits)

    def get_security_yaml(self):
        """Create security YAML data."""
        # Get Token.
        token = secrets.token_hex(nbytes=32)
        # Turn token into yaml
        yaml = f'proxy:\n  secretToken: "{token}"'
        return yaml

    def create(self):
        """Create a single instance of notebook."""
        # Point to chart repo.
        helm(
            "repo"
            "add",
            "jupyterhub",
            self.helm_repo
        )
        helm("repo", "update")
        
        # Get token to secure Jupyterhub
        secret_yaml = self.get_security_yaml()

        # Get Jupyterhub.
        helm(
            "upgrade",
            "--install",
            self.release,
            "jupyterhub/jupyterhub",
            namespace=self.namespace,
            version=self.version,
            config_yaml=secret_yaml
        )

    def delete(self):
        """Delete a Jupyterhub"""
