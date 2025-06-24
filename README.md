## superset-cloner-flask-react
A React frontend app powered by a Flask backend with Superset dashboard cloning capabilities.

### Pre-requisites
- Python 3.13+
- Docker
- Superset 4.0.0+ - Follow instructions [here](https://github.com/nathanbaleeta/magasin-superset-dashboard-cloner/blob/main/SUPERSET_SETUP.md) on how to install & configure the API for consuming

### Quick Setup
The project uses [Pip]([https://python-poetry.org/](https://pypi.org/project/pip/)) to keep track of its dependencies. To setup follow instructions below:

```bash
git clone git@github.com:nathanbaleeta/superset-cloner-flask-react.git

cd superset-cloner-flask-react

python3 -m venv venv

source venv/bin/activate

pip install Flask requests flask_cors
```

You'lll also need to set three environment variables before running the script: ```SUPERSET_INSTANCE_URL```, ```SUPERSET_USERNAME```, and ```SUPERSET_PASSWORD```. If any of these are not set, the Flask backend will fail to run. 

```bash
export SUPERSET_INSTANCE_URL='http://localhost:8088/'
export SUPERSET_USERNAME='admin'
export SUPERSET_PASSWORD='admin'
```

You can verify the ENV variables are set correctly by running
```bash
printenv
```

If you're going to test on staging, you'll need to change these three variables. Take note of the last / in the instance URL, as it's needed for the API endpoint concatenates to work properly.

### Launch backend
To bootstrap the Flask backend
```
python app.py
```
