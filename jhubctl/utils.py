import os
import subprocess

def get_stack_value(stack, key):
    for output in stack.outputs:
        if output['OutputKey'] == key:
            return output['OutputValue']



def kubectl(*args, **kwargs):
    return subprocess.check_call(
        ('kubectl',) + args
        **kwargs
    )


def helm(*args, **kwargs):
    return subprocess.check_call(
        ('helm',) + args,
        **kwargs
    )


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

def get_config_file(fname):
    config_path = os.path.join(get_config_dir(), fname)
    with open(config_path, "r") as f: 
        data = f.read()
    return data