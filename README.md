# kube-debug-pod

## CLI for easy kube debug pod

## Usage:
```bash
Usage: kdb [OPTIONS]

Options:
  -n, --namespace TEXT  Namespace to start pod in, default: default.
  -i, --image TEXT      Image for debug container, default: debian:latest.
  -c, --command TEXT    Command to run in container, default: /bin/bash.
  -p, --pod-name TEXT   The name for the debug pod, default: kdb.
  -v, --version         Display version info and exit.
  -a, --arch-linux      Use archlinux:latest image.
  --help                Show this message and exit.
```