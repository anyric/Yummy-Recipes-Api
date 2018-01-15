#!/bin/sh
rm -r migrations
python3 controller.py db init
python3 controller.py db migrate
python3 controller.py db upgrade