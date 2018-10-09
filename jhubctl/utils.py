import os
import json
import subprocess
import botocore
import jinja2

from pathlib import Path, PurePath

def get_params_path(provider):
    """Get path to provider params templates."""
    # THIS IS HACK... need a better method
    base_path = Path(__file__).resolve().parent
    return base_path.joinpath("providers", provider, "params")


def get_template_path(provider):
    """Get path to provider templates."""
    # THIS IS HACK... need a better method
    base_path = Path(__file__).resolve().parent
    return base_path.joinpath("providers", provider, "templates")


def get_config_path(provider):
    """Get path to provider config templates."""
    # THIS IS HACK... need a better method
    base_path = Path(__file__).resolve()
    return base_path.joinpath("providers", provider, "configs")


def read_config_file(provider, fname):
    config_path = os.path.join(get_config_path(provider), fname)
    with open(config_path, "r") as f:
        data = f.read()
    return data


def read_param_file(provider, fname):
    config_path = os.path.join(get_params_path(provider), fname)
    with open(config_path, "r") as f:
        data = json.load(f)
    return data


def get_kube_path(endpoint):
    """"""
    return Path.home().joinpath('.kube')


def external_cli(name):
    """Build a wrapper for external subprocess command."""

    def command(*args, config_yaml=None, **options):
        f"""Runs a {name} command and returns the stdout as a string
        """
        line = [name] + list(args)
        for key, value in options.items():
            if len(key) == 1:
                line += [f"-{key}", value]
            else:
                line += [f"--{key}", value]
        # Add yaml string as input to command
        if config_yaml is not None:
            line = ["echo", config_yaml, "|"] + line + ["-f", "-"]
        # Return output if anything is returned from subprocess.
        output = subprocess.run(line)#, capture_output=True)
        if output.stdout is not None:
            return output.stdout.decode('utf-8')

    return command


def fill_template(provider_name, template_name, **parameters):
    """Use jinjga2 to fill in template with given parameters.
    
    Parameters
    ----------
    provider_name : str
        Name of cloud provider (must be found in providers module).

    template_name : str
        Name of template.

    Keyword Arguments
    -----------------
    Parameters passed into the jinja2 template

    Returns
    -------
    output_text : str
        Template as a string filled in with parameters.
    """
    template_path = get_template_path(provider_name)

    ## Apply ARN of instance role of worker nodes and apply to cluster
    template_loader = jinja2.FileSystemLoader(searchpath=str(template_path))
    template_env = jinja2.Environment(loader=template_loader)

    template = template_env.get_template(template_name)
    output_text = template.render(**parameters)

    return output_text

