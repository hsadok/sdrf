#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install -y python-dev python-pip

sudo pip install virtualenv
sudo pip install virtualenvwrapper

export WORKON_HOME=~/Envs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv mmmdrf
workon mmmdrf
pip install -r requirements.txt
