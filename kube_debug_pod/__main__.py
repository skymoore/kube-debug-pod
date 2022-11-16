from click import command, option, STRING
from subprocess import call
from . import _version

default_namespace = "default"
default_image = "debian:latest"
default_command = "/bin/bash"
default_pod_name = "kdb"


@command()
@option(
    "-n",
    "--namespace",
    default=default_namespace,
    type=STRING,
    help=f"Namespace to start pod in, default: {default_namespace}.",
)
@option(
    "-i",
    "--image",
    default=default_image,
    type=STRING,
    help=f"Image for debug container, default: {default_image}.",
)
@option(
    "-c",
    "--command",
    default=default_command,
    type=STRING,
    help=f"Command to run in container, default: {default_command}.",
)
@option(
    "-p",
    "--pod-name",
    default=default_pod_name,
    type=STRING,
    help=f"The name for the debug pod, default: {default_pod_name}.",
)
@option("-v", "--version", is_flag=True, help="Display version info and exit.")
@option("-a", "--arch-linux", is_flag=True, help="Use archlinux:latest image.")
def kdb(
    namespace: str,
    command: str,
    image: str,
    pod_name: str,
    version: bool,
    arch_linux: bool,
):

    if version:
        print(f"kube-debug-pod {_version}")
        exit(0)

    if arch_linux:
        image = "archlinux:latest"

    # create the pod
    return_code = call(
        f'kubectl run {pod_name} --image={image} --restart=Never -n {namespace} --command -- /bin/sh -c -- "while true; do sleep 30; done;"',
        shell=True,
    )
    if return_code != 0:
        print(f"failed to start pod {pod_name} in {namespace} namespace")
        exit(return_code)

    # wait for pod to be ready
    print(f"waiting for pod/{pod_name} to be ready...")
    return_code = call(
        f"kubectl wait --for=condition=Ready pod/{pod_name} -n {namespace}", shell=True
    )

    if return_code != 0:
        print(f"failed waiting for pod {pod_name} in {namespace} namespace to be ready")
        exit(return_code)

    # attach to container
    return_code = call(
        f"kubectl exec -t -i {pod_name} -c {pod_name} -n {namespace} -- {command}",
        shell=True,
    )

    if return_code not in [1, 0]:
        print(f"failed to attach to pod {pod_name} in {namespace} namespace")
        exit(return_code)

    # delete pod
    return_code = call(f"kubectl delete pod {pod_name} -n {namespace}", shell=True)
    if return_code != 0:
        print(f"failed to delete pod {pod_name} in {namespace} namespace")
        exit(return_code)

    exit(0)
