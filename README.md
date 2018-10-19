# Goeievraagle
Search engine made for the "Zoekmachines" course at the University of Amsterdam,
taught by dr. Maarten Marx.

## Requirements

- Docker and docker-compose (Used for easy setup of Elasticsearch).
- Python 3.7 or higher.
- `pip` for installing Python packages.
- `yarn` for installing JavaScript libraries.

## Set-up

### Elasticsearch
- Run `docker-compose up -d` in the root folder to start Elasticsearch.

### Backend
- `cd` to the `backend` folder.
- Create a virtualenv: `virtualenv venv -p python3.7`.
- Activate the virtualenv: `. venv/bin/activate`.
- Install required packages: `pip install -r requirements.txt`.
- Import the data set: `flask import-data ../data/{questions,categories}.csv`.
- Run the development server: `flask run`.

### Frontend
- Open a new terminnal
- `cd` to the `frontend` folder.
- Install required packages: `yarn install`.
- Run the development server: `yarn dev`.

Now, go to http://localhost:8080/ in your browser.
