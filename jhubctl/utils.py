import os
import json
import subprocess
import botocore
from pathlib import Path, PurePath


def get_jhubctl_path():
    home = Path.home()
    jhubctl_path = PurePath.joinpath(home, ".jhubctl")
    return jhubctl_path

def create_jhubctl_dir():
    jhubctl_path = get_jhubctl_path()
    # Create directory if it doesn't exist.
    if not os.path.exists(jhubctl_path):
        os.makedirs(jhubctl_path)


def get_deployment_path(cluster_name):
    """Get the path to Jupyterhub deployment configuration."""
    jhubctl_path = get_jhubctl_path()
    deployment_path = PurePath.joinpath(jhubctl_path, f"{cluster_name}")
    return deployment_path


def create_deployment_dir(cluster_name):
    deployment_path = get_deployment_path(cluster_name)
    aws_path = PurePath.joinpath(deployment_path, "aws")
    kube_path = PurePath.joinpath(deployment_path, "kube")
    hub_path = PurePath.joinpath(deployment_path, "hub")

    # Create directory if it doesn't exist.
    if not os.path.exists(deployment_path):
        os.makedirs(deployment_path)

    # Create directory if it doesn't exist.
    if not os.path.exists(aws_path):
        os.makedirs(aws_path)

    # Create directory if it doesn't exist.
    if not os.path.exists(kube_path):
        os.makedirs(kube_path)

    # Create directory if it doesn't exist.
    if not os.path.exists(hub_path):
        os.makedirs(hub_path)


def get_params_path():
    """Get path to Jinja templates."""
    # THIS IS HACK... need a better method
    path = "params"
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, path)


def get_template_path():
    """Get path to Jinja templates."""
    # THIS IS HACK... need a better method
    path = "templates"
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, path)


def get_config_path():
    """Get path to YAML configurations."""
    # THIS IS HACK... need a better method
    path = "configs"
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, path)


def get_kube_path(endpoint):
    """"""
    base_path = PurePath.join(Path.home(), ".kube", endpoint)
    return os.path.join(base_path, kube_path)


def read_config_file(fname):
    config_path = os.path.join(get_config_path(), fname)
    with open(config_path, "r") as f: 
        data = f.read()
    return data


def read_param_file(fname):
    config_path = os.path.join(get_params_path(), fname)
    with open(config_path, "r") as f:
        data = json.load(f)
    return data


def read_deployment_file(cluster_name, fname):
    """Read a file from the deployment directory (in ~/.kube/{cluster_name})."""
    fpath = os.path.join(get_deployment_path(cluster_name), fname):
    with open(fname, "r") as f:
        data = f.read()
    return data
