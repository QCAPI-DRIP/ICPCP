import os
import uuid

import requests
import werkzeug.utils
from flask import Flask, request, send_from_directory, abort, redirect, url_for
from flask_cors import CORS

from legacy_code.ICPCP_TOSCA import Workflow
from legacy_code.cwlparser import CwlParser
from legacy_code.tosca_generator import ToscaGenerator

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


def run_icpc(workflow_file, performance_file, price_file, deadline_file, dag=None, combined_input=None):
    wf = Workflow()
    print(os.getcwd())
    infrastructure_file = '../../legacy_code/input/pcp/inf'
    wf.init(workflow_file, performance_file, price_file, deadline_file, dag, combined_input)
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


def get_iaas_solution(workflow_file_path, input_file_path):
    # Run cwl parser
    cwl_parser = CwlParser(workflow_file_path)
    dag = cwl_parser.g
    # print(dag.nodes())
    # print(dag.edges())

    # Load tosca generator
    tosca_gen = ToscaGenerator()
    tosca_gen.load_default_template()

    # # Define input
    # workflow_file = '../../legacy_code/input/pcp/pcp.dag'
    # combined_input = '../../legacy_code/input/pcp/input_pcp.yaml'
    performance_file = '../../legacy_code/input/pcp/performance_compile1'
    price_file = '../../legacy_code/input/pcp/price'
    deadline_file = '../../legacy_code/input/pcp/deadline'
    # # performance_file = performance_file_name
    # price_file = price_file_name
    # deadline_file = deadline_file_name

    # Run IC-PCP algorithm
    servers = run_icpc(workflow_file_path, performance_file, price_file, deadline_file, dag, input_file_path)

    # Add needed instances to tosca description
    for i in range(0, len(servers)):
        instance = servers[i]
        x = {'num_cpus': i + 1, 'disk_size': "{} GB".format((i + 1) * 10),
             'mem_size': "{} MB".format(int((i + 1) * 4096))}
        instance.properties = x
        tosca_gen.add_compute_node("server {}".format(i + 1), instance)
        print(servers[i].properties)

    tosca_file_name = "generated_tosca_description_" + uuid.uuid4().hex
    tosca_file_loc = os.path.join(app.config['DOWNLOAD_FOLDER'], tosca_file_name)
    tosca_gen.write_template_to_file(tosca_file_loc)
    return tosca_file_name


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

        workflow_file = request.files['workflow_file']
        input_file = request.files['input_file']
        workflow_file_loc = os.path.join(app.config['UPLOAD_FOLDER'],
                                         werkzeug.utils.secure_filename(workflow_file.filename))
        input_file_loc = os.path.join(app.config['UPLOAD_FOLDER'], werkzeug.utils.secure_filename(input_file.filename))
        workflow_file.save(workflow_file_loc)
        input_file.save(input_file_loc)
        tosca_file_name = get_iaas_solution(workflow_file_loc, input_file_loc)
        return redirect(url_for('uploaded_file', filename=tosca_file_name))
        return "files uploaded successfully"


# http://127.0.0.1:5000/tosca?git_url=https://raw.githubusercontent.com/common-workflow-library/legacy/master/workflows/compile/compile1.cwl&performance_url=https://pastebin.com/raw/yhz2YsFF
# http://127.0.0.1:5000/tosca_url?workflow_url=https://raw.githubusercontent.com/common-workflow-library/legacy/master/workflows/compile/compile1.cwl&input_url=https://pastebin.com/raw/HakSvgsA
@app.route('/tosca_url', methods=['GET'])
def tosca_url():

    # TODO: Handle wrong requests

    workflow_url = request.args.get('workflow_url', None)
    input_url = request.args.get('input_url', None)
    # performance_url = request.args.get('performance_url', None)
    # deadline_url = request.args.get('deadline_url', None)
    # price_url = request.args.get('price_url', None)

    # set file names
    workflow_file_location = os.path.join(app.config['UPLOAD_FOLDER'], workflow_url.split("/")[-1] + "_" + uuid.uuid4().hex)
    input_file_location = os.path.join(app.config['UPLOAD_FOLDER'], "input_icpcp_" + uuid.uuid4().hex)
    # performance_file_name = os.path.join(input_folder, "performance_" + uuid.uuid4().hex)
    # deadline_file_name = os.path.join(input_folder, "deadline_" + uuid.uuid4().hex)
    # price_file_name = os.path.join(input_folder, "price_" + uuid.uuid4().hex)

    # download files from url
    get_file_from_url(workflow_url, workflow_file_location)
    get_file_from_url(input_url, input_file_location)
    # get_file_from_url(performance_url, performance_file_name)
    # get_file_from_url(deadline_url, deadline_file_name)
    # get_file_from_url(price_url, price_file_name)

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
    # git_url = 'http://127.0.0.1:5000/tosca?git_url=https://raw.githubusercontent.com/common-workflow-library/legacy/master/workflows/compile/compile1.cwl&performance_url=https://pastebin.com/raw/yhz2YsFF&deadline_url=https://pastebin.com/raw/1Y7XEFe8&price_url=https://pastebin.com/raw/ZaNbfLzP'
    # file_name = git_url.split('/')[-1]
    # get_file_from_url(git_url, file_name)
    app.run()
