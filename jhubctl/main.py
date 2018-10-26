import sys
import os
import re
from copy import deepcopy 

from ipython_genutils.text import indent
from ipython_genutils import py3compat

from traitlets.config.loader import (
    KVArgParseConfigLoader, PyFileConfigLoader, Config, ArgumentError, ConfigFileNotFound, JSONFileConfigLoader
)
from traitlets.config import (
    Application, 
    Configurable, 
    catch_config_error
)

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
from .hubs import HubList, Hub


def exception_handler(exception_type, exception, traceback):
    """Handle jhubctl exceptions"""
    print(f'{exception_type.__name__}: {exception}')

#sys.excepthook = exception_handler


class JhubctlApp(Application):
    """A traitlets application that deploys jupyterhub on Kubernetes clusters.

    Example call:
        $ jhubctl create hub "my_hub" 

    JhubctlApp manages both clusters and jupyterhub deployments through
    a single interface. 

    Subcommands: 
    
        $ jhubctl get <resource> <name> : List a named resource found in kubeconfig.
        $ jhubctl get <resource> : List all resources found in kubeconfig.
        $ jhubctl create <resource> <name> : Create a resource with the given name.
        $ jhubctl delete <resource> <name> : Delete a resource with the given name.
    

    JhubctlApp is configurable through traitlets config system. Configurable traits
    can be set at the command line or in a config file. To generate a config 
    template, use the following flag:

        $ jhubctl --generate-config
    """
    # Name of the commandline application
    name = Unicode(u'jhubctl')

    # Documentation used at the top of the CLI help.
    description = Unicode(
        u"A familiar CLI for managing JupyterHub "
        u"deployments on Kubernetes clusters."
    )

    # Printed examples for the help.
    examples = Unicode(
        u" > jhubctl create hub myhub"
    )

    # Classes to expose to the config system
    classes = List([
        KubeConf,
        Hub
    ])

    # Provider to configure.
    provider_type = Unicode(
        u'AwsEKS',
        help="Provider type."
    ).tag(config=True)
    
    # Subcommands allowed by application.
    subcommands = Dict({
        'create': ((), 'Create a resource.'),
        'delete': ((), 'Delete a resource.'),
        'get': ((), 'List a resource or resources'),
        'describe': ((), 'Describe a resource')
    })

    # Resource that can be deployed and managed.
    resources = List([
        'cluster',
        'hub',
    ])

    # Name of the configuration file to read.
    config_file = Unicode(
        help="Name of configuration file."
    ).tag(config=True)

    @default('config_file')
    def _default_config_file(self):
        return u"jhubctl_config.py"

    def print_subcommands(self):
        """Print the subcommand part of the help."""
        lines = ["Call"]
        lines.append('-'*len(lines[-1]))
        lines.append('')
        lines.append("> jhubctl <subcommand> <resource-type> <resource-name>")
        lines.append('')
        lines.append("Subcommands")
        lines.append('-'*len(lines[-1]))
        lines.append('')

        for name, subcommand in self.subcommands.items():
            lines.append(name)
            lines.append(indent(subcommand[1]))

        lines.append('')
        print(os.linesep.join(lines))

    @catch_config_error
    def parse_command_line(self, argv=None):
        """Parse the jhubctl command line arguments.
        
        This overwrites traitlets' default `parse_command_line` method
        and tailors it to jhubctl's needs.
        """
        argv = sys.argv[1:] if argv is None else argv
        self.argv = [py3compat.cast_unicode(arg) for arg in argv]

        # Append Provider Class to the list of configurable items.
        ProviderClass = getattr(providers, self.provider_type)
        self.classes.append(ProviderClass)

        if any(x in self.argv for x in ('-h', '--help-all', '--help')):
            self.print_help('--help-all' in self.argv)
            self.exit(0)

        if '--version' in self.argv or '-V' in self.argv:
            self.print_version()
            self.exit(0)

        # Generate a configuration file if flag is given.
        if '--generate-config' in self.argv:
            conf = self.generate_config_file()
            with open(self.config_file, 'w') as f:
                f.write(conf)
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
        if self.resource_action not in self.subcommands:
            raise JhubctlError(
                f"Subcommand is not recognized; must be one of these: {self.subcommands}")

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

        # flatten flags&aliases, so cl-args get appropriate priority:
        flags, aliases = self.flatten_flags()
        loader = KVArgParseConfigLoader(argv=argv, aliases=aliases,
                                        flags=flags, log=self.log)
        config = loader.load_config()
        self.update_config(config)
        # store unparsed args in extra_args
        self.extra_args = loader.extra_args

    def initialize(self, argv=None):
        """Handle specific configurations."""
        # Parse configuration items on command line.
        self.parse_command_line(argv)
        if self.config_file:
            self.load_config_file(self.config_file)

        # Initialize objects to interact with.
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
    app = JhubctlApp()
    app.initialize()
    app.start()


if __name__ == "__main__":
    main()

