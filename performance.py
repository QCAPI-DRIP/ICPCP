from definitions import PLANNING_INPUT
import os
import requests
import time


def request_backend(endpoint, port, workflow_file, input_file):
    request_url = "http://{endpoint}:{port}/upload".format(endpoint=endpoint, port=port)
    files = {'workflow_file': open(workflow_file, 'rb'), 'input_file': open(input_file, 'rb')}

    resp = requests.post(request_url, files=files)
    # empty response
    if not resp.text:
        print("empty response file")
        return False

    return True

def request_cluster():
    request_url = "http://52.188.135.248:80/send_file"
    workflow_file = os.path.join(PLANNING_INPUT, "compile1.cwl")
    files = {'file': open(workflow_file, 'rb')}

    resp = requests.post(request_url, files=files)


if __name__ == '__main__':
    workflow_file = os.path.join(PLANNING_INPUT, "compile1.cwl")
    input_file = os.path.join(PLANNING_INPUT, "input_pcp.yaml")
    # request_backend("localhost", 5001, workflow_file, input_file)

    # number of requests to the power of 2 starting with 1 request, e.g. 1, 2, 4, 8, 16
    number_of_requests = 2
    res = 2
    for i in range(0, number_of_requests):
        start = time.time()
        if i == 0:
            request_backend("localhost", 5001, workflow_file, input_file)
        elif i == 1:
            request_backend("localhost", 5001, workflow_file, input_file)
            request_backend("localhost", 5001, workflow_file, input_file)
        else:
            res = res ** 2
            for j in range(0, res):
                request_backend("localhost", 5001, workflow_file, input_file)
        response_time = time.time() - start
        with open("logs.txt", "a") as text_file:
            text_file.write("{} number of requests ---> {}s response time".format(res, response_time))

        time.sleep(5)
