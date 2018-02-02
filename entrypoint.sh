#!/bin/bash


# Make sure repo is clean.
git update-index -q --refresh

# Install the workflows into the current working directory.
/usr/share/docker/install_workflows.sh /nanshe_workflow "$(pwd)"


exec "$@"
