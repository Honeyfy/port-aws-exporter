import logging
import boto3
from aws.resources.extended_resource_handler import ExtendedResourceHandler

logger = logging.getLogger(__name__)


class ASGHandler(ExtendedResourceHandler):
    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.asg_client = boto3.client('autoscaling', region_name=self.region)

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resources(self):
        try:
            asgs = []
            paginator = self.asg_client.get_paginator('describe_auto_scaling_groups')
            for page in paginator.paginate():
                asgs.extend(page['AutoScalingGroups'])

            return [{'identifier': asg['AutoScalingGroupName']} for asg in asgs]
        except Exception as e:
            logger.error(f"An error occurred while fetching the ASG: {e}")
            return None

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resource(self, identifier):
        try:
            response = self.asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[identifier])
            if response.get('AutoScalingGroups'):
                return response['AutoScalingGroups'][0]
        except Exception as e:
            logger.error(f"An error occurred while fetching the ASG: {e}")
            return None
