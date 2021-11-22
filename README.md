# Kraft-Heinz App Overfill

## Getting started
### Install Flask
1. Run `python -m pipenv --version` (or `python3 -m pipenv --version`)

If you don't have it, install it with `pip install pipenv` (or `pip3 install pipenv`)

2. Run `python -m pipenv shell`
3. Run `pip install pipenv` (yes, again)
4. Run `python -m pipenv install`
5. Run `python -m pipenv run python`
6. Paste:
```
from app import db # import db
db.create_all() # create database and tables
exit()
```
7. Run `python -m pipenv run python app.py`
8. Profit (server should be running)

### Install and run Vue project
If you don't have it, install Node from https://nodejs.org/en/download/ (or on Linux get it with sudo apt get/install)
1. Run `npm install -g yarn`
2. Run `yarn global add @quasar/cli`
3. Run `yarn install`
4. Run `quasar dev`
5. Profit (server should be running)

Install Visual Studio Code extensions ESLint and Vetur to be able to open .vue files
