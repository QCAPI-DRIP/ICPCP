import yaml
from werkzeug.datastructures import FileStorage
from toscaparser import shell as parser_shell
from toscaparser.tosca_template import ToscaTemplate
from legacy_code.ICPCP_TOSCA import Workflow
import networkx as nx
from legacy_code.cwlparser import CwlParser

def save(file: FileStorage):
    dictionary = yaml.safe_load(file.stream)


def writeToYaml(services):
    with open('data.yml', 'w') as outfile:
        yaml.dump(services, outfile, default_flow_style=False)


def runICPC():
    wf = Workflow()
    workflow_file = 'C:\\Users\\robin\\Documents\\GitHub\\Q-CWOP\\legacy_code\\input/pcp/pcp.dag'
    performance_file = 'C:\\Users\\robin\\Documents\\GitHub\\Q-CWOP\\legacy_code\\input/pcp/performance'
    price_file = 'C:\\Users\\robin\\Documents\\GitHub\\Q-CWOP\\legacy_code\\input/pcp/price'
    deadline_file = 'C:\\Users\\robin\\Documents\\GitHub\\Q-CWOP\\legacy_code\\input/pcp/deadline'
    infrastructure_file = 'C:\\Users\\robin\\Documents\\GitHub\\Q-CWOP\\legacy_code\\input/pcp/inf'
    wf.init(workflow_file, performance_file, price_file, deadline_file)
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

    wf.print_instances()

    print("\n" + start_str)
    if retVal == -1:
        print("\n**** Invalid final configuration ****")
    else:
        final_cost, final_eft = wf.cal_cost()
        print("final configuration: cost=" + str(final_cost) + "  EFT(exit)=" + str(final_eft))


def verifyTOSCA():
    # parser_shell.main("tosca_parser --template-file=python-flask/service/test1.yaml")
    template = ToscaTemplate(path="C:\\Users\\robin\\Documents\\GitHub\\Q-CWOP\\python-flask\\service\\test.yaml")
    template.verify_template()



if __name__ == '__main__':
    # g = cwlToDag('compile1.cwl')
    # g2 = cwlToDag('lobSTR-workflow.cwl')
    dag = CwlParser('lobSTR-workflow.cwl')
    print(dag.g.nodes())
    print(dag.g.edges())


    # with open('lobSTR-workflow.cwl', 'r') as stream:
    #         data = yaml.safe_load(stream)
    #         print(data)
    #
    # print(g.nodes())
    # print(g.edges())
    # print(g2.nodes())
    # print(g2.edges())
