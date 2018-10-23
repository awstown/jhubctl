import sys

from traitlets.config import Application, Configurable
from traitlets import (
    default,
    observe,
    Unicode,
    List,
    Dict
)

from kubeconf import KubeConf

from .utils import JhubctlError
from . import providers
from .jhub import Hub


def exception_handler(exception_type, exception, traceback):
    """Handle jhubctl exceptions"""
    print(f'{exception_type.__name__}: {exception}')

sys.excepthook = exception_handler


class JhubCtl(Application):
    """Jupyterhub Deployments configuration system."""

    name = Unicode(u'jhubctl')
    description= Unicode(
        u'Command line interface for deploying Jupyterhub on Kubernetes Clusters.'
    )

    classes = List([
        #providers.AwsEks,
        KubeConf,
        Hub
    ])

    provider_type = Unicode(
        u'AwsEKS',
        help="Provider type."
    ).tag(config=True)
    
    actions = List([
        'create',
        'delete',
        'get',
    ])

    resources = List([
        'cluster',
        'hub',
        'ng'
    ])

    def initialize(self):
        """Handle specific configurations."""
        ###### This is a bit of a hack to customize help documentation
        # Strip out any help args
        for arg in sys.argv:
            help_arg = arg in ('--help-all', '-h', '--help')
            if help_arg:
                sys.argv.remove(arg)
                break

        # Parse configuration items on command line.
        self.parse_command_line()

        # Set the provider
        self.ProviderClass = getattr(providers, self.provider_type)
        self.classes.append(self.ProviderClass)

        # If a help command is found, print help and exit.
        if help_arg:
            self.print_help(arg == '--help-all')
            self.exit(0)

        # If not config, parse commands.
        ## Run sanity checks.

        # Check that the minimum number of arguments have been called.
        if len(self.argv) < 3:
            raise JhubctlError(
                "Not enough arguments. \n\n"
                "Expected: jhubctl <action> <resource> <name>")

        # Check action
        self.resource_action = self.argv[0]
        if self.resource_action not in self.actions:
            raise JhubctlError(
                f"Subcommand is not recognized; must be one of these: {self.actions}")

        # Check resource
        self.resource_type = self.argv[1]
        if self.resource_type not in self.resources:
            raise JhubctlError(
                f"First argument after a subcommand must one of these"
                f"resources: {self.resources}"
            )

        # Get name of resource.
        self.resource_name = self.argv[2]

        # Get resource.
        self.cluster = self.ProviderClass
        self.hub = Hub


    def start(self):
        """Execution happening on jhubctl."""
        # Get specified resource.
        Resource = getattr(self, self.resource_type)
        self.resource = Resource(name=self.resource_name)
        self.action = getattr(self.resource, self.resource_action)

        # Execute action
        self.action()

def main():
    app = JhubCtl()
    app.initialize()
    app.start()



if __name__ == "__main__":
    main()

