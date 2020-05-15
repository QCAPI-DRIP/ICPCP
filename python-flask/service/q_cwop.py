import yaml
from werkzeug.datastructures import FileStorage
from toscaparser.tosca_template import ToscaTemplate
from legacy_code.ICPCP_TOSCA import Workflow
from legacy_code.cwlparser import CwlParser
from legacy_code.tosca_generator import ToscaGenerator
import os


def save(file: FileStorage):
    dictionary = yaml.safe_load(file.stream)


def write_to_yaml(data):
    with open('data.yml', 'w') as yaml_output:
        yaml.dump(data, yaml_output, default_flow_style=False)


def run_icpc(workflow_file, performance_file, price_file, deadline_file, dag=None):
    wf = Workflow()
    print(os.getcwd())
    infrastructure_file = '../../legacy_code/input/pcp/inf'
    wf.init(workflow_file, performance_file, price_file, deadline_file, dag)
    wf.calc_startConfiguration(-1)

    start_cost, start_eft = wf.getStartCost()
    start_str = "start configuartion: cost=" + str(start_cost) + "  EFT(exit)=" + str(start_eft)
    print("\nStart situation")
    wf.printGraphTimes()

    wf.ic_pcp()
    print("\nEnd situation")
    wf.printGraphTimes()

    # entry and exit node not part of PCP, so
    # adjust LST, LFT of entry node
    # adjust EST, EFT of exit node
    wf.update_node(0)
    wf.update_node(wf.number_of_nodes() - 1)
    #
    # # check PCP end situation
    wf.updateGraphTimes()

    retVal = wf.checkGraphTimes()
    print("checkGraphTimes: retVal=" + str(retVal))
    tot_idle = wf.checkIdleTime()
    print("checkIdleTime: idle time=" + str(tot_idle))

    wf.print_instances(tot_idle)

    print("\n" + start_str)
    if retVal == -1:
        print("\n**** Invalid final configuration ****")
    else:
        final_cost, final_eft = wf.cal_cost()
        print("final configuration: cost=" + str(final_cost) + "  EFT(exit)=" + str(final_eft))

    return wf.instances


def verify_tosca(filepath):
    """Verify correctness of tosca template"""
    # parser_shell.main("tosca_parser --template-file=python-flask/service/test1.yaml")
    template = ToscaTemplate(path=filepath)
    template.verify_template()


if __name__ == '__main__':
    # Run cwl parser
    cwl_parser = CwlParser('compile1.cwl')
    dag = cwl_parser.g
    # print(dag.nodes())
    # print(dag.edges())

    #Load tosca generator
    tosca_gen = ToscaGenerator()
    tosca_gen.load_default_template()


    # Define input
    workflow_file = '../../legacy_code/input/pcp/pcp.dag'
    performance_file = '../../legacy_code/input/pcp/performance_compile1'
    price_file = '../../legacy_code/input/pcp/price'
    deadline_file = '../../legacy_code/input/pcp/deadline'

    # Run IC-PCP algorithm
    servers = run_icpc(workflow_file, performance_file, price_file, deadline_file, dag)

    # Add needed instances to tosca description
    for i in range(0, len(servers)):
        instance = servers[i]
        x = {'num_cpus': i + 1, 'disk_size': "{} GB".format((i + 1) * 10), 'mem_size': "{} MB".format(int((i + 1) * 4096))}
        instance.properties = x
        tosca_gen.add_compute_node("server {}".format(i + 1), instance)
        #print(servers[i].properties)

    tosca_gen.write_template_to_file("generated_tosca_description")

    # #Verify correctness of generated tosca file
    # verify_tosca("generated_tosca_description.yaml")


