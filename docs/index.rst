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


.. code-block:: bash

    > jhubctl get cluster
    Clusters:
      - mycluster


.. code-block:: bash

    > jhubctl create hub myhub
    Jupyterhub created!


.. code-block:: bash

    > jhubctl get hub
    JupyterHubs:
      - myhub

.. code-block:: bash

    > jhubctl delete cluster mycluster
    100%|███████████████████████████████████| 6/6 [00:07<00:00,  1.39s/it]


.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
