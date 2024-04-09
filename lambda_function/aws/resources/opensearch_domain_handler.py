import logging
import boto3
from aws.resources.extended_resource_handler import ExtendedResourceHandler
from datetime import datetime

logger = logging.getLogger(__name__)

class OpenSearchDomainHandler(ExtendedResourceHandler):
    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.opensearch_client = boto3.client('opensearch', region_name=self.region)

    def convert_datetime(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d')  # or '%Y-%m-%d %H:%M:%S' for including time
        return obj  # Return the object as is if it's not a datetime

    def fetch_resources(self):
        try:
            response = self.opensearch_client.list_domain_names()
            domain_names = response.get('DomainNames', [])
            domains = []

            for domain in domain_names:
                domain_name = domain.get('DomainName')
                if domain_name:
                    detailed_info = self.fetch_resource(domain_name)
                    if detailed_info:
                        # Construct an identifier for each domain
                        # detailed_info['identifier'] = "{}-{}".format(detailed_info.get('ARN').split(':')[4], domain_name)
                        detailed_info['identifier'] = domain_name
                        domains.append(detailed_info)

            return domains
        except Exception as e:
            logger.error(f"An error occurred while fetching OpenSearch domains: {e}")
            return []

    def fetch_resource(self, domain_name):
        try:
            response = self.opensearch_client.describe_domain(DomainName=domain_name)
            detailed_info = response.get('DomainStatus')

            # Recursively convert all datetime objects to strings
            def recursive_datetime_convert(item):
                if isinstance(item, dict):
                    return {k: recursive_datetime_convert(v) for k, v in item.items()}
                elif isinstance(item, list):
                    return [recursive_datetime_convert(v) for v in item]
                elif isinstance(item, datetime):
                    return self.convert_datetime(item)
                else:
                    return item

            detailed_info = recursive_datetime_convert(detailed_info)

            return detailed_info
        except Exception as e:
            logger.error(f"An error occurred while fetching OpenSearch domain '{domain_name}': {e}")
            return None
