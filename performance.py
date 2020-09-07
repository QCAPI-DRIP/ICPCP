from definitions import PLANNING_INPUT
import os
import requests
import time
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import matplotlib.pyplot as plt
import math
from definitions import EXPERIMENT_LOGS
import csv
import numpy


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
    plt.ylabel('Standard deviation')

    # giving a title to my graph
    plt.title('Performance study')

    # show a legend on the plot
    plt.legend()

    # # function to show the plot
    # plt.show()
    plt.savefig(os.path.join(EXPERIMENT_LOGS, "deviation_2replicas1node"))

def plot_multi_graph(x1, y1, x2, y2):
    plt.figure(1)
    plt.plot(x1, y1, label="monolithic")

    plt.plot(x2, y2, label="microservices")

    # naming the x axis
    plt.xlabel('number of requests')
    # naming the y axis
    plt.ylabel('response time (s)')
    # giving a title to my graph
    plt.title('Average performance, avg=10')

    # show a legend on the plot
    plt.legend()
    #
    # # function to show the plot
    # plt.show()

    plt.savefig(os.path.join(EXPERIMENT_LOGS, "performance_2replicas1node"))


def plot_multi_graph_dev(x1, y1, x2, y2):
    plt.figure(2)
    plt.plot(x1, y1, label="monolithic")

    plt.plot(x2, y2, label="microservices")

    # naming the x axis
    plt.xlabel('number of requests')
    # naming the y axis
    plt.ylabel('Standard deviation')
    # giving a title to my graph
    plt.title('Standard deviation, data=10')

    # show a legend on the plot
    plt.legend()
    #
    # # function to show the plot
    # plt.show()

    plt.savefig(os.path.join(EXPERIMENT_LOGS, "deviation_2replicas1node"))

session_results_mono = {}
session_results_micro = {}

def concurrent_requests(number_of_requests_rounds, factor, interval, backend_ip, backend_port, architecture_type):
    global session_results_mono
    global session_results_micro

    # load input
    workflow_file = os.path.join(PLANNING_INPUT, "compile1.cwl")
    input_file = os.path.join(PLANNING_INPUT, "input_pcp.yaml")

    # number of requests is key, value is list of response times
    x_axis_requests = []
    y_axis_response_time = []
    x_y_combined = []
    # We can use a with statement to ensure threads are cleaned up promptly
    futures = []
    number_of_requests = 1

    with open(os.path.join(EXPERIMENT_LOGS, '{}2replicas1node.csv'.format(architecture_type)), 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Number of requests", "Response time (s)"])

        for i in range(0, number_of_requests_rounds):
            # count = 0
            start_time = time.time()
            with ThreadPoolExecutor() as executor:
                for i in range(0, number_of_requests):
                        futures.append(
                            executor.submit(request_backend, backend_ip, backend_port, workflow_file, input_file))

                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if not result:
                            writer.writerow([number_of_requests, "Invalid output"])
                            print("After {} requests, no valid output \n".format(number_of_requests))
                            return False
                        # if result:
                        #     count +=1

                    except Exception as exc:
                        print(exc)
                        return False


                futures.clear()
                # print(count)
                response_time = time.time() - start_time


            #log results
            writer.writerow([number_of_requests, response_time])

            if architecture_type == "mono":
                if number_of_requests in session_results_mono:
                    dict_value = session_results_mono[number_of_requests]
                    dict_value.append(response_time)
                    session_results_mono[number_of_requests] = dict_value

                else:
                    session_results_mono[number_of_requests] = [response_time]

            else:
                if number_of_requests in session_results_micro:
                    dict_value = session_results_micro[number_of_requests]
                    dict_value.append(response_time)
                    session_results_micro[number_of_requests] = dict_value

                else:
                    session_results_micro[number_of_requests] = [response_time]

            x_axis_requests.append(number_of_requests)
            y_axis_response_time.append(response_time)
            number_of_requests *= factor
            time.sleep(interval)

    return x_axis_requests, y_axis_response_time

def send_single_request():
    # load input
    workflow_file = os.path.join(PLANNING_INPUT, "compile1.cwl")
    input_file = os.path.join(PLANNING_INPUT, "input_pcp.yaml")
    endpoint = "52.224.202.237"
    port = 3001

    request_url = "http://{endpoint}:{port}/upload".format(endpoint=endpoint, port=port)
    files = {'workflow_file': open(workflow_file, 'rb'), 'input_file': open(input_file, 'rb')}

    resp = requests.post(request_url, files=files)
    # empty response
    if not resp.text:
        print("empty response file")
        return False

    print(resp.text)
    return True

if __name__ == '__main__':
    #send_single_request()
    concurrent_reqs = True
    print_graph = False
    # Starting with 1 request, each group of requests gets increased by specified factor
    number_of_requests_rounds = 2
    factor = 2
    interval = 2

    #how many time do we execute the same experiment
    number_of_experiment_rounds = 2
    # set ip and port of backend (monolithic)
    backend_ip_mono = "52.224.205.134"
    backend_port_mono = "3001"

    #set ip and port of backend (microservice)
    backend_ip_micro = "52.224.202.237"
    backend_port_micro = "3001"

    log_file_loc_mono = os.path.join(EXPERIMENT_LOGS, "{}.txt".format("mono"))
    log_file_loc_micro = os.path.join(EXPERIMENT_LOGS, "{}.txt".format("micro"))

    # # clear log files
    # open(log_file_loc_mono, 'w').close()
    # open(log_file_loc_micro, 'w').close()

    if concurrent_reqs:
        for _ in range(0, number_of_experiment_rounds):
            if print_graph:
                graph_tuple_mono = concurrent_requests(number_of_requests_rounds, factor, interval, backend_ip_mono, backend_port_mono, "mono")
                graph_tuple_micro = concurrent_requests(number_of_requests_rounds, factor, interval, backend_ip_micro, backend_port_micro, "micro")
                if graph_tuple_mono and graph_tuple_micro:
                    plot_multi_graph(graph_tuple_mono[0], graph_tuple_mono[1], graph_tuple_micro[0], graph_tuple_micro[1])

            else:
                concurrent_requests(number_of_requests_rounds, factor, interval, backend_ip_mono, backend_port_mono, "mono")
                concurrent_requests(number_of_requests_rounds, factor, interval, backend_ip_micro, backend_port_micro, "micro")


        #do computations
        number_of_requests_x_axis_mono = []
        avg_performance_time_y_axis_mono = []
        deviation_mono = []

        number_of_requests_x_axis_micro = []
        avg_performance_time_y_axis_micro = []
        deviation_micro = []

        with open(os.path.join(EXPERIMENT_LOGS, 'mono_avg_2replicas1node.csv'), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Number of requests", "Average response time (s)", "Standard deviation"])

            for key, value in session_results_mono.items():
                number_of_requests_x_axis_mono.append(key)
                mean = numpy.mean(value)
                deviation = numpy.std(value)
                avg_performance_time_y_axis_mono.append(mean)
                deviation_mono.append(deviation)
                writer.writerow([key, mean, deviation])

        with open(os.path.join(EXPERIMENT_LOGS, 'micro_avg_2replicas1node.csv'), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Number of requests", "Average response time (s), Standard deviation"])

            for key, value in session_results_micro.items():
                number_of_requests_x_axis_micro.append(key)
                mean = numpy.mean(value)
                deviation = numpy.std(value)
                avg_performance_time_y_axis_micro.append(mean)
                deviation_micro.append(deviation)
                writer.writerow([key, mean, deviation])

        plot_multi_graph(number_of_requests_x_axis_mono, avg_performance_time_y_axis_mono, number_of_requests_x_axis_micro, avg_performance_time_y_axis_micro)
        plot_multi_graph_dev(number_of_requests_x_axis_mono, deviation_mono, number_of_requests_x_axis_micro, deviation_micro)


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
