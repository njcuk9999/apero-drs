# The APERO reduction interface module


## Installation

Normally just install this after apero-drs 
with:
```bash
pip install -U -e ./apero-ri
```

However for developers you can install this separately

```bash
conda create --name apero-ri python=3.12
conda activate apero-ri

git clone git@github.com:njcuk9999/apero-drs.git
git clone git@github.com:njcuk9999/lbl.git

pip install -U -e ./apero-drs/apero-core -e ./lbl -e ./apero-drs/apero-drs[dev]
pip install -U -e ./apero-ri[dev]
```

## How to run

First time you must run `apero_ri_setup`  to setup the page

After that you just run `apero_ri_run --port=1234`

Then you just need to forward the port you select, and it should work.

The web-server will only work while `apero_ri_run` is running.


## Production deployment

For real multi-user deployments, run with the production WSGI server
(waitress) instead of the Flask development server:

```bash
apero_ri_run --port=1234 --production --threads=16
```

Recommended setup is a reverse proxy (nginx/Apache) terminating HTTPS in
front of the app. The following environment variables configure the app
for that topology:

| Variable | Meaning | Default |
|----------|---------|---------|
| `ARI_PROXY_COUNT` | Number of trusted reverse proxies in front of the app (e.g. `1` for a single nginx). Enables `X-Forwarded-*` handling so client IPs, rate limits, and HTTPS detection are correct. | `0` (off) |
| `ARI_HTTPS` | Set to `1` when the site is served over HTTPS. Marks session cookies `Secure` and enables HSTS. | off |
| `ARI_MAX_CONTENT_MB` | Maximum request body size in MB. | `128` |

Example nginx site config:

```nginx
server {
    listen 443 ssl;
    server_name ari.example.org;
    # ... ssl_certificate / ssl_certificate_key ...

    location / {
        proxy_pass http://127.0.0.1:1234;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

with the app started as:

```bash
ARI_PROXY_COUNT=1 ARI_HTTPS=1 apero_ri_run --port=1234 --production
```

The app exposes `GET /healthz` (unauthenticated, no DB access) for load
balancer health checks and uptime monitoring, and serves a `robots.txt`
that opts out of search-engine indexing.


## Python use

### Use:

```python
import apero_ri
```


### import rules

can import any thing from:

aperocore
apero

