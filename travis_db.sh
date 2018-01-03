#!/bin/sh
service postgresql start
python3 controller.py db init
python3 controller.py db migrate
python3 controller.py db upgrade