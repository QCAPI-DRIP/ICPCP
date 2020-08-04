import os
import uuid

import requests
import werkzeug.utils
from flask import Flask, request, send_from_directory, abort, redirect, url_for, jsonify
from flask_cors import CORS
import yaml
import requests
from legacy_code.ICPCP_TOSCA import Workflow
from legacy_code.cwlparser import CwlParser
from legacy_code.tosca_generator import ToscaGenerator
import legacy_code.naive_planner as plan
from pprint import pprint
import json

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "planning_input")
app.config['DOWNLOAD_FOLDER'] = os.path.join(os.getcwd(), "planning_output")
app.config['MAX_CONTENT_PATH'] = 1000000
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {'cwl', 'yaml'}

CORS(app, resources={r'/*': {'origins': '*'}})
CURRENT_DIR = os.path.dirname(__file__)


def run_icpc(dag=None, combined_input=None):
    wf = Workflow()
    print(os.getcwd())
    wf.init(dag, combined_input)
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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_from_url(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as out_file:
        response = requests.get(url)
        out_file.write(response.content)


def get_iaas_solution(workflow_file_path, input_file_path, save=None):
    # Run cwl parser
    cwl_parser = CwlParser(workflow_file_path)
    dag = cwl_parser.g
    # print(dag.nodes())
    # print(dag.edges())

    # Load tosca generator
    tosca_gen = ToscaGenerator()
    tosca_gen.load_default_template()

    # Run IC-PCP algorithm
    servers = run_icpc(dag, input_file_path)
    total_cost = 0
    make_span = 0
    # Add needed instances to tosca description
    for i in range(0, len(servers)):
        make_span += servers[i].get_duration()
        total_cost += servers[i].get_cost()
        instance = servers[i]
        x = {'num_cpus': i + 1, 'disk_size': "{} GB".format((i + 1) * 10),
             'mem_size': "{} MB".format(int((i + 1) * 4096))}
        instance.properties = x
        tosca_gen.add_compute_node("server {}".format(i + 1), instance)
        print(servers[i].properties)

    print("Total costs = {}".format(total_cost))
    print("Makespan = {}".format(make_span))

    if save == None:
        return total_cost, make_span
    tosca_file_name = "generated_tosca_description_" + uuid.uuid4().hex
    tosca_file_loc = os.path.join(app.config['DOWNLOAD_FOLDER'], tosca_file_name)
    tosca_gen.write_template_to_file(tosca_file_loc)
    return tosca_file_name


def run_naive_planner(workflow_file_path, input_file_path):
    cwl_parser = CwlParser(workflow_file_path)
    task_names = cwl_parser.tasks
    dag = cwl_parser.g
    servers = plan.naivePlan(dag, input_file_path)
    for vm in servers:
        for task in vm.task_list:
            print("{} -----> {}".format(vm.vm_type, task_names[task]))


def request_metadata(workflow_file=None):
    """Request metadata from the parsers"""
    request_url = "http://localhost:5002/send_file"
    headers = {
        'accept': "application/json",
        'Content-Type': "multipart/form-data"
    }
    if workflow_file is None:
        workflow_file = os.path.join(app.config['UPLOAD_FOLDER'], "compile1.cwl")
    files = {'file': open(workflow_file, 'rb')}

    resp = requests.post(request_url, files=files)
    parser_data = resp.json()
    #request_vm_sizes(parser_data)
    return parser_data


    # pprint(resp)

def request_vm_sizes(parser_data):
    """"""
    request_url = "http://localhost:5001/plan"
    resp = requests.post(request_url, json=parser_data)
    plan_data = resp.json()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename=filename + ".yaml",
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/upload', methods=['POST'])
def upload_files():
    if request.method == 'POST':
        # if 'file' not in request.files:
        #     flash('No file present')
        #     return redirect(request.url)
        micro_service = True
        workflow_file = request.files['workflow_file']
        input_file = request.files['input_file']


        workflow_file_loc = os.path.join(app.config['UPLOAD_FOLDER'],
                                         werkzeug.utils.secure_filename(workflow_file.filename))
        input_file_loc = os.path.join(app.config['UPLOAD_FOLDER'], werkzeug.utils.secure_filename(input_file.filename))
        workflow_file.save(workflow_file_loc)
        input_file.save(input_file_loc)

        #microservice based
        if(micro_service):
            with open(input_file_loc, 'r') as stream:
                data_loaded = yaml.safe_load(stream)
                price = data_loaded[0]["price"]
                deadline = data_loaded[2]["deadline"]
                performance_with_vm = data_loaded[1]["performance"]
                performance = []
                for key, value in performance_with_vm.items():
                    performance.append(value)
            icpcp_parameters = {'price': price, 'performance': performance, 'deadline': deadline}
            parser_data = request_metadata(workflow_file_loc)
            parser_data['icpcp_params'] = icpcp_parameters
            request_vm_sizes(parser_data)

        #non microservice based
        else:
            tosca_file_name = get_iaas_solution(workflow_file_loc, input_file_loc, save=True)
            return redirect(url_for('uploaded_file', filename=tosca_file_name))


@app.route('/optimizer', methods=['POST'])
def compare_performance():
    if request.method == 'POST':
        file_names = []
        filtered_file_names = []
        # tuple in the form of (total_costs, makespan)
        performance_list = []
        files = request.files.getlist("performance_files")

        # read workflow
        workflow_file = request.files['workflow_file']
        workflow_file_loc = os.path.join(app.config['UPLOAD_FOLDER'],
                                         werkzeug.utils.secure_filename(workflow_file.filename))

        # read performance files
        for file in files:
            file_loc = os.path.join(app.config['UPLOAD_FOLDER'],
                                    werkzeug.utils.secure_filename(file.filename))
            file_names.append(file.filename)
            file.save(file_loc)

            # calculate total cost and makespan for each performance file
            perf = get_iaas_solution(workflow_file_loc, file_loc)
            performance_list.append(perf)

        # find tuple with min total costs and link it to corresponding file name
        data_min_costs = {}
        min_total_costs = min(performance_list, key=lambda item: item[0])
        index_min_total_costs = performance_list.index(min_total_costs)
        file_name1 = file_names[index_min_total_costs]
        data_min_costs['id'] = "Lowest cost"
        data_min_costs['name'] = file_name1
        data_min_costs['costs'] = str(min_total_costs[0])
        data_min_costs['makespan'] = str(min_total_costs[1])
        filtered_file_names.append(data_min_costs)

        # the same as above but for makespan
        data_min_makespan = {}
        min_makespan = min(performance_list, key=lambda item: item[1])
        index_min_make_span = performance_list.index(min(performance_list, key=lambda item: item[1]))
        file_name2 = file_names[index_min_total_costs]
        data_min_makespan['id'] = "Lowest makespan"
        data_min_makespan['name'] = file_name2
        data_min_makespan['costs'] = str(min_makespan[0])
        data_min_makespan['makespan'] = str(min_makespan[1])
        filtered_file_names.append(data_min_makespan)

        # the same as above but for total costs + makespan
        data_min_combined = {}
        min_combined = min(performance_list, key=lambda item: item[0] + item[1])
        index_min_combined = performance_list.index(min(performance_list, key=lambda item: item[0] + item[1]))
        file_name3 = file_names[index_min_total_costs]
        data_min_combined['id'] = "Lowest total costs + makespan"
        data_min_combined['name'] = file_name3
        data_min_combined['costs'] = str(min_combined[0])
        data_min_combined['makespan'] = str(min_combined[1])
        filtered_file_names.append(data_min_combined)
        return jsonify(filtered_file_names)

        # tosca_file_name = get_iaas_solution(workflow_file_loc, input_file_loc)
        # return redirect(url_for('uploaded_file', filename=tosca_file_name))
        # return "files uploaded successfully"


# http://127.0.0.1:5000/tosca?git_url=https://raw.githubusercontent.com/common-workflow-library/legacy/master/workflows/compile/compile1.cwl&performance_url=https://pastebin.com/raw/yhz2YsFF
# http://127.0.0.1:5000/tosca_url?workflow_url=https://raw.githubusercontent.com/common-workflow-library/legacy/master/workflows/compile/compile1.cwl&input_url=https://pastebin.com/raw/HakSvgsA
@app.route('/tosca_url', methods=['GET'])
def tosca_url():
    # TODO: Handle wrong requests

    workflow_url = request.args.get('workflow_url', None)
    input_url = request.args.get('input_url', None)

    # set file names
    workflow_file_location = os.path.join(app.config['UPLOAD_FOLDER'],
                                          workflow_url.split("/")[-1] + "_" + uuid.uuid4().hex)
    input_file_location = os.path.join(app.config['UPLOAD_FOLDER'], "input_icpcp_" + uuid.uuid4().hex)

    # download files from url
    get_file_from_url(workflow_url, workflow_file_location)
    get_file_from_url(input_url, input_file_location)

    # get IaaS solution
    tosca_file_name = get_iaas_solution(workflow_file_location, input_file_location)
    # after generating tosca, remove input files
    # if os.path.exists(workflow_file_name):
    #     os.remove(workflow_file_name)
    # if os.path.exists(performance_file_name):
    #     os.remove(performance_file_name)
    # if os.path.exists(deadline_file_name):
    #     os.remove(deadline_file_name)
    # if os.path.exists(price_file_name):
    #     os.remove(price_file_name)

    # send generated tosca description to client
    return redirect(url_for('uploaded_file', filename=tosca_file_name))


if __name__ == '__main__':
    run_without_flask = False
    if run_without_flask:
        # input_pcp = os.path.join(app.config['UPLOAD_FOLDER'], "input_pcp.yaml")
        # workflow_file = os.path.join(app.config['UPLOAD_FOLDER'], "compile1.cwl")
        # # runNaivePlanner(workflow_file, input_pcp)
        # get_iaas_solution(workflow_file, input_pcp)
        request_metadata()
    else:
        app.run()
