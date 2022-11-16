from click import STRING
from cloup import command, option
from subprocess import call
from cloup.constraints import mutually_exclusive
from . import _version

default_namespace = "default"
default_image = "debian:latest"
default_command = "/bin/bash"
default_pod_name = "kdb"
arch_linux_image = "archlinux:latest"
sky_tools_image = "skymoore/tools:latest"


@command(show_constraints=True)
@option(
    "-n",
    "--namespace",
    default=default_namespace,
    type=STRING,
    help=f"Namespace to start pod in, default: {default_namespace}.",
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
@mutually_exclusive(
    option("-a", "--arch-linux", is_flag=True, help=f"Use {arch_linux_image} image."),
    option("-s", "--sky-tools", is_flag=True, help=f"Use {sky_tools_image} image."),
    option(
        "-i",
        "--image",
        type=STRING,
        help=f"Image for debug container, default: {default_image}.",
    ),
)
def kdb(
    namespace: str,
    command: str,
    image: str,
    pod_name: str,
    version: bool,
    arch_linux: bool,
    sky_tools: bool,
):

    if version:
        print(f"kube-debug-pod v{_version}")
        exit(0)

    # set image
    if arch_linux:
        image = arch_linux_image

    if sky_tools:
        image = sky_tools_image

    if image is None:
        image = default_image

    print(f"Image: {image}")

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

    # delete pod
    return_code = call(f"kubectl delete pod {pod_name} -n {namespace}", shell=True)
    if return_code != 0:
        print(f"failed to delete pod {pod_name} in {namespace} namespace")
        exit(return_code)

    exit(0)
