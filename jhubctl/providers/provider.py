import click
from functools import wraps

from traitlets import HasTraits

def update_progress(method):
    """Update a progress bar if it exists"""
    @wraps(method)
    def increment(self, *args, **kwargs):
        """Increment progress bar if it exists."""
        output = method(self, *args, **kwargs)
        try:
            pos = self.bar.pos
            self.bar.update(pos+1)
        except AttributeError:
            pass
        return output
    return increment
    

class Provider(HasTraits):
    """Base class for a Provider.
    """


    def __init__(self, name):
        self.cluster_name = f"{name}-cluster"
        self.bar = None

    def check_if_deployed(self):
        """Returns True if the cluster is fully deployed, else 
        returns False.
        """

    def deploy_cluster(self, progressbar=True):
        """Deploy a cluster on this provider."""
        raise Exception("Must be implemented in a subclass.")

    def teardown_cluster(self):
        """Teardown cluster."""
        raise Exception("Must be implemented in a subclass.")

    def reset_progressbar(self, length, label="Starting cluster:"):
        self.bar = click.progressbar(length=length, label=label)
        
    def get_auth_yaml(self):
        raise Exception("Must be implemented in a subclass.")

    def get_storage_yaml(self):
        raise Exception("Must be implemented in a subclass.")

    def get_kubeconfig(self):
        raise Exception("Must be implemented in a subclass.")