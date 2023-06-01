import logging
import boto3
from aws.resources.extended_resource_handler import ExtendedResourceHandler
from port.entities import create_entities_json, handle_entities

logger = logging.getLogger(__name__)


class SecurityGroupHandler(ExtendedResourceHandler):
    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.ec2_client = boto3.client('ec2', region_name=self.region)
        self.mappings = resource_config['port']['entity']['mappings'][0]
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

    def handle(self):
        # Fetch all Security Groups and process them
        self.logger.info("Fetching all Security Groups")
        response = self.ec2_client.describe_security_groups()

        self.logger.info(f"Received {len(response['SecurityGroups'])} Security Groups")

        entities = []
        for sg in response['SecurityGroups']:
            entity = self.process_security_group(sg)
            entities.append(entity)

        # Handle the processed entities
        self.logger.info("Processing Security Groups")
        aws_entities = self.handle_entities(entities)

        self.logger.info("Finished processing Security Groups")
        return {'aws_entities': aws_entities}

    def process_security_group(self, sg):
        # Process security group and create the entity object
        entity = {
            'identifier': sg['GroupId'],
            'title': sg['GroupName'],
            'blueprint': 'aws_security_group',
            'properties': {
                'groupId': sg['GroupId'],
                'groupName': sg['GroupName'],
                'description': sg['Description'],
                'vpcId': sg['VpcId']
            },
            'relations': {
                'vpc': sg['VpcId']
            }
        }
        return entity

    def handle_entities(self, entities):
        # Handle the entities by creating/updating them in Port
        aws_entities = handle_entities(entities, self.port_client)
        return aws_entities
