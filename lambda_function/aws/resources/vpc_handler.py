import boto3
from aws.resources.extended_resource_handler import ExtendedResourceHandler
import logging

logger = logging.getLogger(__name__)


class VPCHandler(ExtendedResourceHandler):

    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.ec2_client = boto3.client('ec2', region_name=self.region)
        self.sts_client = boto3.client('sts')
        self.account_id = self.sts_client.get_caller_identity().get('Account')

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resources(self):
        try:
            vpcs = []
            paginator = self.ec2_client.get_paginator('describe_vpcs')
            for page in paginator.paginate():
                for vpc in page['Vpcs']:
                    vpc['identifier'] = vpc.get('VpcId')  # set identifier as 'VpcId'
                    vpc['regionName'] = self.region  # add regionName to each vpc
                    vpc['accountId'] = self.account_id  # add accountId to each vpc
                    vpcs.append(vpc)
            return vpcs
        except Exception as e:
            logger.error(f"An error occurred while fetching the VPCs: {e}")
            return None

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resource(self, vpc_id):
        try:
            response = self.ec2_client.describe_vpcs(VpcIds=[vpc_id])
            if response.get('Vpcs'):
                vpc = response['Vpcs'][0]
                vpc['identifier'] = vpc.get('VpcId')  # set identifier as 'VpcId'
                vpc['regionName'] = self.region  # add regionName to the vpc
                vpc['accountId'] = self.account_id  # add accountId to the vpc
                return vpc
        except Exception as e:
            logger.error(f"An error occurred while fetching the VPC: {e}")
            return None
