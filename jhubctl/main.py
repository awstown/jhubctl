import sys
import re
from copy import deepcopy 

from ipython_genutils import py3compat
from traitlets.config import Application, Configurable, catch_config_error
from traitlets import (
    default,
    observe,
    Unicode,
    List,
    Dict
)

from kubeconf import KubeConf

from .utils import JhubctlError
from .clusters import providers, ClusterList
from .hubs import HubList



def exception_handler(exception_type, exception, traceback):
    """Handle jhubctl exceptions"""
    print(f'{exception_type.__name__}: {exception}')

#sys.excepthook = exception_handler


class JhubCtl(Application):
    """Jupyterhub Deployments configuration system."""

    name = Unicode(u'jhubctl')
    description= Unicode(
        u'Command line interface for deploying Jupyterhub on Kubernetes Clusters.'
    )

    classes = List([
        KubeConf,
        HubList
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

        # # Parse configuration items on command line.
        self.parse_command_line()

        # ADD SERVER CLASS TO OUR LIST OF CLASSES THAT ARE CONFIGURABLE.
        # THIS SI A HACK RIGHT NOW, NEED TO FIGURE THIS OUT.
        # Append Provider Class to the list of configurable items.
        ProviderClass = getattr(providers, self.provider_type)
        self.classes.append(ProviderClass)

        # If a help command is found, print help and exit.
        if help_arg:
            self.print_help(arg == '--help-all')
            self.exit(0)

        # If not config, parse commands.
        ## Run sanity checks.

        # Check that the minimum number of arguments have been called.
        if len(self.argv) < 2:
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
        try:
            self.resource_name = self.argv[2]
        except IndexError:
            if self.resource_action != "get":
                raise JhubctlError(
                    "Not enough arguments. \n\n"
                    "Expected: jhubctl <action> <resource> <name>")
            else:
                self.resource_name = None
        
        # Get resource.
        self.kubeconf = KubeConf()
        self.cluster_list = ClusterList(kubeconf=self.kubeconf)
        self.hub_list = HubList(kubeconf=self.kubeconf)

    def start(self):
        """Execution happening on jhubctl."""
        # Get specified resource.
        resource_list = getattr(self, f'{self.resource_type}_list')
        resource_action = getattr(resource_list, self.resource_action)
        resource_action(self.resource_name)

def main():
    app = JhubCtl()
    app.initialize()
    app.start()



if __name__ == "__main__":
    main()

