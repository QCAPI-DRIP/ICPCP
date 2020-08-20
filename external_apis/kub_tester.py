# from kubernetes.client import client, config
import kubernetes.config as config
import kubernetes.client as client
from os import path
import yaml
import requests

config.load_kube_config()

def list_pods():
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))


def create_deployment():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_kube_config()
    #
    # with open(path.join(path.dirname(__file__), "deployment_parser.yaml")) as f:
    #     dep = yaml.safe_load(f)
    #     k8s_apps_v1 = client.AppsV1Api()
    #     resp = k8s_apps_v1.create_namespaced_deployment(
    #         body=dep, namespace="default")
    #     print("Deployment created. status='%s'" % resp.metadata.name)
    #
    # with open(path.join(path.dirname(__file__), "deployment_planner.yaml")) as f:
    #     dep = yaml.safe_load(f)
    #     k8s_apps_v1 = client.AppsV1Api()
    #     resp = k8s_apps_v1.create_namespaced_deployment(
    #         body=dep, namespace="default")
    #     print("Deployment created. status='%s'" % resp.metadata.name)

    core_v1_api = client.CoreV1Api()
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)
    with open(path.join(path.dirname(__file__), "service_parser.yaml")) as f:
        body = yaml.safe_load(f)
        resp = core_v1_api.create_namespaced_service(namespace="default", body=body)
        print("Service created. status='%s'" % resp.metadata.name)

    with open(path.join(path.dirname(__file__), "service_planner.yaml")) as f:
        body = yaml.safe_load(f)
        resp = core_v1_api.create_namespaced_service(namespace="default", body=body)
        print("Service created. status='%s'" % resp.metadata.name)


if __name__ == '__main__':
    requests.get("http://localhost:5001")
    # create_deployment()
    # list_pods()