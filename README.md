# DUI2
client/server implementation of DUI (Dials User Interface)

## Requirements

This project relies on an installation of Python3 with Dials, PySide2 and Requests among other dependencies

## Installation

This assumes you have already installed DIALS and have a BASH shell active with the DIALS environment sourced (. dials_env.sh).

First install `pyside2`:

      libtbx.conda install -c conda-forge pyside2

Clone the DUI2 repository (pre-release branch):

       git clone -b V0.9 https://github.com/ccp4/DUI2.git


There are three available command line tools in the final product:

1. Fully local App (running both, server and client locally):

       dials.python DUI2/src/all_local.py

2. Server App (Which actually runs Dials commands)

       dials.python DUI2/src/only_server.py host=MY_HOST port=MY_PORT init_path=/PATH/TO/USER/DATA

3. Client App (GUI front end that talks to the server app)

       dials.python DUI2/src/only_client.py url=http://...[URL of the server]

