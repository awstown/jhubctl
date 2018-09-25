import os
import json
import subprocess
import botocore

class ResourceDoesNotExistError(Exception):
    """Resource does not exist."""


def does_resource_exist(resource):
    """Use boto3 to check if a resource exists."""
    try:
        resource.load()
        return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError':
            return False
        else:
            raise e
    
def raise_if_does_not_exist(resource):
    if does_resource_exist(resource) is False:
        raise ResourceDoesNotExistError


def get_stack_value(stack, key):
    for output in stack.outputs:
        if output['OutputKey'] == key:
            return output['OutputValue']


def kubectl(*args, **kwargs):
    return subprocess.check_call(
        ('kubectl',) + args,
        **kwargs
    )


def helm(*args, **kwargs):
    return subprocess.check_call(
        ('helm',) + args,
        **kwargs
    )


def get_params_dir():
    """Get path to Jinja templates."""
    # THIS IS HACK... need a better method
    path = "params"
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, path)


def get_template_dir():
    """Get path to Jinja templates."""
    # THIS IS HACK... need a better method
    path = "templates"
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, path)


def get_config_dir():
    """Get path to YAML configurations."""
    # THIS IS HACK... need a better method
    path = "configs"
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, path)


def read_config_file(fname):
    config_path = os.path.join(get_config_dir(), fname)
    with open(config_path, "r") as f: 
        data = f.read()
    return data


def read_param_file(fname):
    config_path = os.path.join(get_params_dir(), fname)
    with open(config_path, "r") as f:
        data = json.load(f)
    return data
