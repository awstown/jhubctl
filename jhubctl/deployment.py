

class Deployment(object):
    """Deployment class.
    """
    def __init__(self, provider, kubernetes, hub={}):
        self.provider = provider
        self.kubernetes = kubernetes
        self.hubs = hubs
    
    def get_hubs(self):


    def deploy(self):
        """"""
        self.provider.deploy_cluster()
        self.provider.
        self.kubernetes.setup()