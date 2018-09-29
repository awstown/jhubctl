import os
import json
import subprocess
import botocore
import jinja2

from pathlib import Path, PurePath

def get_params_path(provider):
    """Get path to provider params templates."""
    # THIS IS HACK... need a better method
    base_path = os.path.dirname(os.path.abspath(__file__))
    path = (base_path, "providers", provider, "params")
    return os.path.join(*path)


def get_template_path(provider):
    """Get path to provider templates."""
    # THIS IS HACK... need a better method
    base_path = os.path.dirname(os.path.abspath(__file__))
    path = (base_path, "providers", provider, "template")
    return os.path.join(*path)


def get_config_path(provider):
    """Get path to provider config templates."""
    # THIS IS HACK... need a better method
    base_path = os.path.dirname(os.path.abspath(__file__))
    path = (base_path, "providers", provider, "configs")
    return os.path.join(*path)


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
    return PurePath.join(Path.home(), ".kube", endpoint)


def fill_template(template_name, **parameters):
    """Use jinjga2 to fill in template with given parameters.
    
    Parameters
    ----------
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
    template_dir = get_template_path()

    ## Apply ARN of instance role of worker nodes and apply to cluster
    template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
    template_env = jinja2.Environment(loader=template_loader)

    template = template_env.get_template(template_name)
    output_text = template.render(**parameters)

    return output_text

