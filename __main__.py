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
from legacy_code.NewInstance import NewInstance
from definitions import ENDPOINTS_PATH
# from components.endpoint_registry import EndPointRegistry
from components.virtual_machine import VirtualMachine
import json

# set to true for microservice based architecture
MICRO_SERVICE = True

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

    # vm and exit node not part of PCP, so
    # adjust LST, LFT of vm node
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


def get_iaas_solution(workflow_file_path, input_file_path, save=None, microservices=False):
    # Run cwl parser
    cwl_parser = CwlParser(workflow_file_path)
    dag = cwl_parser.g

    # Run IC-PCP algorithm
    servers = run_icpc(dag, input_file_path)

    total_cost = 0
    make_span = 0

    if save == None:
        for i in range(0, len(servers)):
            make_span += servers[i].get_duration()
            total_cost += servers[i].get_cost()

        print("Total costs = {}".format(total_cost))
        print("Makespan = {}".format(make_span))
        return total_cost, make_span

    return generate_tosca(servers)


def generate_tosca(servers, microservices=False):
    # Load tosca geneartor
    tosca_gen = ToscaGenerator()
    tosca_gen.load_default_template()

    for i in range(0, len(servers)):
        instance = servers[i]
        if not microservices:
            x = {'num_cpus': i + 1, 'disk_size': "{} GB".format((i + 1) * 10),
                 'mem_size': "{} MB".format(int((i + 1) * 4096))}
            instance.properties = x
        tosca_gen.add_compute_node("server {}".format(i + 1), instance)

    tosca_file_name = "generated_tosca_description_" + uuid.uuid4().hex
    tosca_file_loc = os.path.join(app.config['DOWNLOAD_FOLDER'], tosca_file_name)
    tosca_gen.write_template_to_file(tosca_file_loc)
    return tosca_file_name
    print(servers[i].properties)


def run_naive_planner(workflow_file_path, input_file_path):
    cwl_parser = CwlParser(workflow_file_path)
    task_names = cwl_parser.tasks
    dag = cwl_parser.g
    servers = plan.naivePlan(dag, input_file_path)
    for vm in servers:
        for task in vm.task_list:
            print("{} -----> {}".format(vm.vm_type, task_names[task]))


def request_metadata(endpoint, port, workflow_file=None):
    """Request metadata from the parsers"""
    request_url = "http://{endpoint}:{port}/send_file".format(endpoint=endpoint, port=port)
    # request_url = "http://10.0.125.227:5003/send_file"
    # request_url = "http://cwl-parser-service.default:32401/send_file"
    if workflow_file is None:
        workflow_file = os.path.join(app.config['UPLOAD_FOLDER'], "compile1.cwl")
    files = {'file': open(workflow_file, 'rb')}

    resp = requests.post(request_url, files=files)
    parser_data = resp.json()
    return parser_data

    # pprint(resp)


def request_vm_sizes(endpoint, port, parser_data):
    """"Request vm sizes from planner"""
    request_url = "http://{endpoint}:{port}/plan".format(endpoint=endpoint, port=port)
    # request_url = "http://icpcp-planner-service.default:30392/plan"
    # request_url = "http://10.0.114.202:5002/plan"
    resp = requests.post(request_url, json=parser_data)
    plan_data = resp.json()
    return plan_data


def get_servers(vm_data):
    """returns (servers, total_cost, highest_end_time)"""
    servers = []
    total_cost = 0
    highest_end_time = 0
    for vm in vm_data:
        tasks = vm['tasks']
        vm_start = vm['vm_start']
        vm_end = vm['vm_end']
        vm_type = vm['vm_type']
        vm_cost = vm['vm_cost']

        properties = {'num_cpus': vm['num_cpus'], 'disk_size': vm['disk_size'], 'mem_size': vm['mem_size']}
        server = NewInstance(vm_type, vm_cost, vm_start, vm_end, tasks)
        server.properties = properties
        server.task_names = tasks

        # add cost of vm to total cost and find vm with highest end time
        total_cost += server.get_cost()
        if vm_end > highest_end_time:
            highest_end_time = vm_end

        servers.append(server)
    return servers, total_cost, highest_end_time


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename=filename + ".yaml",
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)


@app.route('/architecture')
def get_architecture():
    return json.dumps(MICRO_SERVICE)


AVAILABLE_SERVERS = {'Azure': [{'id': 1, 'num_cpus': 1, 'mem_size': "768MB", 'disk_size': "20GB"},
                               {'id': 2, 'num_cpus': 2, 'mem_size': "1.75GB", 'disk_size': "40GB"},
                               {'id': 3, 'num_cpus': 4, 'mem_size': "7GB", 'disk_size': "120GB"}],
                     'Amazon': [{'id': 1, 'num_cpus': 1, 'mem_size': "768MB", 'disk_size': "20GB"},
                                {'id': 2, 'num_cpus': 2, 'mem_size': "1.75GB", 'disk_size': "40GB"},
                                {'id': 3, 'num_cpus': 4, 'mem_size': "7GB", 'disk_size': "120GB"}],
                     'Google Cloud': [{'id': 1, 'num_cpus': 1, 'mem_size': "768MB", 'disk_size': "20GB"},
                                      {'id': 2, 'num_cpus': 2, 'mem_size': "1.75GB", 'disk_size': "40GB"},
                                      {'id': 3, 'num_cpus': 4, 'mem_size': "7GB", 'disk_size': "120GB"}]}


# [VirtualMachine(1, "1", "768MB", "20GB"), VirtualMachine(2, "2", "1.75GB", "40GB"), VirtualMachine(3, "4", "7GB", "120GB")]
@app.route('/get_vms/<provider>')
def get_available_vms(provider):
    vm_list = AVAILABLE_SERVERS[provider]
    return jsonify(vm_list)


@app.route('/load_vm_list', methods=['POST'])
def load_custom_list():
    # if not request.files['file']:
    #     abort(400)

    vm_list_file = request.files['file']
    # save the cwl file
    file_loc = os.path.join(app.config['UPLOAD_FOLDER'],
                            werkzeug.utils.secure_filename(vm_list_file.filename))
    vm_list_file.save(file_loc)

    with open(file_loc, 'r') as stream:
        data_loaded = yaml.safe_load(stream)

    # os.remove(file_loc)

    return jsonify(data_loaded)


performance_indicator_storage = []


@app.route('/performance_indicator/<kpi>')
def get_kpis(kpi):
    if not performance_indicator_storage[0]:
        return jsonify(False)

    result = []
    if kpi == 'makespan':
        min_makespan = min(performance_indicator_storage, key=lambda x: x['makespan'])
        max_makespan = max(performance_indicator_storage, key=lambda x: x['makespan'])
        if (min_makespan['tosca_file_name'] == max_makespan['tosca_file_name']):
            min_makespan['id'] = "Lowest and highest makespan"
            result.append(min_makespan)
            return jsonify(result)

        min_makespan['id'] = "Lowest makespan"
        result.append(min_makespan)
        max_makespan['id'] = "Highest makespan"
        result.append(max_makespan)
        return jsonify(result)

    if kpi == 'total_cost':
        min_total_cost = min(performance_indicator_storage, key=lambda x: x['total_cost'])
        max_total_cost = max(performance_indicator_storage, key=lambda x: x['total_cost'])
        if (min_total_cost['tosca_file_name'] == max_total_cost['tosca_file_name']):
            min_total_cost['id'] = "Lowest lost and highest cost"
            result.append(max_total_cost)
            return jsonify(result)

        min_total_cost['id'] = "Lowest cost"
        max_total_cost['id'] = "Highest cost"
        result.append(min_total_cost)
        result.append(max_total_cost)
        return jsonify(result)


@app.route('/generate', methods=['POST'])
def generate_performance_model():
    # Used for generation of perfromance model
    PERFORMANCE_MAPPER = {1: 16, 2: 8, 3: 4, 4: 2, 5: 1}
    PRICE_MAPPER = {1: 2, 2: 4, 3: 8, 4: 16, 5: 32}

    workflow_file = request.files['workflow_file']
    selected_vms = json.load(request.files['selected_vms'])
    workflow_file_loc = os.path.join(app.config['UPLOAD_FOLDER'],
                                     werkzeug.utils.secure_filename(workflow_file.filename))
    workflow_file.save(workflow_file_loc)
    fixed_endpoint_parser_ip = "localhost"
    fixed_endpoint_parser_port = "5003"

    parser_data = request_metadata(fixed_endpoint_parser_ip, fixed_endpoint_parser_port, workflow_file_loc)

    pcp_input_file = []
    number_of_tasks = len(parser_data['tasks'])
    count = 0

    for vm in selected_vms:
        count += 1
        num_cpus = vm['num_cpus']
        perf_list = [PERFORMANCE_MAPPER[num_cpus] for _ in range(len(selected_vms))]
        if not pcp_input_file:
            pcp_input_file.append({'price': [PRICE_MAPPER[num_cpus]]})
            pcp_input_file.append({'performance': {'vm%s' % count: perf_list}})
        else:
            pcp_input_file[0]['price'].append(PRICE_MAPPER[num_cpus])
            pcp_input_file[1]['performance']['vm%s' % count] = perf_list

    file_name = 'input_pcp_' + uuid.uuid4().hex + '.yaml'
    location_pcp_file = os.path.join(app.config['DOWNLOAD_FOLDER'], file_name)
    with open(location_pcp_file, 'w') as outfile:
        yaml.dump(pcp_input_file, outfile, default_flow_style=False, allow_unicode=True)

    #TODO: remove file after sending

    try:
        return send_from_directory(app.config["DOWNLOAD_FOLDER"], filename=file_name,
                                   as_attachment=True)
    except FileNotFoundError:
        abort(404)






@app.route('/upload', methods=['POST'])
def upload_files():
    if request.method == 'POST':
        # if 'file' not in request.files:
        #     return redirect(request.url)
        added_endpoints = False
        workflow_file = request.files['workflow_file']
        input_file = request.files['input_file']

        # configure this if you dont want to use endpoints from endpointregistry
        # fixed_endpoint_parser_ip = "52.224.203.20"
        # fixed_endpoint_parser_port = "5003"
        # fixed_endpoint_planner_ip = "52.224.203.30"
        # fixed_endpoint_planner_port = "5002"

        fixed_endpoint_parser_ip = "localhost"
        fixed_endpoint_parser_port = "5003"
        fixed_endpoint_planner_ip = "localhost"
        fixed_endpoint_planner_port = "5002"
        fixed_endpoint_planner2_ip = "localhost"
        fixed_endpoint_planner2_port = "5005"

        workflow_file_loc = os.path.join(app.config['UPLOAD_FOLDER'],
                                         werkzeug.utils.secure_filename(workflow_file.filename))
        input_file_loc = os.path.join(app.config['UPLOAD_FOLDER'], werkzeug.utils.secure_filename(input_file.filename))
        workflow_file.save(workflow_file_loc)
        input_file.save(input_file_loc)

        # microservice based
        if MICRO_SERVICE:
            with open(input_file_loc, 'r') as stream:
                data_loaded = yaml.safe_load(stream)
                price = data_loaded[0]["price"]
                deadline = data_loaded[2]["deadline"]
                performance_with_vm = data_loaded[1]["performance"]
                performance = []
                for key, value in performance_with_vm.items():
                    performance.append(value)

            icpcp_parameters = {'price': price, 'performance': performance, 'deadline': deadline}

            # search for available endpoints
            if added_endpoints:
                # find out what microservices are availablea
                parsers_file_loc = os.path.join(ENDPOINTS_PATH, 'parsers.yaml')
                planners_file_loc = os.path.join(ENDPOINTS_PATH, 'planners.yaml')

                with open(parsers_file_loc, 'r') as stream:
                    try:
                        parsers_data = yaml.safe_load(stream)
                    except yaml.YAMLError as exc:
                        print(exc)

                with open(planners_file_loc, 'r') as stream:
                    try:
                        planners_data = yaml.safe_load(stream)
                    except yaml.YAMLError as exc:
                        print(exc)

                parser_endpoints = parsers_data['.cwl']
                planner_endpoints = list(planners_data.keys())

                # list of generated tosca files
                tosca_files = []

                # send workflow file to each available parser that supports its format
                for (endpoint, port) in parser_endpoints:
                    parser_data = request_metadata(endpoint, port, workflow_file_loc)
                    parser_data['icpcp_params'] = icpcp_parameters

                    # send the parser output to each available planner
                    for (endpoint_planner, port_planner) in planner_endpoints:
                        vm_data = request_vm_sizes(endpoint_planner, port_planner, parser_data)
                        servers = []
                        for vm in vm_data:
                            tasks = vm['tasks']
                            vm_start = vm['vm_start']
                            vm_end = vm['vm_end']
                            properties = {'num_cpus': vm['num_cpus'], 'disk_size': vm['disk_size'],
                                          'mem_size': vm['mem_size']}
                            server = NewInstance(0, 0, vm_start, vm_end, tasks)
                            server.properties = properties
                            server.task_names = tasks
                            servers.append(server)
                            tosca_file = generate_tosca(servers, microservices=True)
                            tosca_files.append(tosca_file)
            else:
                parser_data = request_metadata(fixed_endpoint_parser_ip, fixed_endpoint_parser_port, workflow_file_loc)
                parser_data['icpcp_params'] = icpcp_parameters

                vm_data = request_vm_sizes(fixed_endpoint_planner_ip, fixed_endpoint_planner_port, parser_data)
                # vm_data2 = request_vm_sizes(fixed_endpoint_planner2_ip, fixed_endpoint_planner2_port, parser_data)

                servers_icpcp = get_servers(vm_data)
                # servers_icpcp_greedy_repair = get_servers(vm_data2)

                tosca_file_icpcp = generate_tosca(servers_icpcp[0], microservices=True)
                # tosca_file_icpcp_greedy_repair = generate_tosca(servers_icpcp_greedy_repair, microservices=True)
                performance_indicator_storage.append(
                    dict(tosca_file_name=tosca_file_icpcp, total_cost=servers_icpcp[1], makespan=servers_icpcp[2]))
                return jsonify(True)

            # return redirect(url_for('uploaded_file', filename=tosca_file_icpcp))

        # non microservice based
        else:
            tosca_file_name = get_iaas_solution(workflow_file_loc, input_file_loc, save=True)
            return redirect(url_for('uploaded_file', filename=tosca_file_name))


def tosca_microservice_local_test(workflow_file_loc, input_file_loc):
    added_endpoints = False

    # configure this if you dont want to use endpoints from endpointregistry
    fixed_endpoint_parser_ip = "localhost"
    fixed_endpoint_parser_port = "5003"

    fixed_endpoint_planner_ip = "localhost"
    fixed_endpoint_planner_port = "5002"

    fixed_endpoint_planner2_ip = "localhost"
    fixed_endpoint_planner2_port = "5004"

    # microservice based
    if MICRO_SERVICE:
        with open(input_file_loc, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
            price = data_loaded[0]["price"]
            deadline = data_loaded[2]["deadline"]
            performance_with_vm = data_loaded[1]["performance"]
            performance = []
            for key, value in performance_with_vm.items():
                performance.append(value)

        icpcp_parameters = {'price': price, 'performance': performance, 'deadline': deadline}

        # search for available endpoints
        if added_endpoints:
            # find out what microservices are available
            parsers_file_loc = os.path.join(ENDPOINTS_PATH, 'parsers.yaml')
            planners_file_loc = os.path.join(ENDPOINTS_PATH, 'planners.yaml')

            with open(parsers_file_loc, 'r') as stream:
                try:
                    parsers_data = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)

            with open(planners_file_loc, 'r') as stream:
                try:
                    planners_data = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)

            parser_endpoints = parsers_data['.cwl']
            planner_endpoints = list(planners_data.keys())

            # list of generated tosca files
            tosca_files = []

            # send workflow file to each available parser that supports its format
            for (endpoint, port) in parser_endpoints:
                parser_data = request_metadata(endpoint, port, workflow_file_loc)
                parser_data['icpcp_params'] = icpcp_parameters

                # send the parser output to each available planner
                for (endpoint_planner, port_planner) in planner_endpoints:
                    vm_data = request_vm_sizes(endpoint_planner, port_planner, parser_data)
                    servers = []
                    for vm in vm_data:
                        tasks = vm['tasks']
                        vm_start = vm['vm_start']
                        vm_end = vm['vm_end']
                        properties = {'num_cpus': vm['num_cpus'], 'disk_size': vm['disk_size'],
                                      'mem_size': vm['mem_size']}
                        server = NewInstance(0, 0, vm_start, vm_end, tasks)
                        server.properties = properties
                        server.task_names = tasks
                        servers.append(server)
                        tosca_file = generate_tosca(servers, microservices=True)
                        tosca_files.append(tosca_file)
        else:
            parser_data = request_metadata(fixed_endpoint_parser_ip, fixed_endpoint_parser_port, workflow_file_loc)
            parser_data['icpcp_params'] = icpcp_parameters

            # greedy without repair cycle
            vm_data = request_vm_sizes(fixed_endpoint_planner_ip, fixed_endpoint_planner_port, parser_data)
            servers = []
            tosca_files = []
            for vm in vm_data:
                tasks = vm['tasks']
                vm_start = vm['vm_start']
                vm_end = vm['vm_end']
                properties = {'num_cpus': vm['num_cpus'], 'disk_size': vm['disk_size'], 'mem_size': vm['mem_size']}
                server = NewInstance(0, 0, vm_start, vm_end, tasks)
                server.properties = properties
                server.task_names = tasks
                servers.append(server)
                tosca_file = generate_tosca(servers, microservices=True)
                tosca_files.append(tosca_file)

            # greedy with repair cycle
            vm_data2 = request_vm_sizes(fixed_endpoint_planner2_ip, fixed_endpoint_planner2_port, parser_data)
            servers2 = []
            for vm in vm_data2:
                tasks = vm['tasks']
                vm_start = vm['vm_start']
                vm_end = vm['vm_end']
                properties = {'num_cpus': vm['num_cpus'], 'disk_size': vm['disk_size'], 'mem_size': vm['mem_size']}
                server = NewInstance(0, 0, vm_start, vm_end, tasks)
                server.properties = properties
                server.task_names = tasks
                servers.append(server)
                tosca_file2 = generate_tosca(servers, microservices=True)
                tosca_files.append(tosca_file2)

        return True

    # non microservice based
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
        input_pcp = os.path.join(app.config['UPLOAD_FOLDER'], "input_pcp.yaml")
        workflow_file = os.path.join(app.config['UPLOAD_FOLDER'], "compile1.cwl")
        # # runNaivePlanner(workflow_file, input_pcp)
        get_iaas_solution(workflow_file, input_pcp, save=True)
        # request_metadata()
    else:
        port = int(os.environ.get('PORT', 5001))
        app.run(host='0.0.0.0', port=port, debug=False)
        # test_cluster()
