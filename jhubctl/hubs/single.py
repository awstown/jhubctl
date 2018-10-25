import secrets

from jhubctl.utils import helm, kubectl
from traitlets.config import Configurable
from traitlets import default, Unicode

class Hub(Configurable):
    """Single instance of a JupyterHub deployment.
    """
    # Helm repository to pull charts.
    helm_repo = Unicode(
        u'https://jupyterhub.github.io/helm-chart/',
        help="Jupyterhub Helm Chart repo."
    ).tag(config=True)

    # Helm chart release name. If not given, use the 
    # namespace as the release name.
    release = Unicode(
        help="Release name"
    ).tag(config=True)

    @default('release')
    def _default_release(self):
        return self.namespace

    # Helm chart version to pull.
    version = Unicode(
        u'0.7.0',
        help='Helm Chart for Jupyterhub release.'
    ).tag(config=True)

    # Name to give to namespace.
    namespace = Unicode(
        help="Name of the Kubernetes namespace."
    ).tag(config=True)

    def __init__(self, namespace, release=None, **traits):
        self.namespace = namespace
        if release is None:
            self.release = namespace
        super().__init__(**traits)

    def get_security_yaml(self):
        """Create security YAML data."""
        # Get Token.
        token = secrets.token_hex(nbytes=32)
        # Turn token into yaml
        yaml = f'proxy:\n  secretToken: "{token}"'
        return yaml

    def get(self):
        """Get specific information about this hub."""
        output = helm("get", self.release)
        if output.returncode != 0:
            print("Something went wrong!")
            print(output.stderr)
        else:
            print(output.stdout)

    def create(self):
        """Create a single instance of notebook."""
        # Point to chart repo.
        out = helm(
            "repo",
            "add",
            "jupyterhub",
            self.helm_repo
        )
        out = helm("repo", "update")

        # Get token to secure Jupyterhub
        secret_yaml = self.get_security_yaml()

        # Get Jupyterhub.
        out = helm(
            "upgrade",
            "--install",
            self.release,
            "jupyterhub/jupyterhub",
            namespace=self.namespace,
            version=self.version,
            input=secret_yaml
        )
        if out.returncode != 0:
            print(out.stderr)
        else:
            print(out.stdout)

    def delete(self):
        """Delete a Jupyterhub."""
        # Delete the Helm Release
        out = helm(
            "delete",
            self.release,
            "--purge"
        )
        if out.returncode != 0:
            print(out.stderr)
        else:
            print(out.stdout)

        # Delete the Kubernetes namespace
        out = kubectl(
            "delete",
            "namespace",
            self.namespace
        )
        if out.returncode != 0:
            print(out.stderr)
        else:
            print(out.stdout)
