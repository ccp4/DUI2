# DUI2
client/server implementation of DUI (Dials User Interface)

## Requirements

This project relies on an installation of Python3 with Dials, PySide2 and Requests among other dependencies

## Installation with git and conda

This assumes you have already installed DIALS and have a BASH shell active with the DIALS environment sourced (. dials_env.sh).

First install `pyside2`:

      libtbx.conda install -c conda-forge pyside2

Clone the DUI2 repository (pre-release branch):

       git clone -b v0.91 https://github.com/ccp4/DUI2.git


There are three available command line tools in the final product:

1. Fully local App (running both, server and client locally):

       dials.python DUI2/src/all_local.py

2. Server App (Which actually runs Dials commands)

       dials.python DUI2/src/only_server.py host=MY_HOST port=MY_PORT init_path=/PATH/TO/USER/DATA

3. Client App (GUI front end that talks to the server app)

       dials.python DUI2/src/only_client.py url=http://...[URL of the server]

## Installation with curl and ccp4

This assumes you have already installed and set up CCP4, which include DIALS and PySide2.

First download install script for `DUI2`:

      curl -L -O https://raw.githubusercontent.com/ccp4/DUI2/master/install_dui2_after_ccp4_w_curl.sh

Run the downloaded script with `bash`:

      bash install_dui2_after_ccp4_w_curl.sh

Follow the instruction at the end of the script.

The same tools as if installed with git and conda are available, just different ways to invoke:

1. Fully local App (running both, server and client locally):

       dui_all_local

2. Server App (Which actually runs Dials commands)

       dui_server

3. Client App (GUI front end that talks to the server app)

       dui_client

