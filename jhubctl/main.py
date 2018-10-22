from traitlets.config import Application, Configurable
from traitlets import (
    default,
    observe,
    Unicode,
    List,
    Dict
)
from . import providers
from .k8s import Kubernetes
from .jhub import Hub

class JhubCtl(Application):
    """Jupyterhub Deployments configuration system."""

    name = Unicode(u'jhubctl')
    classes = List([
        providers.AwsEks,
        Kubernetes,
        Hub
    ])

    cluster_provider = Configurable(
        default=providers.AwsEks,
        help="Cloud provider to use."
    )
    
    actions = List([
        'create',
        'delete',
        'get',
        'config'
    ])

    resources = List([
        'cluster',
        'hub',
        'ng'
    ])

    def initialize(self):
        # Parse command line
        self.parse_command_line()

        # Check action
        action = self.argv[0]
        if action not in self.actions:
            raise Exception(f"Subcommand is not recognized; must be one of these: {self.actions}")

        # Check resource
        resource = self.argv[1]
        if resource not in self.resources:
            raise Exception(
                f"First argument after a subcommand must one of these"
                f"resources: {self.resources}"
            )

        resource_name = self.argv[2]


    def start(self):
        pass


def main():
    app = JhubCtl()
    app.initialize()
    app.start()



if __name__ == "__main__":
    main()

