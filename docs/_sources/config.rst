Configuration System
====================

``jhubctl`` inherits the config system inside of *traitlets*. You can generate a configuration 
template using the ``--generate-config`` flag.

.. code-block:: bash

    > jhubctl --generate-config

An example template is shown here:

.. code-block:: python

    # Configuration file for jhubctl.

    #------------------------------------------------------------------------------
    # Application(SingletonConfigurable) configuration
    #------------------------------------------------------------------------------

    ## This is an application.

    ## The date format used by logging formatters for %(asctime)s
    #c.Application.log_datefmt = '%Y-%m-%d %H:%M:%S'

    ## The Logging format template
    #c.Application.log_format = '[%(name)s]%(highlevel)s %(message)s'

    ## Set the log level by value or name.
    #c.Application.log_level = 30

    #------------------------------------------------------------------------------
    # JhubctlApp(Application) configuration
    #------------------------------------------------------------------------------

    ## A familiar CLI for managing JupyterHub deployments on Kubernetes clusters.

    ## Provider type.
    #c.JhubctlApp.provider_type = 'AwsEKS'

    #------------------------------------------------------------------------------
    # KubeConf(Configurable) configuration
    #------------------------------------------------------------------------------

    ## Base object that interacts with kubeconfig file.

    ## Current kube context.
    #c.KubeConf.context = ''

    ## Path to kubeconfig.
    #c.KubeConf.path = traitlets.Undefined

    #------------------------------------------------------------------------------
    # Hub(Configurable) configuration
    #------------------------------------------------------------------------------

    ## Single instance of a JupyterHub deployment.

    ## Jupyterhub Helm Chart repo.
    #c.Hub.helm_repo = 'https://jupyterhub.github.io/helm-chart/'

    ## Release name
    #c.Hub.release = ''

    ## Helm Chart for Jupyterhub release.
    #c.Hub.version = '0.7.0'

    #------------------------------------------------------------------------------
    # Provider(Configurable) configuration
    #------------------------------------------------------------------------------

    ## Base class for Kubernetes Cluster providers.
    #  
    #  To create a new provider, inherit this class and  replace the folowing traits
    #  and methods with the  logic that is appropriate for the provider.
    #  
    #  We recommend creating a new folder for that provider where all templates can
    #  be grouped.

    ## User SSH key name
    #c.Provider.ssh_key_name = ''

    ## Path to template
    #c.Provider.template_dir = ''

    #------------------------------------------------------------------------------
    # AwsEKS(Provider) configuration
    #------------------------------------------------------------------------------

    ## AWS EKS configured for launching JupyterHub deployments.

    ## Name of the cluster
    #c.AwsEKS.cluster_name = ''

    ## Name of the node group setup to deploy jupyterhub instances.
    #c.AwsEKS.node_group_name = ''

    ## AWS Role.
    #c.AwsEKS.role_name = ''

    ## Name of the spot nodes stack
    #c.AwsEKS.spot_nodes_name = ''

    ## Name of the utilities stack
    #c.AwsEKS.utilities_name = ''

    ## Name of the virtual private cloud used by this deployment.
    #c.AwsEKS.vpc_name = ''
