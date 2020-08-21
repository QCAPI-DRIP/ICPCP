import external_apis.kub_create as kub_create
import io
import yaml
import os

SAFE_LOCATION_ENDPOINTS = os.getcwd()
class EndPointRegistry:

    def __init__(self):
        """Parsers are defined as: {file_format : [endpoint]}"""
        self._parsers = {}
        """Planners are defined as: {endpoint : [parameters]}"""
        self._planners = {}

    def add_parser_endpoint(self, name: str, image_repo: str, container_port: int, file_format: str):
        """Use this function to add a parser endpoint to endpoint registry.
        """

        #TODO: Add check for available ports
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
        cluster_ip = kub_create.create_service(name, container_port)
        kub_create.create_deployment(name, image_repo, container_port)
        if name in self._planners:
            raise Exception('This name is already present in the planners.')
        self._planneres[name] = cluster_ip
        return True

    def safe_endpoints(self):
        """Write endpoints to yaml file such that they can be used by the backend"""
        with io.open('parsers.yaml', 'w', encoding='utf8') as outfile:
            yaml.dump(self._parsers, outfile, default_flow_style=False, allow_unicode=True)

        with io.open('planners.yaml', 'w', encoding='utf8') as outfile:
            yaml.dump(self.planners, outfile, default_flow_style=False, allow_unicode=True)


if __name__ == '__main__':
    BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
    print(BASE_DIR)