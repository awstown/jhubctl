from traitlets.config import Application
from traitlets import (
    default,
    observe,
    Unicode,
    List,
    Dict
)
from . import providers


class Deployment(Application):
    """
    """
    name = Unicode()
    description = Unicode()
    action = Unicode(help="Action to execute on resource.")
    classes = List([
        providers.AwsEks
    ])

    def init_cluster(self, name):
        """Initialize the cluster."""
        self.cluster = providers.AwsEks(name=name)

    def init_hub(self, name):
        pass
        
    def init_ng(self, name):
        pass

    def init_resource(self, resource_type, name):
        """Initialize the Resource."""
        try:
            method = getattr(self, f"init_{resource_type}")
            method(name)
        except AttributeError:
            raise AttributeError(
                "Resource options must be cluster, hub, or ng.")

    def get_resource(self, resource_type, name):
        try:
            resource = getattr(self, resource_type)
            return resource
        except AttributeError:
            raise AttributeError(
                "Resource options must be cluster, hub, or ng.")

    def initialize(self, argv=None):
        """
        """
        self.parse_command_line(argv)
        resource_type = self.argv[0]
        resource_name = self.argv[1]
        resource_args = self.argv[2:]

        self.init_resource(resource_type, resource_name)
        resource = self.get_resource(resource_type, resource_name)
        action = getattr(resource, self.action)
        action(*resource_args)


class CreateSubcommand(Deployment):
    name = Unicode(u'create')
    description = Unicode(u'`create` subcommand')
    action = Unicode(u'create')


class DeleteSubcommand(Deployment):
    name = Unicode(u'delete')
    description = Unicode('delete subcommand.')
    action = Unicode(u'delete')


class JhubCtl(Application):
    """Jupyterhub Deployments configuration system."""

    name = Unicode(u'jhubctl')
    classes = List([
        providers.AwsEks
    ])

    # subcommands = Dict({
    #     'create': (CreateSubcommand, 'Create resource.'),
    #     'delete': (DeleteSubcommand, 'Delete resource'),
    #     # 'get': (GetSubcommand, 'Get resource'),
    #     # 'edit': (EditSubcommand, 'Edit resource'),
    #     # 'config': (ConfigSubcommand, 'Config system'),
    # })

    def initialize(self, argv=None):
        self.parse_command_line(argv)
        print('initialize jhubctl')

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
