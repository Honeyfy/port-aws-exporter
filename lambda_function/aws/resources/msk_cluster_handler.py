import logging
import boto3
from botocore.exceptions import ClientError
from aws.resources.extended_resource_handler import ExtendedResourceHandler

logger = logging.getLogger(__name__)

class MSKClusterHandler(ExtendedResourceHandler):
    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.msk_client = boto3.client('kafka', region_name=self.region)

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resources(self):
        clusters = []
        try:
            paginator = self.msk_client.get_paginator('list_clusters')
            for page in paginator.paginate():
                for cluster_info in page['ClusterInfoList']:
                    clusters.append(self.fetch_resource(cluster_info['ClusterArn']))
            return clusters
        except ClientError as e:
            logger.error(f"An error occurred while fetching MSK clusters: {e}")
            return []

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resource(self, cluster_arn):
        try:
            response = self.msk_client.describe_cluster(ClusterArn=cluster_arn)
            cluster_details = response['ClusterInfo']
            # Transform the AWS API response to match the Port blueprint
            port_format_cluster = {
                'identifier': cluster_details['ClusterName'],
                'arn': cluster_details['ClusterArn'],
                'kafkaVersion': cluster_details['CurrentBrokerSoftwareInfo']['KafkaVersion'],
                'numberOfBrokerNodes': cluster_details['NumberOfBrokerNodes'],
                'brokerNodeGroupInfo': {
                    'instanceType': cluster_details['BrokerNodeGroupInfo']['InstanceType'],
                    'clientSubnets': cluster_details['BrokerNodeGroupInfo']['ClientSubnets'],
                    'securityGroups': cluster_details['BrokerNodeGroupInfo']['SecurityGroups']
                },
                'state': cluster_details['State']
            }
            return port_format_cluster
        except ClientError as e:
            logger.error(f"An error occurred while fetching MSK cluster details for {cluster_arn}: {e}")
            return None

