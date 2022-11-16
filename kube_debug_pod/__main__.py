from click import STRING
from cloup import command, option
from cloup.constraints import mutually_exclusive
from subprocess import call, Popen, PIPE
from time import sleep
from . import _version
from json import dumps

default_namespace = "default"
default_image = "debian:latest"
default_command = "/bin/bash"
default_pod_name = "kdb"
default_timeout = "60s"
arch_linux_image = "archlinux:latest"
sky_tools_image = "skymoore/tools:latest"


@command(show_constraints=True)
@option(
    "-n",
    "--namespace",
    default=default_namespace,
    type=STRING,
    help=f"Namespace to start pod in, created if does not exist, default: {default_namespace}.",
)
@option(
    "-c",
    "--command",
    default=default_command,
    type=STRING,
    help=f"Command to run in container, default: {default_command}.",
)
@option(
    "-m",
    "--pod-name",
    default=default_pod_name,
    type=STRING,
    help=f"The name for the debug pod, default: {default_pod_name}.",
)
@option(
    "-t",
    "--timeout",
    type=STRING,
    default=default_timeout,
    help=f"Time to wait for pod to be ready, default: 60s.",
)
@option(
    "-p",
    "--port-forward",
    type=STRING,
    help=f"Forward a port to the container, like 8000:8000.",
)
@option(
    "--pvc",
    multiple=True,
    help="PVCs to attach to mount in the container at /opt/pvc-name.",
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
    timeout: str,
    port_forward: str,
    pvc: list,
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

    print(f"image: {image}")

    # namespace
    namespace_created = False
    print(f"checking for namespace {namespace}...")
    ns_proc = Popen(
        [
            "kubectl",
            "get",
            "ns",
            namespace,
        ],
        stdin=PIPE,
        stderr=PIPE,
        stdout=PIPE,
    )

    while ns_proc.poll() is None:
        sleep(1)

    if ns_proc.poll() != 0:
        return_code = call(
            f"kubectl create ns {namespace}",
            shell=True,
        )
        namespace_created = True

        if return_code != 0:
            print(f"failed to create namespace {namespace}")
            exit(return_code)

    # volumes
    overrides = ""
    if pvc is not None:
        overrides_json = {
            "apiVersion": "v1",
            "kind": "Pod",
            "spec": {
                "containers": [
                    {
                        "name": pod_name,
                        "image": image,
                        "imagePullPolicy": "Always",
                        "command": [
                            "/bin/sh",
                            "-c",
                            'sh -c "while true; do sleep 30;done;"',
                        ],
                        "volumeMounts": [
                            {"mountPath": f"/opt/{v}", "name": v} for v in pvc
                        ],
                    }
                ],
                "tolerations": [
                    {
                        "key": "dedicated",
                        "operator": "Equal",
                        "value": "",
                        "effect": "NoSchedule",
                    },
                    {
                        "key": "dedicated",
                        "operator": "Equal",
                        "value": "",
                        "effect": "NoExecute",
                    },
                ],
                "nodeSelector": {"nodename": "monitoring"},
                "volumes": [
                    {"name": v, "persistentVolumeClaim": {"claimName": v}} for v in pvc
                ],
            },
        }
        overrides = f" --overrides='{dumps(overrides_json)}' --override-type=strategic "

    # create the pod
    return_code = call(
        f'kubectl run {pod_name} --image={image} --restart=Never{overrides} -n {namespace} --command -- /bin/sh -c -- "while true; do sleep 30; done;"',
        shell=True,
    )
    if return_code != 0:
        print(f"failed to start pod {pod_name} in {namespace} namespace")
        exit(return_code)

    # wait for pod to be ready
    print(f"waiting {timeout} for pod/{pod_name} to be ready...")
    return_code = call(
        f"kubectl wait --timeout={timeout} --for=condition=Ready pod/{pod_name} -n {namespace}",
        shell=True,
    )

    if return_code != 0:
        print(f"failed waiting for pod {pod_name} in {namespace} namespace to be ready")
        exit(return_code)

    if port_forward is not None:
        print(
            f"forwarding port {port_forward} to pod/{pod_name} in {namespace} namespace"
        )
        port_forward_proc = Popen(
            [
                "kubectl",
                "port-forward",
                pod_name,
                port_forward,
                "-n",
                namespace,
            ],
            stdin=PIPE,
            stderr=PIPE,
            stdout=PIPE,
        )

    # attach to container
    return_code = call(
        f"kubectl exec -t -i {pod_name} -c {pod_name} -n {namespace} -- {command}",
        shell=True,
    )

    if port_forward is not None and port_forward_proc.poll() is None:
        print("terminating port forward")
        port_forward_proc.terminate()

    # cleanup
    return_code = call(f"kubectl delete pod {pod_name} -n {namespace}", shell=True)
    if return_code != 0:
        print(f"failed to delete pod {pod_name} in {namespace} namespace")
        exit(return_code)

    if namespace_created:
        return_code = call(f"kubectl delete ns {namespace}", shell=True)
        if return_code != 0:
            print(f"failed to delete namespace {namespace}")
            exit(return_code)

    exit(0)
