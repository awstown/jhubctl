
from ..utils import kubectl, helm
from .single import Hub

class HubList(object):
    """A class to manage many Jupyterhub deployments.

    Parameter
    ---------
    kubeconf : KubeConf object
        A KubeConf object for managing the kubeconfig
        on the current system.
    """
    def __init__(self, kubeconf):
        self.kubeconf = kubeconf

    def create(self, name):
        """Create a jupyterhub deployment on the cluster."""
        hub = Hub(namespace=name)
        hub.create()

    def get_hubs(self):
        """Get a list of hubs names.
        
        Returns
        -------
        hubs : list
            List of hub names
        """
        # Use helm to get a list of hubs.
        output = helm(
            'list',
            '-q'
        )
        # Check if an error occurred.
        if output.returncode != 0:
            print("Something went wrong!")
            print(output.stderr)
        else:
            hubs = output.stdout.split()
            return hubs

    def get(self, name=None):
        """Print a list of all jupyterHubs."""
        # Print a list of hubs.
        if name is None:
            hubs = self.get_hubs()
            print("Running Jupyterhub Deployments (by name):")
            for hub_name in hubs:
                hub = Hub(namespace=hub_name)
                data = hub.get_description()
                url = data['LoadBalancer Ingress']
                print(f'  - Name: {hub_name}')
                print(f'    Url: {url}')
        else:
            hub = Hub(namespace=name)
            hub.get()
        
    def delete(self, name):
        """Delete Hub from Kubernetes Cluster
        """
        hub = Hub(namespace=name)
        hub.delete()

    def describe(self, name):
        """Describe a cluster."""
        hub = Hub(namespace=name)
        hub.describe()
