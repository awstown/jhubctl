AWS Elastic Kubernetes Cluster
==============================

"`Amazon EKS`_ runs the Kubernetes management infrastructure for you across multiple AWS availability zones to eliminate a single point of failure. Amazon EKS is certified Kubernetes conformant so you can use existing tooling and plugins from partners and the Kubernetes community. Applications running on any standard Kubernetes environment are fully compatible and can be easily migrated to Amazon EKS."

.. _`Amazon EKS`: https://aws.amazon.com/eks/

Prerequisites
-------------

**jhubctl** interacts with AWS using Amazon's ``boto3`` Python API. This API requires that you have Amazon credentials configured on your local machine. 

1. Install the AWS CLI.
~~~~~~~~~~~~~~~~~~~~~~~

Use ``pip`` to install the AWS command line interface.

.. code-block:: bash

    pip install awscli


First, you must have **admin** privileges on the AWS account where you'll be creating resources.


Install AWS
-----------
