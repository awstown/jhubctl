from traitlets.config import Application
from traitlets import (
    default,
    observe,
    Unicode,
    List,
    Dict
)
from . import providers


class BaseSubcommand(Application):
    
    name = Unicode()
    description = Unicode()
    method = Unicode(help="Method to call on resource object.")

    resource_options = Dict({
        'cluster': 'provider'
        # 'hub':
        # 'ng':
    }, help="Mapping CMD to jhubctl attribute names.")

    def get_resource(self, resource_type):
        try:
            parent_attr = self.resource_options[resource_type]
            resource = getattr(self.parent, parent_attr)
            return resource
        except AttributeError:
            raise AttributeError(
                "Resource options must be cluster, hub, or ng.")

    def initialize(self, argv=None):
        # Handle no arguments.
        if len(argv) == 0:
            self.print_help()
            self.exit()

        self.parse_command_line(argv)
        resource_type = argv[0]
        resource_args = argv[1:]

        # Get resource
        resource = self.get_resource(resource_type)
        method = getattr(resource, self.method)
        method(resource_args)


class CreateSubcommand(BaseSubcommand):
    """"""

    name = Unicode(u'create')
    description = Unicode(u'`create` subcommand')
    method = Unicode(u'create')


class DeleteSubcommand(BaseSubcommand):
    name = Unicode(u'delete')
    description = Unicode('delete subcommand.')
    method = Unicode(u'delete')



class JhubCtl(Application):
    """Jupyterhub Deployments configuration system."""

    name = Unicode(u'jhubctl')

    classes = List([
        # Kubernetes
    ])

    subcommands = Dict({
        'create': (CreateSubcommand, 'Create resource.'),
        'delete': (DeleteSubcommand, 'Delete resource'),
        # 'create': (CreateSubcommand, 'Delete resource'),
        # 'edit': (EditSubcommand, 'Delete resource'),
        # 'config': (ConfigSubcommand, 'Delete resource'),
    })

    provider_class = Unicode(
        help="Cloud provider."
    ).tag(config=True)

    @default('provider_class')
    def _default_provider_class(self):
        provider_class = 'AwsEks'
        self.classes.append(provider_class)
        return provider_class

    @observe('provider_class')
    def _observe_provider_class(self, change):
        # Remove the old class and add new one.
        self.classes.remove(change['old'])
        self.classes.append(change['new'])
    
    def init_provider(self):
        # Get provider and ini
        Provider = getattr(providers, self.provider_class)
        self.provider = Provider

    def initialize(self, argv=None):
        self.init_provider()
        self.parse_command_line(argv)
        # # Handle no args
        # if argv is None:
        #     print("AAAHAHHHH")
        #     self.print_help()
        #     self.exit()



    def start(self):
        pass


def main():
    app = JhubCtl()
    app.initialize()
    app.start()


def test():
    app = JhubCtl()
    app.initialize()
    app.start()
    return app

if __name__ == "__main__":
    main()
