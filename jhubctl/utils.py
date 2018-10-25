import jinja2
import pathlib
import subprocess

class SubclassError(Exception):
    """Must be implemented in a subclass."""

class JhubctlError(Exception):
    """CLI exceptions"""


def get_flag_args(**options):
    """Build a list of flags."""
    flags = []
    for key, value in options.items():
        # Build short flags.
        if len(key) == 1:
            flag = f'-{key}'
        # Built long flags.
        else:
            flag = f'--{key}'
        flags = flags + [flag, value]
    return flags


def kubectl(*args, input=None, **flags):
    """Simple wrapper to kubectl."""
    # Build command line call.
    line = ['kubectl'] + list(args)
    line = line + get_flag_args(**flags)
    if input is not None:
        line = line + ['-f', '-']
    # Run subprocess
    output = subprocess.run(
        line,
        input=input,
        capture_output=True,
        text=True
    )
    return output


def helm(*args, input=None, **flags):
    """Simple wrapper to helm."""
    # Build command line call.
    line = ['helm'] + list(args)
    line = line + get_flag_args(**flags)
    if input is not None:
        line = line + ['-f', '-']
    # Run subprocess
    output = subprocess.run(
        line,
        input=input,
        capture_output=True,
        text=True
    )
    return output


def sanitize_path(path):
    if isinstance(path, str):
        path = pathlib.Path(path).resolve()
    elif isinstance(path, pathlib.Path):
        path = path.resolve()
    else:
        raise Exception()
    return path


def get_template(template_path, **parameters):
    """Use jinja2 to fill in template with given parameters.
    
    Parameters
    ----------
    template_path : str
        Name of template.

    Keyword Arguments
    -----------------
    Parameters passed into the jinja2 template

    Returns
    -------
    output_text : str
        Template as a string filled in with parameters.
    """
    path = sanitize_path(template_path)
    template_file = path.name
    template_dir = str(path.parent)

    ## Apply ARN of instance role of worker nodes and apply to cluster
    template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
    template_env = jinja2.Environment(loader=template_loader)

    template = template_env.get_template(template_file)
    output_text = template.render(**parameters)

    return output_text
