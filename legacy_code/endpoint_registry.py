import external_apis.kub_create as kub_create

class EndPointRegistry:

    def __init__(self):
        """Parsers are defined as: {file_format : [endpoint]}"""
        self._parsers = {}
        """Planners are defined as: {endpoint : [parameters]}"""
        self._planners = {}

    def add_parser_endpoint(self, name: str, image_repo: str, container_port: int, file_format: str):
        """Use this function to add a parser endpoint to endpoint registry.
        Example endpoint_url: "http://localhost:5002/send_file"
        file_format: ".cwl"
        """

        #TODO: Add check for available ports
        #add endpoint to kubernetes
        cluster_ip = kub_create.create_service(name, container_port)
        kub_create.create_deployment(name, image_repo, container_port)
        self._parsers[file_format] = [cluster_ip]


    def add_planner_endpoint(self, name: str, endpoint_url: str, planner_params: list):
        """Use this function to add a planner endpoint to endpoint registry.
        Example endpoint_url: "http://localhost:5002/send_file"
        planner_params: [price, performance, deadline]
        """
        if name in self._planners:
            raise Exception('This name is already present in the planners.')

        self._planners[name] = (endpoint_url, planner_params)
