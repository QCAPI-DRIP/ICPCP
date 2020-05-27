from flask import Flask, jsonify, request, Response, send_file, send_from_directory, abort
import requests
from flask_cors import CORS

import yaml
from werkzeug.datastructures import FileStorage
from toscaparser.tosca_template import ToscaTemplate
from legacy_code.ICPCP_TOSCA import Workflow
from legacy_code.cwlparser import CwlParser
from legacy_code.Errors.api_error import APIError
from legacy_code.tosca_generator import ToscaGenerator

import os
import uuid

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config["TOSCA_FILES"] = os.getcwd()

CORS(app, resources={r'/*': {'origins': '*'}})



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

def get_file_from_url(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as out_file:
        response = requests.get(url)
        out_file.write(response.content)




@app.route('/tosca', methods=['GET'])
def tosca():
    git_url = request.args.get('git_url')
    file_name = git_url.split('/')[-1]
    get_file_from_url(git_url, file_name)

    # Run cwl parser
    cwl_parser = CwlParser(file_name)
    dag = cwl_parser.g
    # print(dag.nodes())
    # print(dag.edges())

    # Load tosca generator
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
        x = {'num_cpus': i + 1, 'disk_size': "{} GB".format((i + 1) * 10),
             'mem_size': "{} MB".format(int((i + 1) * 4096))}
        instance.properties = x
        tosca_gen.add_compute_node("server {}".format(i + 1), instance)
        print(servers[i].properties)

    tosca_gen.write_template_to_file("generated_tosca_description")
    # performance_file_url = request.args.get('performance_file_url')
    # deadline_file_url = request.args.get('deadline_file_url')
    # price_file_url = request.args.get('price_file_url')
    # return jsonify("tosca")
    try:
        return send_from_directory(app.config["TOSCA_FILES"], filename="generated_tosca_description.yaml", as_attachment=True)
    except FileNotFoundError:
        abort(404)
    # try:
    #     return Response(
    # except Exception as e:
    #     raise APIError(message=str(e), status_code=400)

# @app.route('/file-downloads/')
# def file_downloads():
#     try:
#         return render_template('downloads.html')
#     except Exception as e:
#         return str(e)


if __name__ == '__main__':
    # git_url = 'https://raw.githubusercontent.com/common-workflow-library/legacy/master/workflows/make-to-cwl/dna.cwl'
    # file_name = git_url.split('/')[-1]
    # get_file_from_url(git_url, file_name)
    app.run()