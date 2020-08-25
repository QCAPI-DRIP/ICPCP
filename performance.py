from definitions import PLANNING_INPUT
import os
import requests

def request_backend(endpoint, port, workflow_file, input_file):
    request_url = "http://{endpoint}:{port}/upload".format(endpoint=endpoint, port=port)
    files = {'workflow_file': open(workflow_file, 'rb'), 'input_file': open(input_file, 'rb')}

    resp = requests.post(request_url, files=files)
    #empty response
    if not resp.text:
        print("empty response file")

def request_cluster():
    request_url = "http://52.188.135.248:80/send_file"
    workflow_file = os.path.join(PLANNING_INPUT, "compile1.cwl")
    files = {'file': open(workflow_file, 'rb')}

    resp = requests.post(request_url, files=files)


if __name__ == '__main__':
    workflow_file = os.path.join(PLANNING_INPUT, "compile1.cwl")
    input_file = os.path.join(PLANNING_INPUT, "input_pcp.yaml")
    request_backend("localhost", 5001, workflow_file, input_file)