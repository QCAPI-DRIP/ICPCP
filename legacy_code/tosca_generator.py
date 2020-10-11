import yaml
from legacy_code.NewInstance import NewInstance


class ToscaGenerator:

    def __init__(self):
        self.template = None

    def add_compute_node(self, name, instance):
        """Add compute nodes to tosca template"""
        properties = instance.properties
        if self.template is not None:
            mydict = {'type' : "tosca.nodes.Compute", 'capabilities' : {'host' : {'properties' : properties}}}
            if 'topology_template' in self.template and 'node_templates' in self.template['topology_template']:
                    if self.template['topology_template']['node_templates'] is None:
                        self.template['topology_template']['node_templates'] = {name : mydict}
                    else:
                        self.template['topology_template']['node_templates'][name] = mydict
            else:
                print("Invalid tosca template provided")
        else:
            print("First load a tosca template")




    def load_default_template(self):
        with open('default_template.yaml', 'r') as stream:
            data = yaml.safe_load(stream)
        self.template = data

    def write_template_to_file(self, filename):
        if self.template is not None:
            with open(filename + ".yaml", 'w') as yaml_output:
                yaml.dump(self.template, yaml_output, default_flow_style=False, sort_keys=False)
        else:
            "First load a template before writing to file"

if __name__ == '__main__':
    instances = NewInstance(0, 0, 0, 0)
    instances.properties = {'num_cpus': 2, 'disk_size': "20 GB", 'mem_size': "4098 MB"}
    tosca_gen = ToscaGenerator(instances)
    tosca_gen.load_default_template()
    tosca_gen.add_compute_node("db_server")
    tosca_gen.write_template_to_file("testyaml3")
    print(tosca_gen.template)

