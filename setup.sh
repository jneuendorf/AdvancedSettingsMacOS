#!/usr/bin/env bash

which brew
if [[ $? == "1" ]]; then
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi
brew install python python3
brew upgrade python python3

python3 -m venv venv
source ./venv/bin/activate
pip install -r ./requirements.txt
./manage.py runserver
