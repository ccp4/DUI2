# DUI2

client/server implementation of DUI (Dials User Interface)

## Requirements

This project relies on an installation of `python3` with `dials` (https://dials.github.io/), `pyside2` and `requests` among other dependencies. There are two ways to install DUI2:


## Option 1, Installation with curl and ccp4

This assumes you have already installed and set up CCP4, which include `dials` and `pyside2`.

First download install script for `DUI2`:

      curl -L -O https://raw.githubusercontent.com/ccp4/DUI2/master/install_dui2_after_ccp4_w_curl.sh

Next run the downloaded script with `bash`:

      bash install_dui2_after_ccp4_w_curl.sh

Follow the instruction at the end of the script.

There are three available command line tools after installation:

1. Fully local App (running both, server and client locally)

       dui2

2. Server App (Which actually runs Dials commands)

       dui2_server_side host=MY_HOST port=MY_PORT init_path=/PATH/TO/USER/DATA

3. Client App (GUI front end that talks to the Server App)

       dui2_client_app url=http://...[URL of the server]

## Option 2, Installation of everything (including Dials) with conda, mamba and git

This assumes you have already installed an Anaconda package manger like `miniconda` and have a BASH shell active with the `conda` command enabled, see https://docs.anaconda.com/miniconda/install/ for details.

First update `conda`:

       conda update conda -y

We will use `mamba` to make the installation of `Dials` and other needed dependencies in a virtual environment easier and faster:

       conda install -c=conda-forge mamba -y

Provably Anaconda will ask you to run a specific command or to close and reopen your shell to make the installation of `mamba` effective

Next create a virtual environment with `Dials`, `PySide V2`, `PyQt webengine` and `git` inside it, replace `/PATH/TO/ENV/W/NAME` with the path where you want to install `Dials` and the GUI dependencies. This may take a few minutes:

       mamba create -p /PATH/TO/ENV/W/NAME -c conda-forge python=3.11 dials pyside2 pyqtwebengine git

Now we should activate our newly created environment, again replace `/PATH/TO/ENV/W/NAME` with the path where you installed `Dials` and other dependencies:

       conda activate /PATH/TO/ENV/W/NAME


Finally clone the DUI2 source code from GitHub repository:

       git clone -b v2025.7.17  https://github.com/ccp4/DUI2.git

The same tools as if installed with `curl` and `CCP4` are available, just different ways to invoke them. Remember that if you are running Dui2 from another directory, to put the full path of the `.py` file:

1. Fully local App (running both, server and client locally):

       python DUI2/src/run_dui2.py

2. Server App (Which actually runs Dials commands)

       python DUI2/src/run_dui2_server.py host=MY_HOST port=MY_PORT init_path=/PATH/TO/USER/DATA

3. Client App (GUI front end that talks to the server app)

       python DUI2/src/run_dui2_client.py url=http://...[URL of the server]


