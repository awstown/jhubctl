# jhubctl

**A familiar CLI for managing JupyterHub deployments on Kubernetes clusters.**

*jhubctl* makes it easy to deploy JupyterHub instances on Kubernetes clusters. The command line application follows a similar interface to `kubectl` and both tools work seemlessly together. *jhubctl* is not meant to replace `kubectl`; rather, it provides a simpler interface to launching, editing, and deleting JupyterHub deployments on Kubernetes Clusters. Specific Kubernetes configuration should be done using `kubectl` and `helm`.

*jhubctl* is designed to work with any cloud service provider. Currently, it only supports AWS's Elastic Kubernetes Service (EKS), but we are hoping to extend it to other providers in the near future.

## Getting Started

### Prerequisites

1. Install *jhubctl* using pip:

    ```
    pip install jhubctl
    ```

1. Give your machine access/privileges to AWS using AWS's CLI credentials. See instructions [here]().

1. Launch a cluster and jupyterhub.

### Example Usage

Create clusters.
```bash
$ jhubctl create cluster mycluster

100%|███████████████████████████████████| 6/6 [00:07<00:00,  1.39s/it]
```

Deploy jupyterhubs on a cluster.
```bash
$ jhubctl create hub hub1
```

Deploy a custom configured jupyterhub using a `config.yaml` file.
```bash
$ jhubctl create hub hub2 --Hub.config_file="config.yaml"
```

List all running Jupyterhub deployments in a cluster.
```
$ jhubctl get hub

Running Jupyterhub Deployments (by name):
  - Name: hub1
    Url: aff02ecd6d8b111e8b8be0a21c647ea9-730724679.us-west-2.elb.amazonaws.com
  - Name: hub2
    Url: a03325febd88711e8b8be0a21c647ea9-1146691895.us-west-2.elb.amazonaws.com
```

Describe a jupyterhub pod.
```
$ jhubctl describe hub hub1

Name:                     proxy-public
Namespace:                hub1
Labels:                   app=jupyterhub
                          chart=jupyterhub-0.7.0
                          component=proxy-public
                          heritage=Tiller
                          release=test
Annotations:              <none>
Selector:                 component=proxy,release=test
Type:                     LoadBalancer
IP:                       172.20.135.155
LoadBalancer Ingress:     aff02ecd6d8b111e8b8be0a21c647ea9-730724679.us-west-2.elb.amazonaws.com
Port:                     http  80/TCP
TargetPort:               8000/TCP
NodePort:                 http  30449/TCP
Endpoints:                10.42.2.173:8000
Session Affinity:         None
External Traffic Policy:  Cluster
Events:
  Type    Reason                Age   From                Message
  ----    ------                ----  ----                -------
  Normal  EnsuringLoadBalancer  6m    service-controller  Ensuring load balancer
  Normal  EnsuredLoadBalancer   6m    service-controller  Ensured load balancer
```


List current running clusters.
```
$ jhubctl get cluster

Running Clusters:
  - cluster1
  - cluster2
  - cluster3
```

## Contributing

Download and install this repo from source, and move into the base directory.
```
git clone https://github.com/townsenddw/jhubctl
cd jhubctl
```
If you use [pipenv](https://pipenv.readthedocs.io/en/latest/), you can install a developement version:
```
pipenv install --dev
``` 

Otherwise you can install a development version using pip
```
pip install -e .
```
