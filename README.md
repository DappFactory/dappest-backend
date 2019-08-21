# dapp_store_backend

A backend for our dapp store.

NOTE: REMEMBER TO ALWAYS CLEAR DOCKER CONTAINERS AND VOLUMES. IF YOUR BUILD IS FAILING, THIS IS PROBABLY WHY.

## API endpoints

API endpoints can be viewed in Swagger @ `http://localhost:8000/api/v1/`.

## Quickstart

Clone the repo and docker-compose up.
```
git clone https://gitlab.com/DappFactory/dapp-store-backend.git
docker-compose -f local.yml up --build
```

## Running Tests

PLEASE CLEAR DOCKER CONTAINERS AND VOLUMES BEFORE RUNNING TESTS.
```
docker-compose -f test.yml up --build
```

## Deployment

In your production environment, make sure the ``DAPP_STORE_BACKEND_ENV`` environment variable is set to ``"prod"``.

## Notes For Developers On Docker

1. Docker Pruning of Volumes
```
alias dvp="docker volume prune --force"
```

2. Remove volumes (related to db) and migrations/ directories


3. Removing Containers That Are Stopped
```
alias dvp="docker volume prune --force
function drm() { docker rm $(docker ps -a -q); }
function ds() { docker stop $(docker ps -a -q); }
```

4. Running your Tests (Exec into container -> run locally!)
docker exec -it <CONTIANER_ID> /bin/sh

pytest -s dapp_store_backend/tests