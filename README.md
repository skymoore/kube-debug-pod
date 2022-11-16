# kube-debug-pod

## CLI for easy kube debug pod

## Install:
```bash
python -m pip install kube-debug-pod
```
## Usage:
```bash
kdb [OPTIONS]

Options:
  -n, --namespace TEXT     Namespace to start pod in, default: default.
  -c, --command TEXT       Command to run in container, default: /bin/bash.
  -m, --pod-name TEXT      The name for the debug pod, default: kdb.
  -t, --timeout TEXT       Time to wait for pod to be ready, default: 60s.
  -p, --port-forward TEXT  Forward a port to the container, like 8000:8000.
  -v, --version            Display version info and exit.
  -a, --arch-linux         Use archlinux:latest image.
  -s, --sky-tools          Use skymoore/tools:latest image.
  -i, --image TEXT         Image for debug container, default: debian:latest.
  --help                   Show this message and exit.

Constraints:
  {--arch-linux, --sky-tools, --image}
    mutually exclusive
```

### Example Usage 1:
```bash
kdb -s -n myns -p 8000:8000 -m mypod
```

### Example Usage 2:
```bash
kdb -n myns
```

### Example Usage 3:
```bash
kdb
```