# Command Structure

    Usage:
    jhubctl [flags] [Options] <command> Resource

    Commands:
        create
            cluster         Create k8s cluster on the default cloud platform flag e.g. `--cloud-provider=gcloud`
            juypterhub(hub) Create JupyterHub within a k8s cluster leverages the JupyterHub Helm chart
            nodegroup(ng)   Create additional node group for a JupyterHub
        delete
            cluster
            jupyterhub(hub)
            nodegroup(ng)
        get
            cluster
            jupyterhub(hub)
            nodegroup(ng)
        edit?
            cluster
            jupyterhub(hub)
            nodegroup(ng)

    Config Commands:
        config
            export-kubeconfig Exports config to ~/.kube/kubeconfig-<ClusterName>. Useful if working on a machine 
                                that has aws configured but has not connected to k8s cluster before
        
    Resources:
            cluster
            jupyterhub(hub)
            nodegroup(ng)
