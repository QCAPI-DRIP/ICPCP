from kubernetes import client, config
import os
from definitions import K8_CONFIG_PATH
# KUBE_CONFIG__LOCATION = os.path.join(os.getcwd(), 'config', 'config')
config.load_kube_config(K8_CONFIG_PATH)

def create_deployment(name, image_repo, container_port):
    # Fetching and loading local Kubernetes Information
    apps_v1_api = client.AppsV1Api()

    # Configureate Pod template container
    container = client.V1Container(
        name=name,
        image=image_repo,
        ports=[client.V1ContainerPort(container_port=container_port)],
        # resources=client.V1ResourceRequirements(
        #     requests={"cpu": "100m", "memory": "200Mi"},
        #     limits={"cpu": "500m", "memory": "500Mi"}
        # )
    )
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": name}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.V1DeploymentSpec(
        replicas=3,
        template=template,
        selector={'matchLabels': {'app': name}})
    # Instantiate the deployment object
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=name),
        spec=spec)

    apps_v1_api.create_namespaced_deployment(
            namespace="default", body=deployment
        )

def create_service(name, container_port):
    core_v1_api = client.CoreV1Api()
    body = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name="service-{}".format(name)
        ),
        spec=client.V1ServiceSpec(
            selector={"app": name},
            ports=[client.V1ServicePort(
                port=3001,
                target_port=container_port
            )],
            type="LoadBalancer"
        )
    )
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)
    data = core_v1_api.create_namespaced_service(namespace="default", body=body)
    cluster_ip = data.spec.cluster_ip
    return cluster_ip

def list_pods():
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

def main():
    create_service("test", 5000)
    list_pods()

if __name__ == "__main__":
    # KUBE_CONFIG__LOCATION = os.path.join(os.getcwd(), 'config', 'config')
    # print(KUBE_CONFIG__LOCATION)
    list_pods()
    #main()