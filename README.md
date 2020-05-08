# Warbler

Warbler is a mock twitter clone built completely as a backend application. Users can sign up/login, follow users, have followers, and create/like messages (tweets). Bcrypt authentication is used to manage user login and Flask sessions store current user data.

The app is built with Flask and Jinja and uses a PostgreSQL database. Tests were written for the views and models using the Python unittest module.

Live demo: https://warbler-flask-app.herokuapp.com

Create a new account or login using the following information:

* Username: user
* Password: password

## Getting Started
To clone the repository run the following command:

```
git clone https://github.com/paigegodfrey/warbler.git
```

In the project directory please run:

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
createdb warbler
python seed.py
flask run
```

