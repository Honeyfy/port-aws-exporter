import logging
import boto3
from datetime import datetime
from aws.resources.extended_resource_handler import ExtendedResourceHandler

logger = logging.getLogger(__name__)

class EKSClusterHandler(ExtendedResourceHandler):
    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.eks_client = boto3.client('eks', region_name=self.region)
        self.ec2_client = boto3.client('ec2', region_name=self.region)
    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resources(self):
        try:
            clusters = []
            paginator = self.eks_client.get_paginator('list_clusters')
            for page in paginator.paginate():
                for cluster_name in page['clusters']:
                    clusters.append(self.fetch_resource(cluster_name))
            return clusters
        except Exception as e:
            logger.error(f"An error occurred while fetching EKS clusters: {e}")
            return None

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resource(self, cluster_name):
        try:
            response = self.eks_client.describe_cluster(name=cluster_name)
            cluster_info = response['cluster']
            # vpc_id = self._get_vpc_id_from_subnets(cluster_info['resourcesVpcConfig']['subnetIds']) if cluster_info['resourcesVpcConfig']['subnetIds'] else None
            return {
                'identifier': cluster_info['name'],
                'arn': cluster_info['arn'],
                'createdAt': cluster_info['createdAt'].strftime('%Y-%m-%d'),
                'version': cluster_info['version'],
                'endpoint': cluster_info['endpoint'],
                'roleArn': cluster_info['roleArn'],
                'status': cluster_info['status'],
                'health': cluster_info['health']['issues'],
                'tags': cluster_info.get('tags', {}),
                'subnetIds': cluster_info['resourcesVpcConfig']['subnetIds'],
                'securityGroupIds': cluster_info['resourcesVpcConfig']['securityGroupIds'],
                'openIdConnectIssuerUrl': cluster_info['identity']['oidc']['issuer'],
                'endpointPublicAccess': cluster_info['resourcesVpcConfig']['endpointPublicAccess'],
                'endpointPrivateAccess': cluster_info['resourcesVpcConfig']['endpointPrivateAccess'],
                'publicAccessCidrs': cluster_info['resourcesVpcConfig']['publicAccessCidrs'],
                'vpcId': cluster_info['resourcesVpcConfig']['vpcId']
            }
        except Exception as e:
            logger.error(f"An error occurred while fetching EKS cluster '{cluster_name}': {e}")
            return None

    # def _get_vpc_id_from_subnets(self, subnet_ids):
    #     if subnet_ids:
    #         response = self.ec2_client.describe_subnets(SubnetIds=[subnet_ids[0]])
    #         return response['Subnets'][0]['VpcId']
    #     return None
