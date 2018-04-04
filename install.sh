#!/usr/bin/env bash
echo "Type the root password"
su root -c "\
apt-get update && \
apt-get install -y git libfreetype6-dev python-dev python-pip python-tk htop parallel tmux vim && \
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
