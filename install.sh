#!/usr/bin/env bash
sudo apt-get update
sudo apt-get install -y libfreetype6-dev python-dev python-pip python-tk

sudo pip install virtualenv
sudo pip install virtualenvwrapper

export WORKON_HOME=~/Envs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv mmmdrf
workon mmmdrf
pip install -r requirements.txt
