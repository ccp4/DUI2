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

3. Client App (GUI front end that talks to the server app)

       dui2_client_app url=http://...[URL of the server]

## Option 2, Installation of everything (including Dials) with conda and git

This assumes you have already installed an Anaconda package manger like `miniconda` and have a BASH shell active with the `conda` command enabled. If you have already installed one of the packages, like for example `git` you may skip the step where you install it.

First update `conda`:

       conda update conda -y

We will need to downgrade the version of `Python` to make possible the installation of `dials`, consider doing the entire installation on a different virtual environment:

       conda install python=3.11

Next install `dials`, this may take several minutes:

       conda install -c conda-forge dials -y

Then install `PySide V2`, again several minutes, be very patient:

       conda install -c conda-forge pyside2 -y

Next install an `HTML` viewer compatible with in `PySide V2`:

       conda install -c conda-forge pyqtwebengine -y

Next install `git`:

       conda install -c conda-forge git -y

Finally clone the DUI2 repository (pre-release branch):

       git clone -b v2025.1.12  https://github.com/ccp4/DUI2.git



The same tools as if installed with `curl` and `CCP4` are available, just different ways to invoke them. Remember that if you are running Dui2 from another directory, to put the full path of the `.py` file:

1. Fully local App (running both, server and client locally):

       python DUI2/src/run_dui2.py

2. Server App (Which actually runs Dials commands)

       python DUI2/src/run_dui2_server.py host=MY_HOST port=MY_PORT init_path=/PATH/TO/USER/DATA

3. Client App (GUI front end that talks to the server app)

       python DUI2/src/run_dui2_client.py url=http://...[URL of the server]


