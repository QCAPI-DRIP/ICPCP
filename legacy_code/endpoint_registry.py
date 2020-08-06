class EndPointRegistry:


    def __init__(self):
        self.parsers = {}
        self.planners = {}

    def add_parser_endpoint(self, name: str, endpoint_url: str, file_format: str):
        """Use this function to add parser endpoint to endpoint registry.
        Example endpoint_url: "http://localhost:5002/send_file"
        file_format: .cwl
        """
        self.parsers[name] = (endpoint_url, file_format)


    def add_planner_endpoint(self, name: str, endpoint_url: str, planner_params: [])
        self.planners[name] = (endpoint_url, planner_params)