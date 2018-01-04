[![Build Status](https://travis-ci.org/anyric/Yummy-Recipes-Api.svg?branch=master)](https://travis-ci.org/anyric/Yummy-Recipes-Api) [![Coverage Status](https://coveralls.io/repos/github/anyric/Yummy-Recipes-Api/badge.svg?branch=master)](https://coveralls.io/github/anyric/Yummy-Recipes-Api?branch=master) [![Maintainability](https://api.codeclimate.com/v1/badges/de93cc9873d904c8d2aa/maintainability)](https://codeclimate.com/github/anyric/Yummy-Recipes-Api/maintainability)
[![Code Health](https://landscape.io/github/anyric/Yummy-Recipes-Api/yummy-pull/landscape.svg?style=flat)](https://landscape.io/github/anyric/Yummy-Recipes-Api/yummy-pull)


# Yemmy Recipes API
Yemmy Recipes is an application that allow users to keep track of their owesome food recipes. It helps individuals who love to cook and eat good food to remember recipes and also share with others.

# Features
* Users can create an account
* Users can log in
* Users can create, view, update and delete recipe categories
* Users can create, view, update and delete recipes in existing categories

# Pre-requisites
The following list of softwares should be first install in order for the app to run.
* Python 3.6.X
* Flask
* Postman for GUI interaction (optional)
* Flasgger for documentation
* Postgres Database

# Installations
The following steps should help you setup the environment and get the app runing.
* Install Python
#### For Windows and Mac OS
Download the excutable files from the official Python website at the link below
[https://www.python.org/downloads/](https://www.python.org/downloads/) and just run the installer packages

#### For Linux OS
From the command line run '$ sudo apt-get install python3.6'

#### Installing the project locally
* Create a new folder in your favourite location e.g 'project' on the Desktop
* Move into the new folder you have just created
``cd Desktop/project``
* Install virtualenv so that we can create a virtual environment to run the project ``$pip install virtualenv``
* create a virtual environment called "my_env" ``$python3 -m env my_env``
* clone the project repo ``$git clone https://github.com/anyric/Yummy-Recipes-Api.git``
* Activate your virtual environment `$source my_env/bin/activate`
* Install project requirements from the requirements.txt file ``(my_env)~$pip install -r requirements.txt``
* At this point am assuming you have already install your postgres database, So go a head and create two databases ``yummy_api`` and ``test_db`` for the development/production and testing configurations respectively.
* Remember to update the database URL for the Config and TestingConfig classes in the `config.py` module respectively to reflect your local settings especially the username and password for the database account
* Run the application ``(my_env)~$ python app.py``

# Running tests
You can test the application using two libraries nose2 or nosetests: ``nose2 --with-coverage` or `nosetests --with-coverage --cover-package=apps``

# API Endpoints
### Users
|            URL Endpoints            | HTTP Requests |                      Access                    | Public Access|
|-------------------------------------|---------------|------------------------------------------------|--------------|
|POST /recipe/api/v1.0/user/register  |     POST      | Register a new user                            |  TRUE        |
|PUT /recipe/api/v1.0/user/update     |     PUT       | Change user password                           |  FALSE       |
|GET /recipe/api/v1.0/user/view       |     GET       | Retrieves a paginated lists of registered users|  FALSE       |
|DELETE /recipe/api/v1.0/user/delete  |   DELETE      | Deletes a registered user                      |  FALSE       |


