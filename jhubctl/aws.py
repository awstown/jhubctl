import boto3

client = boto3.client('cloudformation')
waiter = client.get_waiter('stack_create_complete')
cf = boto3.resource('cloudformation')
iam = boto3.client('iam')
