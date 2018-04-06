Stateful Dominant Resource Fairness
===================================

This repository contains source code of the discrete-event tasks simulator used
in the SDRF paper. It also includes an implementation of
`DRF <sdrf/allocators/wdrf.py>`_ and `SDRF <sdrf/allocators/sdrf.py>`_ that can
be used with the simulator. Moreover the SDRF implementation uses a
`live tree <sdrf/helpers/c_live_tree>`_ written in C++11.

Download and Install Dependencies
---------------------------------

First, ensure that pip is installed and python headers are available. In a
Debian based system this can be done with (make sure you have root
privileges)::

    apt install git python-dev python-pip

Then, clone this repository::

    git clone git@github.com:hugombarreto/sdrf.git

Install all the python dependencies (unless you are using something like
virtualenv, which is highly recommended, you must have root privileges)::

    pip install -r requirements.txt

Finally, compile C and C++ sources::

    cd sdrf/helpers/c_live_tree
    bash compile.sh


Script
......

Alternatively, you may use the ``install.sh``  script to setup everything
automatically. The script installs all dependencies and sets a virtualenv. It
was designed to work with a fresh install of Debian 9, but it may work in other
Debian based systems as well. Run it with::

    source install.sh


Usage
-----

To view available commands run::

    python -m sdrf --help

For further help in a particular subcommand you can run::

    python -m sdrf SUBCOMMAND --help


Simulate task allocation
------------------------

The simulator uses a file with tasks as input. The file is a simple csv with
one task per line. Tasks must be arranged in chronological order. Every line
must be formatted as follow::

    [submit time],[start time],[finish time],[user id],[task id],[cpu],[memory]

Fields Description
..................

:[submit time]:
    Time the task was submitted by the user (in microseconds). The first
    timestamp can be any value, it does not need to be zero.

:[start time]:
    Time the task started in the real workload. If the workload is syntactic it
    can be the same as the submit time.

:[finish time]:
    Time the task finished in the real workload. If the workload is syntactic
    it can be the start time + task duration.

:[user id]:
    A unique identifier for the user that submits the task (any string should
    work).

:[task id]:
    A unique identifier for the task (any string should work).

:[cpu]:
    Amount of CPUs required by the task (can be a floating point number, which
    is useful in case this value was normalized).

:[memory]:
    Amount of memory required by the task (can be a floating point number,
    which is useful in case this value was normalized).

Running
.......

To run the simulation use the ``simulate_task_allocation`` command::

    python -m sdrf simulate_task_allocation [OPTIONS] TASKS_FILE [SAVING_PATH]

You can find details about the available options with::

    python -m sdrf simulate_task_allocation --help

To run the simulator with SDRF you must specify at least one delta and one
resource percentage, e.g.::

    python -m sdrf simulate_task_allocation tasks.csv -r0.9 -d0.9999

Simulate multiple parameters using multiple cores
-------------------------------------------------

If you want to run the simulation for multiple parameters, the best way is to
use GNU Parallel. I provide an example command that can be adapted to your
needs::

    parallel --tmux --delay 5.1 --bar --joblog <log location> --memfree 1G --shuf python -m sdrf simulate_task_allocation --same_share -a sdrf <tasks file> <saving path> ::: -r0.5 -r0.6 -r0.7 -r0.8 -r0.9 -r1.0 ::: -d0.9 -d0.99 -d0.999 -d0.9999 -d0.99999 -d0.999999 -d0.9999999


Using Google Cluster Traces
---------------------------

We also include a parser for the google cluster traces. You may download the
traces following the instructions here_.

.. _here: https://github.com/google/cluster-data/blob/master/ClusterData2011_2.md

The parser automatically filters tasks that require zero resources as well as
tasks that failed for problems beyond the reach of users. In the end it creates
a csv file that follows the format required by the ``simulate_task_allocation``
command. Usage::

    python -m sdrf parse_google_tasks DATASET_DIR SAVING_FILE

where ``DATASET_DIR`` is the directory containing the Google cluster data and
``SAVING_FILE`` is the name of the output file.

