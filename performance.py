from definitions import PLANNING_INPUT
import os
import requests
import time
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import matplotlib.pyplot as plt


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


def plot_to_graph(x, y):
    # plotting the points
    plt.plot(x, y)

    # naming the x axis
    plt.xlabel('Number of requests')
    # naming the y axis
    plt.ylabel('Response time')

    # giving a title to my graph
    plt.title('Performnace study')

    # function to show the plot
    plt.show()

def plot_multi_graph(x1, y1, x2, y2):
    plt.plot(x1, y1, label="monolithic")

    plt.plot(x2, y2, label="microservices")

    # naming the x axis
    plt.xlabel('number of requests')
    # naming the y axis
    plt.ylabel('response time')
    # giving a title to my graph
    plt.title('Microservices vs monolithic')

    # show a legend on the plot
    plt.legend()

    # function to show the plot
    plt.show()

def concurrent_requests(number_of_requests_rounds, factor, interval, backend_ip, backend_port):
    # load input
    workflow_file = os.path.join(PLANNING_INPUT, "compile1.cwl")
    input_file = os.path.join(PLANNING_INPUT, "input_pcp.yaml")

    x_axis_requests = []
    y_axis_response_time = []

    # We can use a with statement to ensure threads are cleaned up promptly
    futures = []
    number_of_requests = 1
    with open("logs.txt", "a") as text_file:
        with ThreadPoolExecutor() as executor:
            for i in range(0, number_of_requests_rounds):
                start_time = time.time()
                for i in range(0, number_of_requests):
                    futures.append(
                        executor.submit(request_backend, backend_ip, backend_port, workflow_file, input_file))

                for future in as_completed(futures):
                    try:
                        if not future.result():
                            text_file.write("After {] requests, no valid output \n".format(number_of_requests))
                            break

                    except Exception as exc:
                        print(exc)
                        break

                response_time = time.time() - start_time
                text_file.write(
                    "{} number of requests ---> {}s response time \n".format(number_of_requests, response_time))

                x_axis_requests.append(number_of_requests)
                y_axis_response_time.append(response_time)
                number_of_requests *= factor
                time.sleep(interval)

    return x_axis_requests, y_axis_response_time



if __name__ == '__main__':
    concurrent_reqs = True
    # Starting with 1 request, each group of requests gets increased by specified factor
    number_of_requests_rounds = 3
    factor = 2
    interval = 2

    # set ip and port of backend (monolithic)
    backend_ip_mono = "52.224.248.96"
    backend_port_mono = "3001"

    #set ip and port of backend (microservice)
    backend_ip_micro = "52.224.197.60"
    backend_port_micro = "3001"



    # clear log file
    open('logs.txt', 'w').close()

    if concurrent_reqs:
        graph_tuple_mono = concurrent_requests(number_of_requests_rounds, factor, interval, backend_ip_mono, backend_port_mono)
        graph_tuple_micro = concurrent_requests(number_of_requests_rounds, factor, interval, backend_ip_micro, backend_port_micro)
        plot_multi_graph(graph_tuple_mono[0], graph_tuple_mono[1], graph_tuple_micro[0], graph_tuple_micro[1])
    else:
        # load input
        workflow_file = os.path.join(PLANNING_INPUT, "compile1.cwl")
        input_file = os.path.join(PLANNING_INPUT, "input_pcp.yaml")


        # number of requests to the power of 2 starting with 1 request, e.g. setting it to 4 results in 1, 2, 4, 16
        number_of_requests = 5
        # change this if you want to raise to a different power
        power = 2
        # dont change this variable
        res = 2

        with open("logs.txt", "a") as text_file:
            for i in range(0, number_of_requests):
                start = time.time()
                if i == 0:
                    if not request_backend(backend_ip, backend_port, workflow_file, input_file):
                        text_file.write(
                            "After 1 request, no valid output ---> {}s response time \n".format(response_time))
                        break


                elif i == 1:
                    resp = request_backend(backend_ip, backend_port, workflow_file, input_file)
                    resp2 = request_backend(backend_ip, backend_port, workflow_file, input_file)
                    if not resp and resp2:
                        text_file.write(
                            "After 2 requests, no valid output ---> {}s response time \n".format(response_time))
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
