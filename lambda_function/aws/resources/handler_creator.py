from typing import Dict, Type

from aws.resources.base_handler import BaseHandler
from aws.resources.cloudcontrol_handler import CloudControlHandler
from aws.resources.cloudformation_handler import CloudFormationHandler
from aws.resources.security_group_handler import SecurityGroupHandler
from aws.resources.asg_handler import ASGHandler
from aws.resources.rds_aurora_handler import RDSAuroraHandler
from aws.resources.rds_aurora_handler import RDSInstanceHandler
from aws.resources.account_handler import AccountHandler
from aws.resources.region_handler import RegionHandler
from aws.resources.vpc_handler import VPCHandler
from aws.resources.eks_cluster_handler import EKSClusterHandler
from aws.resources.aws_tag_handler import AWSTagsHandler
from aws.resources.opensearch_domain_handler import OpenSearchDomainHandler
from aws.resources.msk_cluster_handler import MSKClusterHandler


SPECIAL_AWS_HANDLERS: Dict[str, Type[BaseHandler]] = {
    "AWS::Account": AccountHandler,
    "AWS::Region": RegionHandler,
    ## 'AWS::AvailableTags': AWSTagsHandler,
    "AWS::EC2::VPC": VPCHandler,
    "AWS::CloudFormation::Stack": CloudFormationHandler,
    'AWS::EC2::SecurityGroup': SecurityGroupHandler,
    'AWS::EKS::Cluster': EKSClusterHandler,
    'AWS::AutoScaling::AutoScalingGroup': ASGHandler,
    'AWS::RDS::DBCluster': RDSAuroraHandler,
    'AWS::RDS::DBInstance': RDSInstanceHandler,
    'AWS::OpenSearch::Domain': OpenSearchDomainHandler,
    'AWS::MSK::Cluster': MSKClusterHandler,
}


def create_resource_handler(resource_config, port_client, lambda_context, default_region):
    handler = SPECIAL_AWS_HANDLERS.get(resource_config['kind'], CloudControlHandler)
    print(f"handler: '{handler}'")
    return handler(resource_config, port_client, lambda_context, default_region)