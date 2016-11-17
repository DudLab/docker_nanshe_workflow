[![CircleCI](https://circleci.com/gh/nanshe-org/docker_nanshe_workflow/tree/master.svg?style=shield)](https://circleci.com/gh/nanshe-org/docker_nanshe_workflow/tree/master)

# Purpose

To provide a simple and easy to use container with the `nanshe_workflow` and all dependencies preinstalled and ready to use, which can act as a miniature cluster and can work on any machine.

# Building

## Automatic

This repo is part of an automated build, which is hosted on Docker Hub ( <https://hub.docker.com/r/nanshe/nanshe_workflow> ). Changes added to this trigger an automatic rebuild that deploys the resulting image to Docker Hub. To download an existing image, one simply needs to run `docker pull nanshe/nanshe_workflow`. Currently, this is a private repo on Docker Hub. So, to get access one must contact @jakirkham about access.

## Manual

If one wishes to develop this repo, building will need to be performed manually. This container can be built simply by `cd`ing into the repo and using `docker build -t <NAME> .`; where, `<NAME>` is the name tagged to the image built. More information about building can be found in Docker's documentation ( <https://docs.docker.com/reference/builder> ). Please consider opening a pull request for changes that you make.

# Testing

The `nanshe_workflow` is tested independently of this container. The base container used by this container's base, `nanshe/nanshe`, is composed of tested `nanshe` releases and a base image `jakirkham/centos_drmaa_conda`. Both of which are tested independently. That being said, when this container is built the test suite is run. As a result, if it fails the test suite, the container build will fail meaning it won't be tagged or released on Docker Hub.

# Usage

Once an image is acquired either from one of the provided builds or manually, the image is designed to setup all necessary services (Grid Engine) and provide an iPython notebook ready to use. In the case of an automated build, `<NAME>` is `nanshe/nanshe_workflow`.

## Standard use

Python scripts have been written to simplify the setup, teardown, and manage the `boot2docker` VM and the container. This has been done with eye towards transparency and simplicity. To get started, one can simply use the `startup-nanshe-workflow` command provided in the repo. This uses Python and thus will work on any system where Python is installed.

### Install

For convenience, not required, one can install this command into their Python distribution by using the `setup.py` file included. For this to work, one **must** have [`setuptools`]( https://setuptools.readthedocs.io/en/latest/ ) and [`pip`]( https://pip.pypa.io/en/stable/ ) installed in their Python distribution. Additionally, the install does not follow standard Python installs. To install, run `pip install -e .`. This will install a copy of the executable in the Python path so it can be used anywhere.

### Loading data

As the primary goal of this is to analyze data, it is incredibly important to have a simple mechanism to do so and to understand how it works. In order to mount data, simply use the option `-d` or `--directory`, which may be followed by a directory to mount. If a directory is not specified, the current working directory is assumed. When mounting a data directory, the workflows will be installed into the directory if they are not found. Any workflows found in the data directory will be left intact. Once iPython loads, the data directory will be used as the notebook directory. This means the workflows and data will be available to you in the same directory. All changes made to these workflows will appear in the data directory. When quitting the notebook, these changes will persist allowing the user to resume from some previous state the workflow had.

### Updating

Periodically, updates will be made to this repo and the related Docker image. New copies of the image can be retrieved from Docker Hub and the git repo can be updated. To make this process simpler, passing the option `-u` or `--update` to `startup-nanshe-workflow` will make the git repo current with `master`. **Note:** If the repo and submodule are not clean or cannot be fast-forwarded, this will fail. Also, it will attempt to pull the latest image, which will be the same as the current repo. If the image cannot be pulled (e.g. not logged into Docker Hub, Internet issue), it will build the image locally.

### Skip VM shutdown

The `boot2docker` virtual machine is started and shutdown each time by default. It is also initialized with default arguments the first time. Though the VM is quite light, it still takes some time to perform this startup and shutdown. It may be preferable to keep the VM up after a run. This can be done by providing the `-s` or `--no-shutdown` argument to `startup-nanshe-workflow`.

### Persisting

If one wishes to keep a container after running is completed, this can be done using `-p` or `--persist` options with `startup-nanshe-workflow`.

## Development/Advanced use

### Mounting development workflow

Results in the container are not persisted after it is shutdown. If one wishes, to keep the notebook after a run simply use `-w` or `--mount-workflow` with `startup-nanshe-workflow`. This will make sure the git submodule included in this repo `nanshe_workflow` is inserted in the container. All changes will be saved to that repo after it closes.

### Building

In development, one may wish to build an image. This can be done by passing the `-b` or `--build` option `startup-nanshe-workflow`. These can be combined with an update to ensure the update is built locally, as well. If nothing has changed since the last build, this will be a no-op that reuse cached layers.

### Docker/iPython options

In the event that there is some desired functionality not handled by the previous options, Any option that one would want to pass to `docker run` or `ipython notebook` still can. The only requirements are the following docker options come after options to `startup-nanshe-workflow` and the block of docker options must begin with the `docker` option. Similarly, the ipython option block must follow the docker option block (if there is one) and must begin with the `ipython` option. This helps avoid option clashes and also makes it clear to other users where the options are intended to go.

### Docker relative paths (Volumes/Workdir)

Path options to `docker run` like volume options (`-v` and `--volume`) and workdir options (`-w` and `--workdir`) normally are required to be absolute paths by `docker run`. However, `startup-nanshe-workflow` will accept relative paths process them to produce absolute paths before passing them to `docker run`. This helps keep commands concise and allow the user to specify the current directory or similar concisely. **Note:** Setting the workdir will not change the current working directory used by iPython notebooks. **Additional Note:** If the workdir is set, this will be used to fix all relative machines on the remote regardless of the order it appears in the argument list.

### Uninstall

This is only needed if one has run the installation step above and wishes to uninstall. To do this, run `pip uninstall startup-nanshe-workflow`. Then feel free to remove the `docker_nanshe_workflow` directory.

## Docker usage

If one does not wish to use the python scripts presented above. They can use docker directly. The typical use case will be to run `docker run --rm -it -p <HOST port>:<CONTAINER port> <NAME>`. In this case, `<CONTAINER port>` is `8888`. As for `<HOST port>`, it can be anything that you want. However, if you are using Boot2Docker, it is the `<VM port>`. Typically, this should just be set to `80` meaning it won't need to be specified in the URL. In which case, on a machine with docker, the container will provide access to iPython through <http://localhost>. With `boot2docker`, a different IP address will be required, which can be determined by running `boot2docker ip`.

### Persist container

If one wishes the container to persist after it is terminated, drop `--rm` from the `docker run` command.

### Daemon mode

One can run the container in daemon mode, which captures all output and returns one to the command prompt immediately after issuing `docker run`. To do this, simply replace `--rm -it` with `-d` in the `docker run` command. This will write a `<CONTAINER ID>` to `stdout` (i.e. the terminal). To see the output from the container (including iPython), run `docker logs <CONTAINER ID>`. Once the user is done with the container, they are responsible for cleaning it up. To terminate the container, use `docker stop <CONTAINER ID>`. To delete the container, use `docker rm <CONTAINER ID>`.

### Mounting data

To provide data within the container, simply use `-v <HOST dir>:<Docker dir>` with `docker run`; where, `<HOST dir>` is the absolute path to data on your computer and `<Docker dir>` is the absolute path to where the data will be available for iPython. For simplicity, this can be set to `/mnt/data`, but anything under `/mnt` should be fine. To export data, also place it in this mounted directory.

### Boot2Docker - Port Mapping

If one is using [boot2docker]( http://boot2docker.io/ ), required by Mac and Windows, port forwarding can be used to map VM ports to the host machine. This can be done by running `boot2docker ssh -vnNTL <HOST port>:localhost:<VM port>` in a terminal while using the container. Alternatively, this can be setup permanently by running `VBoxManage controlvm "boot2docker-vm" natpf1 "ipython-port,tcp,,<HOST port>,,<VM port>"` when `boot2docker` is already up. If `boot2docker` is down, simply replace `controlvm` with `modifyvm`. For simplicity, the `<VM port>` can just be set to `8888`. The host can also be set to `8888` if it is not in use; otherwise another port should be used. If the port mapping needs to be deleted, simply run `VBoxManage modifyvm "boot2docker-vm" natpf1 delete "ipython-port"`.

## Managing Containers

Every time `docker run` is issued this creates a container. It is important to stop containers when one is done using them. To do this, run `docker stop <CONTAINER ID>`. To terminate this session simply run `docker stop <CONTAINER ID>`. To remove this container completely, run `docker rm <CONTAINER ID>`. Running `docker ps` displays a list of all active containers. To see all containers, including inactive ones, run `docker ps -a`.
