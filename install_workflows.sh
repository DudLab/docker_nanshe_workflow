#!/bin/bash


EXIT=0
HELP=false


if [ "$1" == "-h" ] || [ "$1" == "--help" ];
then
    HELP=true
elif [ $# -ne 2 ];
then
    echo "Requires exactly two parameters."
    HELP=true
    EXIT=64
fi

if [ $HELP = true ];
then
    echo "$(basename "$0") [-h] [DIR DIR]-- copy workflows between directories

where:
    -h   show this help text
    DIR  directory to get workflows from.
    DIR  directory to install workflows to."
    exit $EXIT
fi


for each_workflow in $(find "$1" -name "*.ipynb");
do
    cp -n "$each_workflow" "$2"
done
