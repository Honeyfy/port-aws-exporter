from aws.resources.base_handler import BaseHandler


class ExtendedResourceHandler(BaseHandler):
    def __init__(self, resource_config, port_client, lambda_context, default_region):
        super().__init__(resource_config, port_client, lambda_context, default_region)
        self.region = default_region

    def handle(self):
        # This method should be overridden by subclasses
        # Subclasses should implement the logic to handle the specific resource
        pass
