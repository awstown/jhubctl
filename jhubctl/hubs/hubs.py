
from ..utils import kubectl, helm
from .single import Hub

class HubList(object):
    """Manage a list of jhubctl.
    """
    def __init__(self, kubeconf):
        self.kubeconf = kubeconf

    def create(self, name):
        """Create a jupyterhub deployment on the cluster."""
        hub = Hub(namespace=name)
        hub.create()

    def get(self, name=None):
        """Print a list of all jupyterHubs.
        """
        if name is None:
            print("Running Jupyterhub Deployments (by name):")
            output = helm(
                'list',
                '-q'
            )
            if output.returncode != 0:
                print("Something went wrong!")
                print(output.stderr)
            else:
                names = output.stdout.strip().split('\n')
                for name in names:
                    print(f"  - {name}")

        else:
            hub = Hub(namespace=name)
            hub.get()
        
    def delete(self, name):
        """Delete Hub from Kubernetes Cluster
        """
        hub = Hub(namespace=name)
        hub.delete()
