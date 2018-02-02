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
elif [ "$(cd "$1" && pwd)" == "$(cd "$2" && pwd)" ];
then
    echo "Skipping copying workflows as source and destination are the same."
    exit 0
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


echo "Copying workflows from source to destination..."
for each_workflow in $(find "$1" -name "*.ipynb");
do
    each_workflow="$(basename "$each_workflow")"
    if [[ -e "$2/$each_workflow" ]];
    then
        echo "    Skipped: "$each_workflow""
    else
        cp "$1/$each_workflow" "$2"
        echo "    Copied:  "$each_workflow""
    fi
done
echo "Completed copying of workflows."
