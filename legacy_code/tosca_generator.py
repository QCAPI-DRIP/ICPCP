import yaml


class ToscaGenerator:

    def __init__(self, instances):
        self.instances = instances

    def define_node_templates(self):
        "Compute nodes will be generated here"
        pass

    def load_default_template(self):
        with open('default_tempalte.yaml', 'r') as stream:
            data = yaml.safe_load(stream)

        return data
