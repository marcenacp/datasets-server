# Dataset viewer - reverse proxy

> Reverse-proxy in front of the API. Only used in the docker compose (CI), not in the Helm chart (staging/prod)

See [docker-compose-dataset-viewer.yml](../../tools/docker-compose-dataset-viewer.yml) for usage.

The reverse proxy uses nginx:

- it serves the static assets directly (the API also serves them if required, but it's unnecessary to go through starlette for this, and it generates errors in Safari, see [1](https://github.com/encode/starlette/issues/950) and [2](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/CreatingVideoforSafarioniPhone/CreatingVideoforSafarioniPhone.html#//apple_ref/doc/uid/TP40006514-SW6))
- it serves the OpenAPI specification
- it proxies the other requests to the API

It takes various environment variables, all of them are mandatory:

- `ASSETS_STORAGE_ROOT`: the directory that contains the static assets, eg `/storage/assets`
- `CACHED_ASSETS_STORAGE_ROOT`: the directory that contains the static cached assets, eg `/storage/cached-assets`
- `OPENAPI_FILE`: the path to the OpenAPI file, eg `docs/source/openapi.json`
- `HOST`: domain of the reverse proxy, eg `localhost`
- `PORT`: port of the reverse proxy, eg `80`
- `URL_ADMIN`: URL of the admin, eg `http://admin:8081`
- `URL_API`: URL of the API, eg `http://api:8080`
- `URL_ROWS`: URL of the rows service, eg `http://rows:8082`
- `URL_SEARCH`: URL of the search service, eg `http://search:8083`
- `URL_SSE_API`: URL of the SSE API service, eg `http://sse-api:8085`
- `URL_WEBHOOK`: URL of the webhook service, eg `http://webhook:8087`

The image requires three directories to be mounted (from volumes):

- `$ASSETS_DIRECTORY` (read-only): the directory that contains the static assets.
- `/etc/nginx/templates` (read-only): the directory that contains the nginx configuration template ([templates](./nginx-templates/))
