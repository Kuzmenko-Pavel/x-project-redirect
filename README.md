# x-project-redirect

Getting Started
---------------

- Change directory into your newly created project.

    cd redirect

- Create a Python virtual environment.

    virtualenv --no-site-packages -p python3.5 env

- Upgrade packaging tools.

    env/bin/pip install --upgrade pip setuptools

- Install the project req

    sudo apt install unixodbc-dev python3.5-pyodbc

- Install the project in editable mode with its testing requirements.

    env/bin/pip install -e .

- Run your project.

    env/bin/python -m x_project_redirect

- Run celery project.

    env/bin/celery worker -A x_project_redirect.celery_worker -Q click -l DEBUG

