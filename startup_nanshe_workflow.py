__author__ = "John Kirkham <kirkhamj@janelia.hhmi.org>"
__date__ = "$Jul 31, 2015 18:00:05 EDT$"


import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
import threading
import webbrowser


if sys.version_info.major == 2:
    from urllib2 import urlopen, URLError
elif sys.version_info.major >= 3:
    from urllib.request import urlopen
    from urllib.error import URLError

    xrange = range


has_boot2docker = False
with open(os.devnull, "wb") as devnull:
    try:
        has_boot2docker = (
            0 == subprocess.check_call(
                ["boot2docker", "version"], stdout=devnull, stderr=devnull
            )
        )
    except:
        pass


has_docker_machine = False
with open(os.devnull, "wb") as devnull:
    try:
        has_docker_machine = (
            0 == subprocess.check_call(
                ["docker-machine", "--version"], stdout=devnull, stderr=devnull
            )
        )
    except:
        pass


assert has_docker_machine or has_boot2docker, "In order to use this script, " \
                        "you must have docker-machine installed. Visit here " \
                        "( https://www.docker.com/docker-toolbox ) for " \
                        "details on how to do this."


class Docker(object):
    def __init__(self):
        pass

    def __enter__(self):
        """
            Start up the VM, creating it if it doesn't exist.
        """

        return(self)

    def __exit__(self, type, value, traceback):
        """
            Shutdown the VM.
        """

        pass

    def shellinit(self):
        """
            Set environment variables.
        """

        pass

    @property
    def ip(self):
        """
            Get the VM's IP address.

            Returns:
                (str):              The IP Address of the VM.
        """

        vm_ip = "127.0.0.1"

        return(vm_ip)

    @property
    def images(self):
        """
            Get a list of the images.

            Returns:
                (dict of lists):    A dictionary keyed by the field name and a
                                    list of the values for each image.
        """

        images_list = subprocess.check_output(["docker", "images"]).strip()
        images_list = [
            re.sub(b"\s\s+", b"\n", _).splitlines()
            for _ in images_list.splitlines()
        ]

        if sys.version_info.major >= 3:
            images_list = [
                [__.decode("utf-8") for __ in _] for _ in images_list
            ]

        images_dict = dict()
        for each_key in images_list[0]:
            images_dict[each_key] = list()

        for i in xrange(1, len(images_list)):
            for j, each_key in enumerate(images_list[0]):
                images_dict[each_key].append(images_list[i][j])

        return(images_dict)

    def pull(self, image):
        """
            Pull an image from DockerHub.
        """

        image_old = image.split(":")
        image_old[0] += "_old"
        image_old = ":".join(image_old)

        try:
            subprocess.call(["docker", "tag", "-f", image, image_old])
            subprocess.check_call(["docker", "pull", image])
        finally:
            subprocess.call(["docker", "rmi", image_old])

    def build(self, image, path):
        """
            Build and tag an image.
        """

        image_old = image.split(":")
        image_old[0] += "_old"
        image_old = ":".join(image_old)

        try:
            subprocess.call(["docker", "tag", "-f", image, image_old])
            subprocess.check_call([
                "docker", "build", "--rm", "-t", image, path
            ])
        finally:
            subprocess.call(["docker", "rmi", image_old])


class Boot2Docker(Docker):
    def __init__(self, shutdown=True):
        """
            Creates/recreate the VM if it doesn't exist or settings are off.
        """

        super(Boot2Docker, self).__init__()
        self.shutdown = shutdown

        dev_dir = os.path.dirname(os.path.abspath(__file__))
        dev_boot2docker_profile = os.path.join(dev_dir, ".boot2docker_profile")

        user_home_dir = os.path.expanduser('~')
        boot2docker_dir = os.path.join(user_home_dir, ".boot2docker")
        boot2docker_profile = os.path.join(boot2docker_dir, "profile")

        if not os.path.exists(boot2docker_profile):
            try:
                subprocess.check_call(["boot2docker", "destroy"])
            except subprocess.CalledProcessError:
                pass
            try:
                os.makedirs(boot2docker_dir)
            except OSError:
                pass
            with open(boot2docker_profile, 'w') as prof_file:
                with open(dev_boot2docker_profile) as dev_prof_file:
                    prof_file.write(dev_prof_file.read().replace(
                        '~', user_home_dir
                    ))

        subprocess.check_call(["boot2docker", "init"])

    def __enter__(self):
        """
            Start up the VM, creating it if it doesn't exist.
        """

        subprocess.check_call(["boot2docker", "up"])
        self.shellinit()

        return(self)

    def __exit__(self, type, value, traceback):
        """
            Shutdown the VM.
        """

        if self.shutdown:
            subprocess.check_call(["boot2docker", "down"])

    def shellinit(self):
        """
            Set environment variables.
        """

        vm_vars = subprocess.check_output(["boot2docker", "shellinit"]).strip()
        vm_vars = vm_vars.split()[1::2]
        vm_vars = dict([_.split(b'=') for _ in vm_vars])

        if sys.version_info.major == 2:
            os.environ.update(vm_vars)
        elif sys.version_info.major >= 3:
            os.environb.update(vm_vars)

    @property
    def ip(self):
        """
            Get the VM's IP address.

            Returns:
                (str):              The IP Address of the VM.
        """

        vm_ip = subprocess.check_output(["boot2docker", "ip"]).strip()

        if sys.version_info.major >= 3:
            vm_ip = vm_ip.decode("utf-8")

        return(vm_ip)


class DockerMachine(Docker):
    def __init__(self, machine_name, shutdown=True):
        """
            Creates/recreate the VM if it doesn't exist or settings are off.
        """

        super(DockerMachine, self).__init__()
        self.shutdown = shutdown
        self.machine_name = machine_name

        subprocess.call([
            "docker-machine", "create",
            "--driver", "virtualbox",
            "--virtualbox-memory", "2048",
            "--virtualbox-cpu-count", "8",
            "--virtualbox-host-dns-resolver",
            self.machine_name
        ])

    def __enter__(self):
        """
            Start up the VM, creating it if it doesn't exist.
        """

        subprocess.call(["docker-machine", "start", self.machine_name])
        self.shellinit()

        return(self)

    def __exit__(self, type, value, traceback):
        """
            Shutdown the VM.
        """

        if self.shutdown:
            subprocess.call(["docker-machine", "stop", self.machine_name])

    def shellinit(self):
        """
            Set environment variables.
        """

        vm_vars = subprocess.check_output([
            "docker-machine",
            "env",
            self.machine_name
        ]).strip().splitlines()
        vm_vars = "\n".join([_ for _ in vm_vars if _.startswith("export")])
        vm_vars = vm_vars.split()[1::2]
        vm_vars = dict([_.replace("\"", "").split(b'=') for _ in vm_vars])

        if sys.version_info.major == 2:
            os.environ.update(vm_vars)
        elif sys.version_info.major >= 3:
            os.environb.update(vm_vars)

    @property
    def ip(self):
        """
            Get the VM's IP address.

            Returns:
                (str):              The IP Address of the VM.
        """

        vm_ip = subprocess.check_output([
            "docker-machine", "ip", self.machine_name
        ]).strip()

        if sys.version_info.major >= 3:
            vm_ip = vm_ip.decode("utf-8")

        return(vm_ip)


def open_browser(url):
    """
        Opens a browser to the given URL as soon as it is ready (within 0.1s).

        Args:
            url(str):       URL to open the browser.
    """

    wait = True
    while wait:
        try:
            content = urlopen(url).read()
            if (content != "Gateway Timeout: can't connect to remote host"):
                wait = False
        except URLError:
            time.sleep(0.1)

    webbrowser.open(url)


class OptionDefaultAction(argparse.Action):
    """
        A custom action for an argparse option.

        Ensures that the default value is only used if the option is provided.
        If the option is not provided, the default value is `None`. If a value
        is provided with the option, then it is used.
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(OptionDefaultAction, self).__init__(
            option_strings, dest, nargs, **kwargs
        )

        self.option_default = self.default
        self.default = None

    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            values = self.option_default

        setattr(namespace, self.dest, values)


def main(*argv):
    """
        Handles boot2docker and docker with our image in an easy-to-use way.

        Args:
            argv(strs):     Command line arguments including executable name.

        Returns:
            int:            Exit code.
    """

    machine_name = "nanshe-workflow"
    workflow_name = "nanshe_workflow"
    parent_image_name = "nanshe/nanshe"
    image_name = "dudlab/nanshe_workflow"
    docker_dir = os.path.dirname(os.path.abspath(__file__))
    workflow_dir = os.path.join(docker_dir, workflow_name)
    docker_workdir = "/" + workflow_name

    DockerVM = None
    if has_docker_machine:
        DockerVM = lambda shutdown: DockerMachine(
            machine_name, shutdown=shutdown
        )
    elif has_boot2docker:
        DockerVM = Boot2Docker

    argv = list(argv)

    parser = argparse.ArgumentParser(
        description="Simplified startup of the container/workflow.",
        usage="startup-nanshe-workflow " +
              "[-h] [-d [DIRECTORY]] [-u] [-s] [-p] [-w] [-t] [-b] " +
              "[docker <DOCKER_ARGS>...] [ipython <IPYTHON_ARGS>...]"
    )
    parser.add_argument(
        "-d", "--directory",
        nargs='?',
        default=os.path.curdir,
        action=OptionDefaultAction,
        help="Data directory to mount and install the workflow into."
    )
    parser.add_argument(
        "-u", "--update",
        action="store_true",
        help="Whether to update the docker image and the git repo."
    )
    parser.add_argument(
        "-s", "--no-shutdown",
        action="store_true",
        help="Whether to shutdown the VM after exiting."
    )
    parser.add_argument(
        "-p", "--persist",
        action="store_true",
        help="Whether to keep the container after exiting."
    )
    parser.add_argument(
        "-w", "--mount-workflow",
        action="store_true",
        help="Whether to mount the workflow from the repo into the container."
    )
    parser.add_argument(
        "-t", "--testing",
        action="store_true",
        help="Whether to enable testing of the workflows."
    )
    parser.add_argument(
        "-b", "--build",
        action="store_true",
        help="Whether to rebuild the docker image from the repo."
    )

    known_args = argv[1:]

    ipython_args = []
    try:
        ipython_arg_index = known_args.index("ipython")
        ipython_args = known_args[ipython_arg_index+1:]
        known_args = known_args[:ipython_arg_index]
    except ValueError:
        pass

    docker_args = []
    try:
        docker_arg_index = known_args.index("docker")
        docker_args = known_args[docker_arg_index+1:]
        known_args = known_args[:docker_arg_index]
    except ValueError:
        pass

    has_short_workdir_opt = docker_args.count("-w")
    has_long_workdir_opt = docker_args.count("--workdir")
    assert (has_short_workdir_opt + has_long_workdir_opt) <= 1

    workdir_arg = ""
    if has_short_workdir_opt:
        workdir_arg = "-w"
    elif has_long_workdir_opt:
        workdir_arg = "--workdir"

    if workdir_arg:
        i = docker_args.index(workdir_arg)
        if not os.path.isabs(docker_args[i + 1]):
            docker_workdir = docker_args[i + 1] = os.path.abspath(os.path.join(
                docker_workdir, docker_args[i + 1]
            ))

    for volume_arg in ["-v", "--volume"]:
        try:
            i = docker_args.index(volume_arg)
            while i < len(docker_args):
                docker_arg_i = docker_args[i + 1].split(":")
                docker_arg_i[0] = os.path.abspath(docker_arg_i[0])
                if not os.path.isabs(docker_arg_i[1]):
                    docker_arg_i[1] = os.path.abspath(os.path.join(
                        docker_workdir, docker_arg_i[1]
                    ))
                docker_arg_i = ":".join(docker_arg_i)
                docker_args[i + 1] = docker_arg_i
                i = docker_args.index(volume_arg, i + 2)
        except ValueError:
            pass

    parsed_args, unknown_args = parser.parse_known_args(known_args)
    directory = parsed_args.directory
    update = parsed_args.update
    shutdown = not parsed_args.no_shutdown
    persist = parsed_args.persist
    mount_workflow = parsed_args.mount_workflow
    testing = parsed_args.testing
    build = parsed_args.build

    if directory is not None:
        directory = os.path.abspath(directory)

    assert not (bool(directory) and bool(mount_workflow)), \
        "Cannot mount a data directory and the workflow at the same time."

    if update:
        cwd = os.getcwd()
        os.chdir(docker_dir)

        changes = subprocess.check_output([
            "git", "status", "--porcelain", "--ignore-submodules"
        ])
        num_changes = len(changes.splitlines())
        assert num_changes == 0, "Git repo not clean."

        changes = subprocess.check_output([
            "git",
            "submodule",
            "foreach",
            "--recursive",
            "git",
            "status",
            "--porcelain"
        ])
        num_changes = len(changes.splitlines())
        submodules = subprocess.check_output([
            "git", "submodule", "foreach", "--recursive", ""
        ])
        num_changes -= len(submodules.splitlines())
        assert num_changes == 0, "Git submodule(s) not clean."

        subprocess.check_call(["git", "checkout", "master"])
        subprocess.check_call([
            "git",
            "pull",
            "--ff-only",
            "https://github.com/nanshe-org/docker_nanshe_workflow",
            "master"
        ])
        subprocess.check_call(["git", "submodule", "update", "--checkout"])

        os.chdir(cwd)

        user_home_dir = os.path.expanduser('~')
        boot2docker_dir = os.path.join(user_home_dir, ".boot2docker")
        boot2docker_profile = os.path.join(boot2docker_dir, "profile")
        dev_boot2docker_profile = os.path.join(
            docker_dir, ".boot2docker_profile"
        )
        try:
            with open(boot2docker_profile) as prof_file:
                with open(dev_boot2docker_profile) as dev_prof_file:
                    prof_hash = hashlib.sha1(prof_file.read())
                    dev_prof_hash = hashlib.sha1(dev_prof_file.read().replace(
                        '~', user_home_dir
                    ))

                    prof_hash = prof_hash.digest()
                    dev_prof_hash = dev_prof_hash.digest()

                    if prof_hash != dev_prof_hash:
                        os.remove(boot2docker_profile)
        except IOError:
            pass

    with DockerVM(shutdown=shutdown) as vm:
        if update or (image_name not in vm.images["REPOSITORY"]):
            vm.pull(parent_image_name)
            if not build:
                try:
                    vm.pull(image_name)
                except subprocess.CalledProcessError:
                    build = True

        if build:
            vm.build(image_name, docker_dir)

        mounted_directory = ""
        if directory is not None:
            subprocess.check_call([
                "docker",
                "run",
                "-it",
                "--rm",
                "--volume=" + docker_dir + ":" + "/mnt/docker",
                "--volume=" + directory + ":" + "/mnt/ext",
                "--entrypoint=/mnt/docker/install_workflows.sh",
                image_name,
                ".",
                "/mnt/ext"
            ])
            print("Installed workflows into directory: \"%s\"" % directory)
            mounted_directory = "/root/work"
        elif mount_workflow:
            directory = workflow_dir
            mounted_directory = "/" + workflow_name

        workflow_url = "http://" + vm.ip
        browser_thread = threading.Thread(
            target=open_browser,
            args=(workflow_url,)
        )
        browser_thread.daemon = True
        browser_thread.start()

        subprocess.check_call(
            [
                "docker",
                "run",
                "-it",
                "-p", "80:8888"
            ] +
            (
                [] if persist else ["--rm"]
            ) +
            (
                [
                    "-v", directory + ":" + mounted_directory
                ] if directory else []
            ) +
            (
                [
                    "-w",  mounted_directory
                ] if mounted_directory else []
            ) +
            (
                [
                    "-e", "TEST_NOTEBOOKS" + "=" + "true"
                ] if testing else []
            ) +
            docker_args +
            [
                image_name
            ] +
            ipython_args
        )

    return(0)
