import jinja2
import pathlib


class SubclassError(Exception):
    """Must be implemented in a subclass."""


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
        output = subprocess.run(line)  # , capture_output=True)
        if output.stdout is not None:
            return output.stdout.decode('utf-8')

    return command


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
