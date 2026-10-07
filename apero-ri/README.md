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

## Search

The top-level **Search** page at `/search` is available from the home page,
top navigation, and sidebar, immediately after Astrometrics.

**Object / Observation** finds objects across accessible profiles by name
or alias, coordinates, observation date, exact RUN ID, header key, target
information, or spectrum information. Results are grouped by profile and
link to the data portal. Clicking a RUN ID in Manage RUN IDs opens the
RUN ID search automatically. Astrometrics retains its catalogue and target
resolution tools and links to Search for data-portal lookups.

**Documentation / Site** searches documentation for the selected version,
or documentation plus the labels and static content of permitted site
pages. Shared template content is included; live private records are not
indexed here. Words must all match; use double quotes for an exact phrase.
The documentation sidebar uses the same matching rules, while `/search`
provides full-page results with excerpts and more-results pagination.

## Manage RUN IDs

The Admin Portal's **Manage RUN IDs** page keeps one catalog per instrument
at `/admin_portal/run_ids`. It supports column filters, search, sorting,
pagination, inline PI/comment edits, and adding new RUN IDs. Save a row with
its disk icon; duplicate RUN IDs within an instrument are rejected.

Catalogs are stored in
`<ARI data directory>/apero-assets/run_ids/<instrument>.json`. Writes use
an exclusive filesystem lock and atomic replacement. Profile object tables
and existing science groups seed new records; rescanning never overwrites
saved metadata or removes IDs when profiles disappear. Empty PI/comment
edits are saved too.

Each catalog is also mirrored to
`<ARI data directory>/admin/run_ids/<instrument>_run_ids.yaml`, with RUN IDs
as top-level keys and `pi`/`comment` fields underneath. Existing catalogs
are mirrored the next time they are loaded. Asset JSON is authoritative;
the YAML copy can restore it if the JSON file is missing.

**Export CSV** downloads every saved row matching the current search,
column filters, and Missing PI checkbox, across all pages and in the current
sort order. Pending edits are excluded. CSV columns are `RUN ID`, `PI`, and
`COMMENT`; `RUN_ID` is also accepted on import.

**Import CSV** applies to the selected instrument and requires pending
edits to be saved or reverted first. Choose a duplicate policy:

- **Reject import**: reject the entire file if any ID already exists or
    occurs more than once in the CSV.
- **Keep existing / first CSV row**: preserve saved metadata and use the
    first occurrence of each new ID.
- **Overwrite / last CSV row**: replace PI and comment, including blanks,
    using the last occurrence of each ID.

Imports report added, updated, and skipped counts and list duplicate IDs.
Malformed CSV files are rejected without applying any imported records.
The file size limit is 5 MB.

Science groups use these catalogs for available RUN IDs and labels such as
`RUN_ID (PI) [Comment]`. Clicking a label opens the appropriate instrument
tab with that exact RUN ID filtered. The `manage.run_id.<INSTRUMENT>`
permission controls access, inherited by admins through instrument
moderator groups.

The RUN ID health banner reports how many saved records lack a PI name,
with a breakdown for each manageable instrument. The same check appears
on the Admin Portal cards and global Health Status page. Counts update
after saving a row or using Save All; blank or whitespace-only PI values
are considered missing.

The YAML mirror is included by the standard ARI backup policy under `admin`;
that policy excludes `apero-assets` by default. Keep either catalog copy in
your backups. Persistent storage does not itself protect against disk loss
or deletion of the data directory.


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

## Testing

Unit tests live in `apero-ri/tests`.

```bash
cd /scratch2/spirou/drs-bin/apero-drs-spirou-08XXX
PYTHONPATH="/scratch2/spirou/drs-bin/apero-drs-spirou-08XXX/apero-ri" \
python -m pytest -q apero-ri/tests
```

See `apero-ri/tests/README.md` for test scope and conventions.

### Use:

```python
import apero_ri
```


### import rules

can import any thing from:

aperocore
apero

