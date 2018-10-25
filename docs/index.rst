.. jhubctl documentation master file, created by
   sphinx-quickstart on Tue Oct 23 17:34:53 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

jhubctl
=======

**A familiar CLI for managing JupyterHub deployments on Kubernetes clusters.**


Basic Usage
===========

``jhubctl`` follows a similar pattern as Kubernetes' ``kubectl`` interface. 

.. code-block:: bash

    > jhubctl create cluster mycluster
    100%|███████████████████████████████████| 6/6 [00:07<00:00,  1.39s/it]

List clusters.

.. code-block:: bash

    > jhubctl get cluster
    Clusters:
      - mycluster

Create Hubs.

.. code-block:: bash

    > jhubctl create hub myhub
    Jupyterhub created!

List Hub deployments.

.. code-block:: bash

    > jhubctl get hub
    JupyterHubs:
      - myhub

Delete clusters.

.. code-block:: bash

    > jhubctl delete cluster mycluster
    100%|███████████████████████████████████| 6/6 [00:07<00:00,  1.39s/it]

Getting Started
===============

1. Choose your provider.

Currently, ``jhubctl`` only supports AWS's Elastic Kubernetes Cluster (EKS) service.

2. Install

Follow one of these pages to setup your command line.

* AWS EKS

3. 



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   _sources/eks.rst
   _sources/config.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
