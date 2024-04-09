import logging
import time
import boto3
from aws.resources.extended_resource_handler import ExtendedResourceHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RDSAuroraHandler(ExtendedResourceHandler):
    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.rds_client = boto3.client('rds', region_name=self.region)

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resources(self):
        try:
            db_clusters = []
            paginator = self.rds_client.get_paginator('describe_db_clusters')
            for page in paginator.paginate():
                db_clusters.extend(page['DBClusters'])

            for db_cluster in db_clusters:
                db_instances = []
                paginator = self.rds_client.get_paginator('describe_db_instances')
                for page in paginator.paginate(Filters=[{'Name': 'db-cluster-id', 'Values': [db_cluster['DBClusterIdentifier'],]}]):
                    db_instances.extend(page['DBInstances'])
                db_cluster['DBInstances'] = [db_instance['DBInstanceIdentifier'] for db_instance in db_instances]

            return [{'identifier': db_cluster['DBClusterIdentifier']} for db_cluster in db_clusters]
        except Exception as e:
            logger.error(f"An error occurred while fetching the DB cluster: {e}")
            return None

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resource(self, cluster_id):
        try:
            response = self.rds_client.describe_db_clusters(DBClusterIdentifier=cluster_id)
            if response.get('DBClusters'):
                db_cluster = response['DBClusters'][0]
                db_instances = []
                paginator = self.rds_client.get_paginator('describe_db_instances')
                for page in paginator.paginate(Filters=[{'Name': 'db-cluster-id', 'Values': [db_cluster['DBClusterIdentifier'],]}]):
                    db_instances.extend(page['DBInstances'])
                db_cluster['DBInstances'] = [db_instance['DBInstanceIdentifier'] for db_instance in db_instances]
                return db_cluster
        except Exception as e:
            logger.error(f"An error occurred while fetching the DB cluster: {e}")
            return None


class RDSInstanceHandler(ExtendedResourceHandler):
    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.rds_client = boto3.client('rds', region_name=self.region)

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resources(self):
        try:
            db_instances = []
            paginator = self.rds_client.get_paginator('describe_db_instances')
            for page in paginator.paginate():
                db_instances.extend(page['DBInstances'])

            for db_instance in db_instances:
                subnet_group_name = db_instance.get('DBSubnetGroup')
                if subnet_group_name:
                    db_instance['VpcId'] = subnet_group_name.get('VpcId', '')
                    db_instance['Subnets'] = [subnet['SubnetIdentifier'] for subnet in subnet_group_name.get('Subnets', [])]

            return [{'identifier': db_instance['DBInstanceIdentifier']} for db_instance in db_instances]
        except Exception as e:
            logger.error(f"An error occurred while fetching the DB instance: {e}")
            return None

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resource(self, instance_id):
        try:
            response = self.rds_client.describe_db_instances(DBInstanceIdentifier=instance_id)
            if response.get('DBInstances'):
                db_instance = response['DBInstances'][0]
                subnet_group_name = db_instance.get('DBSubnetGroup', '')
                if subnet_group_name:
                    db_instance['VpcId'] = subnet_group_name.get('VpcId', '')
                    db_instance['Subnets'] = [subnet['SubnetIdentifier'] for subnet in
                                              subnet_group_name.get('Subnets', [])]
                return db_instance
        except Exception as e:
            logger.error(f"An error occurred while fetching the DB instance: {e}")
            return None
