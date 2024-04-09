import logging
import boto3
from aws.resources.extended_resource_handler import ExtendedResourceHandler

logger = logging.getLogger(__name__)


class RegionHandler(ExtendedResourceHandler):

    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.ec2_client = boto3.client('ec2', region_name=self.region)

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resources(self):
        try:
            response = self.ec2_client.describe_regions()
            logger.info("regions: %s" % response)
            regions = response['Regions']
            resources = [{'identifier': region['RegionName'], 'RegionName': region['RegionName'], 'OptInStatus': region['OptInStatus']} for region in regions]
            logger.info("resources: %s" % resources)
            return resources
        except Exception as e:
            logger.error(f"An error occurred while fetching the regions: {e}")
            return None


    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resource(self, region_name):
        try:
            response = self.ec2_client.describe_regions()
            for region in response['Regions']:
                if region['RegionName'] == region_name:
                    return {'identifier': region_name, 'RegionName': region['RegionName'], 'OptInStatus': region['OptInStatus']}
            logger.error(f"Region {region_name} not found")
            return None
        except Exception as e:
            logger.error(f"An error occurred while fetching the region: {e}")
            return None

