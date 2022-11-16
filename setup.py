#!/usr/bin/env python3

from setuptools import find_packages, setup
from kube_debug_pod import _version

with open("./README.md") as readme_file:
    readme = readme_file.read()

with open("./requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    author="Sky Moore",
    author_email="i@msky.me",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    description="CLI to easily create k8s debug pod.",
    include_package_data=True,
    install_requires=requirements,
    keywords=["k8s", "debug"],
    license="MIT",
    long_description_content_type="text/markdown",
    long_description=readme,
    name="kube-debug-pod",
    packages=find_packages(include=["kube_debug_pod"]),
    entry_points={
        "console_scripts": ["kdb = kube_debug_pod.__main__:kdb"],
    },
    url="https://github.com/skymoore/kube-debug-pod",
    version=_version,
    zip_safe=True,
)
