from definitions import PLANNING_INPUT
import os
import requests
import time
import aiohttp
from concurrent.futures import ThreadPoolExecutor


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


def concurrent_requests():
    # load input
    workflow_file = os.path.join(PLANNING_INPUT, "compile1.cwl")
    input_file = os.path.join(PLANNING_INPUT, "input_pcp.yaml")

    # set ip and port of backend
    backend_ip = "52.224.197.60"
    backend_port = "3001"

    pool = ThreadPoolExecutor(max_workers=5)

    urls = ['http://www.google.com', 'http://www.yahoo.com', 'http://www.bing.com']  # Create a list of urls

    for page in pool.map(fetch, urls):
        # Do whatever you want with the results ...
        print(page[0:100])

if __name__ == '__main__':
    #clear log file
    open('logs.txt', 'w').close()

    #load input
    workflow_file = os.path.join(PLANNING_INPUT, "compile1.cwl")
    input_file = os.path.join(PLANNING_INPUT, "input_pcp.yaml")

    #set ip and port of backend
    backend_ip = "52.224.197.60"
    backend_port = "3001"

    # number of requests to the power of 2 starting with 1 request, e.g. setting it to 4 results in 1, 2, 4, 16
    number_of_requests = 5
    #change this if you want to raise to a different power
    power = 2
    # dont change this variable
    res = 2


    with open("logs.txt", "a") as text_file:
        for i in range(0, number_of_requests):
            start = time.time()
            if i == 0:
                if not request_backend(backend_ip, backend_port, workflow_file, input_file):
                        text_file.write("After 1 request, no valid output ---> {}s response time \n".format(response_time))
                        break


            elif i == 1:
                resp = request_backend(backend_ip, backend_port, workflow_file, input_file)
                resp2 = request_backend(backend_ip, backend_port, workflow_file, input_file)
                if not resp and resp2:
                        text_file.write("After 2 requests, no valid output ---> {}s response time \n".format(response_time))
                        break
            else:
                res = res ** power
                for j in range(0, res):
                    if not request_backend(backend_ip, backend_port, workflow_file, input_file):
                        break

            response_time = time.time() - start
            if i == 0:
                text_file.write("1 number of requests ---> {}s response time \n".format(response_time))
            else:
                text_file.write("{} number of requests ---> {}s response time \n".format(res, response_time))

            time.sleep(5)
