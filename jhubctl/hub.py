

def deploy_hub(cluster_name):
    """
    """
    # Get and random hex string.
    hex_str = subprocess.getoutput("openssl rand -hex 32")

    #
    hub_yaml = f'proxy:\n  secretToken: "{hex_str}"'
    hub_yaml_file = f"{cluster_name}-jupyterhub"
    hub_yaml_path = get_kube_dir(kube_yaml_file)
    with open(, "w") as f:
        f.write(hub_yaml)
