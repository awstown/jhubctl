# jhubctl

**A familiar CLI for managing JupyterHub deployments on Kubernetes clusters.**

**jhubctl** makes it easy to deploy JupyterHub on Kubernetes clusters. The command line application follows a kubectl 
model. 

## Example Usage

```bash
$ jhubctl create cluster mycluster
```

```bash
$ jhubctl create hub DATA_301
```

```
$ jhubctl get hubs
DATA_301
STAT_331
```

```
$ jhubctl get cluster
Running Clusters:
prod
test
dev
```

## Install

Install using pip:
```
pip install jhubctl
```

