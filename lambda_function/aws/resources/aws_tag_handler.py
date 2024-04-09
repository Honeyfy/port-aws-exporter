import logging
import boto3
import json
import os
import time
from aws.resources.extended_resource_handler import ExtendedResourceHandler

logger = logging.getLogger(__name__)

class AWSTagsHandler(ExtendedResourceHandler):
    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.tagging_client = boto3.client('resourcegroupstaggingapi', region_name=self.region)
        self.cache_file_path = '/tmp/tag_cache.json'
        self.cache_lifetime_seconds = 21600  # Cache lifetime in seconds

    def cache_tags(self, tags):
        cache_data = {
            'timestamp': time.time(),
            'data': tags
        }
        with open(self.cache_file_path, 'w') as file:
            json.dump(cache_data, file)

    def load_cached_tags(self):
        if not os.path.exists(self.cache_file_path):
            return None

        with open(self.cache_file_path, 'r') as file:
            cache_data = json.load(file)
            cache_age = time.time() - cache_data['timestamp']
            if cache_age < self.cache_lifetime_seconds:
                return cache_data['data']
            else:
                return None

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resources(self):
        cached_tags = self.load_cached_tags()
        if cached_tags is not None:
            return cached_tags

        try:
            tag_dict = {}
            paginator = self.tagging_client.get_paginator('get_resources')

            for page in paginator.paginate(TagFilters=[]):
                for resource_tag_mapping in page['ResourceTagMappingList']:
                    for tag in resource_tag_mapping['Tags']:
                        tag_key_value = f"{tag['Key']}-{tag['Value']}"
                        if tag_key_value not in tag_dict:
                            tag_dict[tag_key_value] = {'key': tag['Key'], 'value': tag['Value']}

            tags = [{'identifier': tag_key_value, 'tagKey': data['key'], 'tagValue': data['value']} for tag_key_value, data in tag_dict.items()]
            self.cache_tags(tags)
            return tags
        except Exception as e:
            logger.error(f"An error occurred while fetching AWS tags: {e}")
            return None

    @ExtendedResourceHandler.backoff_retry(max_attempts=10, backoff_factor=2)
    def fetch_resource(self, identifier):
        all_tags = self.load_cached_tags()
        if not all_tags:
            all_tags = self.fetch_resources()

        for tag in all_tags:
            if tag['identifier'] == identifier:
                return tag

        logger.error(f"Tag with identifier {identifier} not found")
        return None

