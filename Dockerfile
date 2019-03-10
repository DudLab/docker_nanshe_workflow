FROM nanshe/nanshe_notebook:sge
MAINTAINER John Kirkham <jakirkham@gmail.com>

ADD nanshe_workflow /nanshe_workflow
RUN rm -rf /nanshe_workflow/.git
ADD .git/modules/nanshe_workflow /nanshe_workflow/.git
RUN export INSTALL_CONDA_PATH="/opt/conda${PYTHON_VERSION}" && \
    . "${INSTALL_CONDA_PATH}/etc/profile.d/conda.sh" && \
    conda activate base && \
    sed -i.bak "s/..\/..\/..\/nanshe_workflow/../g" /nanshe_workflow/.git/config && \
    rm -f /nanshe_workflow/.git/config.bak && \
    sed -i.bak "/.*worktree = .*/d" /nanshe_workflow/.git/config && \
    rm -f /nanshe_workflow/.git/config.bak && \
    cd /nanshe_workflow && git update-index -q --refresh && cd / && \
    conda deactivate

ADD entrypoint.sh /usr/share/docker/entrypoint_3.sh
ADD install_workflows.sh /usr/share/docker/install_workflows.sh

RUN for PYTHON_VERSION in 2 3; do \
        export INSTALL_CONDA_PATH="/opt/conda${PYTHON_VERSION}" && \
        . "${INSTALL_CONDA_PATH}/etc/profile.d/conda.sh" && \
        conda activate base && \
        cd /nanshe_workflow && git update-index -q --refresh && cd / && \
        (mv /nanshe_workflow/.git/shallow /nanshe_workflow/.git/shallow-not || true) && \
        export CONDA_PKGS_DIRS="/opt/conda${PYTHON_VERSION}/conda-bld/bld_pkgs" && \
        conda build /nanshe_workflow/nanshe_workflow.recipe && \
        unset CONDA_PKGS_DIRS && \
        (mv /nanshe_workflow/.git/shallow-not /nanshe_workflow/.git/shallow || true) && \
        conda install -qy --use-local nanshe_workflow && \
        conda remove -qy nanshe_workflow && \
        conda build purge && \
        rm -rf /opt/conda${PYTHON_VERSION}/conda-bld/* && \
        conda clean -tipsy && \
        python -m pip install -e /nanshe_workflow && \
        python -m jupyter trust /nanshe_workflow/nanshe_ipython.ipynb && \
        python -m jupyter nbextension enable --sys-prefix execute_time/ExecuteTime && \
        python -c "from notebook.services.config import ConfigManager as C; C().update('notebook', {'ExecuteTime': {'clear_timings_on_clear_output': True}})" && \
        conda deactivate && \
        rm -rf ~/.conda && \
        rm -rf ~/.cache ; \
    done

ENV OPENBLAS_NUM_THREADS=1
ENV DASK_DISTRIBUTED__WORKER__MULTIPROCESSING_METHOD="spawn"

RUN rm -f /tmp/test.sh && \
    touch /tmp/test.sh && \
    chmod +x /tmp/test.sh && \
    echo -e '#!/bin/bash' >> /tmp/test.sh && \
    echo -e "" >> /tmp/test.sh && \
    echo -e "set -e" >> /tmp/test.sh && \
    echo -e "" >> /tmp/test.sh && \
    echo -e "export CORES=2" >> /tmp/test.sh && \
    echo -e "" >> /tmp/test.sh && \
    echo -e "for PYTHON_VERSION in 2 3; do" >> /tmp/test.sh && \
    echo -e "    . /opt/conda${PYTHON_VERSION}/etc/profile.d/conda.sh && " >> /tmp/test.sh && \
    echo -e "    conda activate base && " >> /tmp/test.sh && \
    echo -e "    cd /nanshe_workflow && " >> /tmp/test.sh && \
    echo -e "    /usr/share/docker/entrypoint.sh /usr/share/docker/entrypoint_2.sh /usr/share/docker/entrypoint_3.sh python setup.py test && " >> /tmp/test.sh && \
    echo -e "    (qdel -f -u root || true) && " >> /tmp/test.sh && \
    echo -e "    qstat && " >> /tmp/test.sh && \
    echo -e "    service sge_execd stop && " >> /tmp/test.sh && \
    echo -e "    service sgemaster stop && " >> /tmp/test.sh && \
    echo -e "    git clean -fdx && " >> /tmp/test.sh && \
    echo -e "    rm -rf ~/ipcontroller.o* && " >> /tmp/test.sh && \
    echo -e "    rm -rf ~/ipcontroller.e* && " >> /tmp/test.sh && \
    echo -e "    rm -rf ~/ipengine.o* && " >> /tmp/test.sh && \
    echo -e "    rm -rf ~/ipengine.e* && " >> /tmp/test.sh && \
    echo -e "    conda deactivate ; " >> /tmp/test.sh && \
    echo -e "done" >> /tmp/test.sh && \
    /tmp/test.sh && \
    rm /tmp/test.sh

WORKDIR /nanshe_workflow
ENTRYPOINT [ "/opt/conda/bin/tini", "--", "/usr/share/docker/entrypoint.sh", "/usr/share/docker/entrypoint_2.sh", "/usr/share/docker/entrypoint_3.sh", "python", "-m", "notebook", "--allow-root", "--no-browser", "--ip=0.0.0.0" ]
