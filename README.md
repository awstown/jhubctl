# jhubctl

**A familiar CLI for managing JupyterHub deployments on Kubernetes clusters.**

WARNING: Still under active development! Does not work yet.

## Example Usage

```bash
$ jhubctl create hub DATA_301
```

```
$ jhubctl list hubs
DATA_301
STAT_331
```

```
$ jhubctl get cluster
3 clusters found:
prod [default]
test
dev

# lists only hubs in default cluster (prod)
$ jhubctl get jhub 
data301
stat350
wissellab

# list hubs in dev cluster
$ jhubctl get jhub --cluster dev 
s3jhub
cool-new-hub-feature
```

## Using kubectl with jhubctl

If you want to 
```
kubectl config --kubeconfig=jhubctl-config get-context <deployment-name>
```


## Install

Clone this repo, change into the main directory, and run:
```
pip install -e .
```


