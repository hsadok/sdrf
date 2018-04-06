#!/usr/bin/env bash
echo "Type the root password"
su root -c "\
apt-get update && \
apt-get install -y git python-dev python-pip htop parallel tmux vim && \
\
pip install virtualenv && \
pip install virtualenvwrapper"

export WORKON_HOME=~/Envs
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv sdrf
workon sdrf
pip install -r requirements.txt

cd sdrf/helpers/c_live_tree
/usr/bin/env bash compile.sh

cd -
cd sdrf/tests
/usr/bin/env bash compile.sh
cd -
