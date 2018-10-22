import pathlib

from kubeconf import KubeConf, get_kube_path()

from ..utils import helm, kubectl
from traitlets_paths import PurePath
from traitlets.config import Configurable
from traitlets import (
    default,
    Unicode
)
    
class Kubernetes(Configurable):
    """Kubernetes configuration system.
    """

    config_path = PurePath(
        help="Kube config path."
    ).tag(config=True)

    @default('kube_path')
    def _default_kube_path(self)
        """Default kube path."""
        return get_kube_path()

    context = Unicode(
        help='Kubectl context.'
    ).tag(config=True)

    @default('context')
    def _default_context(self):
        """Current context."""
        return self.conf.get_context()
        
    hub_helm_repo = Unicode(
        u'https://jupyterhub.github.io/helm-chart/',
        help="Jupyterhub Helm Chart repo."
    ).tag(config=True)

    def __init__(self, **traits):
        # Pass configurations to traitlets base class
        super().__init__(**traits)
        self.conf = KubeConf(path=self.config_path)
        self.conf.set_context(self.context)

    def add_deployment(
        self,
        name,
        server,
        certificate_authority_data,
        ):
        """Add a deployment to kubeconfig."""
        self.conf.open()
        self.conf.add_cluster(
            name,
            server,
            certificate_authority_data
        )
        self.conf.add_user(
            name
        )
        self.add_context(
            name,
            cluster_name=name,
            user_name=name,
        )

    def init_helm(self):
        """Initialize helm on provider."""
        # Setup helm (ServiceAccount) on the server
        kubectl(
            'create',
            'serviceaccount',
            'tiller',
            namespace='kube-system'
        )

        # Give the new ServiceAccount full permissions
        kubectl(
            'create',
            'clusterrolebinding',
            'tiller',
            clusterrole='cluster-admin',
            serviceaccount='kube-system:tiller'
        )

        # Initialize Helm
        helm(
            'init',
            '--service-account',
            'tiller'
        )

        # Secure the helm.
        kubectl(
            'patch',
            'deployment',
            'tiller-deploy',
            namespace='kube-system',
            type='json',
            patch='[{"op": "add", "path": "/spec/template/spec/containers/0/command", "value": ["/tiller", "--listen=localhost:44134"]}]'
        )

    def init_hub(self):
        """Make helm aware of Jupyterhub Helm repo."""
        # Point helm to jupyterhub repo.
        helm(
            "repo",
            "add",
            "jupyterhub",
            self.hub_helm_repo
        )

        helm(
            "repo",
            "update"
        )