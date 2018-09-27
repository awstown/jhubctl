import click
from functools import wraps

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
    

class Provider(object):
    """Base class for a Provider.
    """
    def __init__(self, name):
        self.cluster_name = f"{name}-cluster"
        self.bar = None

    def deploy_cluster(self, progressbar=True):
        """Deploy a cluster on this provider."""
        raise Exception("Must be implemented in a subclass.")

    def teardown_cluster(self):
        """Teardown cluster."""
        raise Exception("Must be implemented in a subclass.")

    def reset_progressbar(self, length, label="Starting cluster."):
        self.bar = click.progressbar(length=length, label=label)
        self.bar.update()
