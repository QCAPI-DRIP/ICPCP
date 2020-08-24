import external_apis.kub_create as kub_create
import io
import yaml
import os
from definitions import ENDPOINTS_PATH

class EndPointRegistry:

    def __init__(self):
        """Parsers are defined as: {file_format : [endpoint]}"""
        self._parsers = {}
        """Planners are defined as: {endpoint : [parameters]}"""
        self._planners = {}

    def add_parser_endpoint(self, name: str, image_repo: str, container_port: int, file_format: str):
        """Use this function to add a parser endpoint to endpoint registry.
        """
        if name in self._parsers:
            raise Exception('This name is already present in the planners.')
        #TODO: Add check for available ports
        #TODO: Check if service and deployment are already on current k8 cluster
        #add endpoint to kubernetes
        cluster_ip = kub_create.create_service(name, container_port)
        kub_create.create_deployment(name, image_repo, container_port)
        self._parsers[file_format] = [cluster_ip]

        return True


    def add_planner_endpoint(self, name: str, image_repo: str, container_port: int, planner_params: list):
        """Use this function to add a planner endpoint to endpoint registry.
        Example endpoint_url: "http://localhost:5002/send_file"
        planner_params: [price, performance, deadline]
        """
        # if name in self._planners:
        #     raise Exception('This name is already present in the planners.')

        # add endpoint to kubernetes
        if name in self._planners:
            raise Exception('This name is already present in the planners.')
        cluster_ip = kub_create.create_service(name, container_port)
        kub_create.create_deployment(name, image_repo, container_port)

        self._planners[cluster_ip] = planner_params
        return True

    def safe_endpoints(self):
        """Write endpoints to yaml file such that they can be used by the backend"""
        parser_file_loc = os.path.join(ENDPOINTS_PATH, 'parsers.yaml')
        planner_file_loc = os.path.join(ENDPOINTS_PATH, 'planners.yaml')
        if self._parsers:
            with open(parser_file_loc, 'w', encoding='utf8') as outfile:
                yaml.dump(self._parsers, outfile, default_flow_style=False, allow_unicode=True)

        if self._planners:
            with open(planner_file_loc, 'w', encoding='utf8') as outfile:
                yaml.dump(self._planners, outfile, default_flow_style=False, allow_unicode=True)


if __name__ == '__main__':
    registry = EndPointRegistry()
    #registry.add_parser_endpoint("test-parser", "masterminded/cwl-parser:latest", 5050, ".cwl")
    registry.add_planner_endpoint("test-planner", "masterminded/icpcp-planner:latest", 5051, [])
    registry.safe_endpoints()