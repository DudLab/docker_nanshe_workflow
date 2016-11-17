#!/bin/bash


# Make sure repo is clean.
git update-index -q --refresh


exec "$@"
