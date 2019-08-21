# dapp_store_backend - data_fetcher

Service to fetch external data from 3rd party APIs.

## Quickstart

Run the individual service.
```
git clone https://gitlab.com/DappFactory/dapp-store-backend.git
docker build -f ./local/data_fetcher/Dockerfile .
docker run -v ./:/app:rw <image_id>
```

## Running Tests

```
docker exec <container_id> pytest --pyargs data_fetcher
```

## Deployment

In your production environment, make sure the ``DAPP_STORE_BACKEND_ENV`` environment variable is set to ``"prod"``.
