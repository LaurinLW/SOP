# Experiment

## Setup
Most things can be setup using the setup script.
It requires python 3 and the python docker package to run.

Run `python setup.py setup` to start the setup process. The script will ask for the rpc url and a directory to share folders between containers.
Once the setup is complete you can start the project using `python setup.py start`.

You can use `python setup.py stop` to stop the running webserver container and all running experiment containers.