import logging
import boto3
from aws.resources.extended_resource_handler import ExtendedResourceHandler

logger = logging.getLogger(__name__)


class AccountHandler(ExtendedResourceHandler):

    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.sts_client = boto3.client('sts', region_name=self.region)

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resources(self):
        try:
            caller_identity = self.sts_client.get_caller_identity()
            account = {
                'identifier': caller_identity['Account'],  # set identifier as 'Account'
                'accountId': caller_identity['Account']
            }
            return [account]  # Wrapping it inside a list because the fetch_resources function is expected to return a list
        except Exception as e:
            logger.error(f"An error occurred while fetching the account: {e}")
            return None

    @ExtendedResourceHandler.backoff_retry(max_attempts=3, backoff_factor=2)
    def fetch_resource(self, account_id):
        try:
            caller_identity = self.sts_client.get_caller_identity()
            if caller_identity['Account'] == account_id:
                account = {
                    'identifier': caller_identity['Account'],  # set identifier as 'Account'
                    'accountId': caller_identity['Account']
                }
                return account
            else:
                logger.error(f"Account id mismatch: Expected {account_id}, but got {caller_identity['Account']}")
                return None
        except Exception as e:
            logger.error(f"An error occurred while fetching the account: {e}")
            return None
