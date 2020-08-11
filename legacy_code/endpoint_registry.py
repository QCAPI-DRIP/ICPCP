class EndPointRegistry:

    def __init__(self):
        self._parsers = {}
        self._planners = {}

    def add_parser_endpoint(self, name: str, endpoint_url: str, file_format: str):
        """Use this function to add a parser endpoint to endpoint registry.
        Example endpoint_url: "http://localhost:5002/send_file"
        file_format: ".cwl"
        """
        if name in self._parsers:
            raise Exception('This name is already present in the parsers.')

        self._parsers[name] = (endpoint_url, file_format)

    def add_planner_endpoint(self, name: str, endpoint_url: str, planner_params: list):
        """Use this function to add a planner endpoint to endpoint registry.
        Example endpoint_url: "http://localhost:5002/send_file"
        planner_params: [price, performance, deadline]
        """
        if name in self._planners:
            raise Exception('This name is already present in the planners.')

        self._planners[name] = (endpoint_url, planner_params)
