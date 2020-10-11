import yaml
from legacy_code.NewInstance import NewInstance

COMPUTE_TEMPLATE_CODE = """
interfaces:
  Standard:
     create: "dumy.yaml"
type: "tosca.nodes.QC.VM.Compute"
                        """

TOPOLOGY_TEMPLATE_CODE = """
properties:
    domain: "Frankfurt"
    provider: "EC2"
requirements: null
interfaces:
    CloudsStorm:
      delete:
        inputs:
          code_type: "SEQ"
          object_type: "SubTopology"
      hscale:
        inputs:
          code_type: "SEQ"
          object_type: "SubTopology"
      provision:
        inputs:
          code_type: "SEQ"
          object_type: "SubTopology"
      start:
        inputs:
          code_type: "SEQ"
          object_type: "SubTopology"
      stop:
        inputs:
          code_type: "SEQ"
          object_type: "SubTopology"
type: "tosca.nodes.QC.VM.topology"
"""

DESCRIPTION_TEMPLATE = """
description: "TOSCA template"
imports:
- nodes: "https://raw.githubusercontent.com/QCDIS/sdia-tosca/master/types/nodes.yaml"
- data: "https://raw.githubusercontent.com/QCDIS/sdia-tosca/master/types/data.yml"
- capabilities: "https://raw.githubusercontent.com/QCDIS/sdia-tosca/master/types/capabilities.yaml"
- policies: "https://raw.githubusercontent.com/QCDIS/sdia-tosca/master/types/policies.yaml"
- interfaces: "https://raw.githubusercontent.com/QCDIS/sdia-tosca/master/types/interfaces.yml"
"""


class ToscaGenerator:

    def __init__(self):
        self.template = None
        self.topology_vms = []

    def add_compute_node(self, name, instance):
        """Add compute nodes to tosca template"""
        properties = instance.properties
        vm_dict = {'vm': {'capability': "tosca.capabilities.QC.VM", 'node': name,
                          'relationship': "tosca.relationships.DependsOn"}}
        self.topology_vms.append(vm_dict)

        if self.template is not None:
            template_dict = yaml.load(COMPUTE_TEMPLATE_CODE)
            properties_dict = {'properties': properties}
            combined_dict = {**properties_dict, **template_dict}
            if 'topology_template' in self.template and 'node_templates' in self.template['topology_template']:
                if self.template['topology_template']['node_templates'] is None:
                    self.template['topology_template']['node_templates'] = {name: combined_dict}
                else:
                    self.template['topology_template']['node_templates'][name] = combined_dict
            else:
                print("Invalid tosca template provided")
        else:
            print("First load a tosca template")

    def add_topology(self):
        if self.topology_vms is not None:
            toplogy_dict = yaml.load(TOPOLOGY_TEMPLATE_CODE)
            toplogy_dict['requirements'] = self.topology_vms
            if 'topology_template' in self.template and 'node_templates' in self.template['topology_template']:
                if self.template['topology_template']['node_templates'] is None:
                    self.template['topology_template']['node_templates'] = toplogy_dict
                else:
                    self.template['topology_template']['node_templates']['topology'] = toplogy_dict
            else:
                print("Invalid tosca template provided")
        else:
            print("First add compute node(s)")

    def add_description(self):
        description_dict = yaml.load(DESCRIPTION_TEMPLATE)
        combined_dict = {**self.template, **description_dict}
        self.template = combined_dict


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
    instances = NewInstance(0, 0, 0, 0, [])
    instances.properties = {'disk_size': "20 GB", 'mem_size': "4098 MB", 'num_cores' : 1, 'os': "Ubuntu 18.04",
                            'user_name': "vm_user"}
    tosca_gen = ToscaGenerator()
    tosca_gen.load_default_template()
    tosca_gen.add_compute_node("db_server", instances)
    tosca_gen.add_topology()
    tosca_gen.add_description()
    tosca_gen.write_template_to_file("testyaml9")
    print(tosca_gen.template)
