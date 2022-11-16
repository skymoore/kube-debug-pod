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
  -n, --namespace TEXT  Namespace to start pod in, default: default.
  -c, --command TEXT    Command to run in container, default: /bin/bash.
  -p, --pod-name TEXT   The name for the debug pod, default: kdb.
  -v, --version         Display version info and exit.
  -a, --arch-linux      Use archlinux:latest image.
  -s, --sky-tools       Use skymoore/tools:latest image.
  -i, --image TEXT      Image for debug container, default: debian:latest.
  --help                Show this message and exit.

Constraints:
  {--arch-linux, --sky-tools, --image}
    mutually exclusive               Show this message and exit.
```

## Example Usage:
```bash
kdb -n myapp
```