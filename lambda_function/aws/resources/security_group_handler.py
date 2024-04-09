import logging
import boto3
from aws.resources.extended_resource_handler import ExtendedResourceHandler

logger = logging.getLogger(__name__)


class SecurityGroupHandler(ExtendedResourceHandler):

    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.ec2_client = boto3.client('ec2', region_name=self.region)

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resources(self):
        try:
            security_groups = []
            paginator = self.ec2_client.get_paginator('describe_security_groups')
            for page in paginator.paginate():
                security_groups.extend(page['SecurityGroups'])

            for sg in security_groups:
                sg['identifier'] = sg.get('GroupId')  # set identifier as 'GroupId'
            return security_groups
        except Exception as e:
            logger.error(f"An error occurred while fetching the security groups: {e}")
            return None

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resource(self, group_id):
        try:
            response = self.ec2_client.describe_security_groups(GroupIds=[group_id])
            if response.get('SecurityGroups'):
                security_group = response['SecurityGroups'][0]
                security_group['identifier'] = security_group.get('GroupId')  # set identifier as 'GroupId'
                return security_group
        except Exception as e:
            logger.error(f"An error occurred while fetching the security group: {e}")
            return None
