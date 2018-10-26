import secrets
import pathlib

from jhubctl.utils import helm, kubectl, YAML
from traitlets.config import Configurable
from traitlets import default, Unicode



class Hub(Configurable):
    """Single instance of a JupyterHub deployment.
    """
    # Helm repository to pull charts.
    helm_repo = Unicode(
        u'https://jupyterhub.github.io/helm-chart/',
        help="Jupyterhub Helm Chart repo."
    ).tag(config=True)

    # Helm chart release name. If not given, use the 
    # namespace as the release name.
    release = Unicode(
        help="Release name"
    ).tag(config=True)

    @default('release')
    def _default_release(self):
        return self.namespace

    # Helm chart version to pull.
    version = Unicode(
        u'0.7.0',
        help='Helm Chart for Jupyterhub release.'
    ).tag(config=True)

    # Name to give to namespace.
    namespace = Unicode(
        help="Name of the Kubernetes namespace."
    ).tag(config=True)

    config_file = Unicode(
        help="Name of config.yaml for this Jupyterhub deployment. Updates the Helm chart."
    ).tag(config=True)

    def __init__(self, namespace, release=None, **traits):
        self.namespace = namespace
        if release is None:
            self.release = namespace
        super().__init__(**traits)

    def _get_security_config(self):
        """Create security YAML data."""
        # Get Token.
        token = secrets.token_hex(nbytes=32)
        # Turn token into yaml
        data = {
            'proxy': {'secretToken': token}
        }
        return data

    def _get_config_from_cli(self):
        """Get config.yaml items from CLI"""
        # NOT IMPLEMENTED YET.
        data = {}
        return data

    def _get_config_from_file(self):
        """Get config.yaml items from named file."""
        data = {}
        # If a config file is given, use it.
        if self.config_file != '':
            text = pathlib.Path(self.config_file).read_text()
            yaml = YAML()
            data = yaml.load(text)     
        return data
        
    def get_config(self):
        """Build a config dictionary.
        """
        data = {}
        data.update(self._get_config_from_file())
        data.update(self._get_config_from_cli())
        data.update(self._get_security_config())
        return data

    def get_config_yaml(self):
        """Get config.yaml as a string.
        """
        data = self.get_config()
        yaml = YAML()
        return yaml.dump(data)

    def get(self):
        """Get specific information about this hub."""
        output = helm("get", self.release)
        if output.returncode != 0:
            print("Something went wrong!")
            print(output.stderr)
        else:
            print(output.stdout)

    def create(self):
        """Create a single instance of notebook."""
        print("Deploying a JupyterHub.")
        print("his may take a few minutes...")
        # Point to chart repo.
        out = helm(
            "repo",
            "add",
            "jupyterhub",
            self.helm_repo
        )
        out = helm("repo", "update")

        # Get token to secure Jupyterhub
        config_yaml = self.get_config_yaml()

        # Get Jupyterhub.
        out = helm(
            "upgrade",
            "--install",
            self.release,
            "jupyterhub/jupyterhub",
            namespace=self.namespace,
            version=self.version,
            input=config_yaml
        )
        if out.returncode != 0:
            print(out.stderr)
        else:
            print(out.stdout)

    def delete(self):
        """Delete a Jupyterhub."""
        # Delete the Helm Release
        print(f"Deleting {self.release}, this make take a few minutes...\n")
        out = helm(
            "delete",
            self.release,
            "--purge"
        )
        if out.returncode != 0:
            print(out.stderr)
        else:
            print(out.stdout)

        # Delete the Kubernetes namespace
        out = kubectl(
            "delete",
            "namespace",
            self.namespace
        )
        if out.returncode != 0:
            print(out.stderr)
        else:
            print(out.stdout)

    def _get_description_message(self):
        """Get a description message."""
        # Describe cluster.
        out = kubectl(
            "describe",
            "services",
            "proxy-public",
            namespace=self.namespace
        )
        return out.stdout

    def _parse_description(self, description_text):
        """Turn description to dictionary."""
        text = description_text
        text = text.strip()
        lines = text.split('\n')

        data = {}
        for line in lines:
            if ":" in line:
                idx = line.index(":")
                key = line[:idx]
                value = line[idx+1:].lstrip().rstrip()
                data[key] = value
            else:
                if isinstance(value, list) is False:
                    value = [value]
                value.append(line.lstrip().rstrip())
                data[key] = value
        return data

    def get_description(self):
        """Get description (as dictionary)"""
        message = self._get_description_message()
        data = self._parse_description(message)
        return data

    def describe(self):
        """Describe jupyterhub pod."""
        print(self._get_description_message())
