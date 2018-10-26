# jhubctl

**A familiar CLI for managing JupyterHub deployments on Kubernetes clusters.**

*jhubctl* makes it easy to deploy JupyterHub instances on Kubernetes clusters. The command line application follows a similar interface to `kubectl` and both tools work seemlessly together. *jhubctl* is not meant to replace `kubectl`; rather, it provides a simpler interface to launching, editing, and deleting JupyterHub deployments on Kubernetes Clusters. Specific Kubernetes configuration should be done using `kubectl` and `helm`.

## Getting Started

See [Installing](#installing) for directions on installation.

### Example Usage

Create a cluster.
```bash
$ jhubctl create cluster mycluster
```

Deploy a jupyterhub on the current cluster.
```bash
$ jhubctl create hub hub1
```

List all running Jupyterhub deployments.
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
prod
test
dev
```

## Installing

Currently, this package is only available from source. Clone this repo and install using
pip.
```
git clone https://github.com/townsenddw/jhubctl
cd jhubctl
pip install -e .
```
