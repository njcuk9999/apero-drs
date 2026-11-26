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

## Object file browser

The Data Portal object page offers spectrum presets for extracted 2D
`[e.fits]` (`DRS_POST_E`), telluric-corrected 2D `[t.fits]` (`DRS_POST_T`),
and telluric-corrected 1D `[s.fits]` (`DRS_POST_S`) products. These presets
select processed output files that pass QC or have no recorded QC; files with
no recorded QC still display `--` in the QC column. **Templates** selects
`TELLU_TEMP`, `TELLU_TEMP_S1DW`, and `TELLU_TEMP_S1DV` across file blocks.
For APERO 0.7 profiles, `out` files indexed as `DRS_PP` also match product
presets by their `e.fits`, `t.fits`, `s.fits`, `p.fits`, or `v.fits` suffix.
Column filters match without regard to case and preserve the entered text;
the filename filter also supports `*` as a wildcard.
Object-product refresh status belongs in the Admin Portal, not object pages.

## Portal collections

Portal landing pages and APERO profile collections can switch between card and
list layouts. Both layouts support alphabetical A–Z or Z–A ordering. ARI stores
the selected layout and sort direction per user and page in the existing
preferences file, alongside theme and timezone settings.

## Profile editor

On **Admin Portal → APERO Profiles**, changing a draft profile name updates
the default table suffix filters and clears selections that no longer match.
Custom filters are preserved. **Refresh from profile name** reloads database
tables and resets all table filters and selections to the current name.
Run **Test Table Names** again after changing the selection.

**Data Paths → Advanced** opens a replacement overlay, keeping these controls
off the settings page. Enter **Replace / With**, then **Preview changes** to
review before-and-after cards for each affected path. **Apply changes**
confirms the preview; Cancel, Escape, or clicking outside discards it.
Changing either input requires a new preview. Replacement is literal and an
empty replacement removes the matching text. Other profile settings and
disabled paths are untouched; save the profile to persist the edits and
rerun **Test Paths**.

**Create missing directories when testing** is off by default. When checked,
**Test Paths** creates missing directories, including parents, on the ARI
server (or its mounted storage), using the server process's permissions.
Creation failures appear beside the path. The optional trigger-log file is
only checked, never created.

## Async tasks

The Admin Portal's Async Tasks page shows all tasks in Active and Inactive
panels, with instrument and APERO-profile filters. Cards show the latest run
time. Profile-scoped tasks have independent identities, schedules, runtime
history, and activation settings. Saving a new enabled profile creates its
task entries; disabled and temporary profiles are not scheduled. Global and
instrument-scoped tasks remain shared at their respective scopes.

**Parallel defaults** controls NCORES, parallel backend, and process start
method across profiles. **Set by default** updates inheriting tasks and future
tasks while preserving explicit per-task overrides. **Update all tasks** also
clears those overrides. Enable **Override parallel defaults** in an individual
task's edit dialog to give that task its own settings.

Local-capable tasks look for completed precomputed output at
`PATH_OTHER/apero-ri/tasks/<instrument>/<APERO profile>/`. Each task has a
completion manifest containing its output paths and SHA-256 checksums. Missing,
incomplete, or modified results fall back to server computation. Successful
server and `apero_ri_task` runs publish their results to this same directory.
There is no per-profile sync mode or manually selected source path. The data
host and ARI server must expose the same profile's `PATH_OTHER` tree and use
matching instrument and profile names. Publishing requires write access.
Without `PATH_OTHER`, tasks run on the server without shared publication.
Filtered runs compute their selected subset without replacing shared results.
APERO checks manifests map outputs to the receiving profile's checks root.

`apero_ri_task` still accepts the runtime JSON payload through `--params-json`;
its `APERO_PROFILES` entries must include `paths.PATH_OTHER` to publish shared
outputs. Standalone runs compute fresh data rather than restoring old results.

### Processing sequence integration

APERO sequences can contain registered tools as well as science recipes.
`DrsRunSequence.add()` accepts their `DrsRecipe` definitions; the processing
generator explicitly distinguishes science recipes from tools. The standalone
ARI CLI is not itself an APERO-registered tool, so it cannot be inserted by
command name alone.

The `ARITASK` tool is registered as `apero_ri_task.py` and is appended to the
`full_seq`, `limited_seq`, `science_seq`, and `quick_seq` workflows for SPIROU,
NIRPS-HA, and NIRPS-HE. It builds the task profile in memory from the active
APERO paths and database settings and the bundled instrument preset. It does
not read or write a generated YAML or require a profile on the ARI server.
To use a custom profile, pass `--profile=/path/to/profile.yaml` to APERO's
`apero_ri_task.py`. The YAML must contain a single ARI profile mapping;
its filename stem identifies the profile for outputs. This override replaces
the generated profile and is never rewritten. The tool uses
`PATH_OTHER/apero-ri` as its local task-data root and writes precomputed results
to the shared profile directory.

APERO processing executes `ARITASK` after the regular run batch, even when the
regular batch uses multiple workers. Queue mode groups the final tool after the
preceding recipe groups. Install `apero-ri` in the reduction environment to
enable local task execution; otherwise the automatic step logs a warning and
skips. The RI web server does not need to be running.

`ARITASK` precomputes the object table, observation table, per-object queries,
QC statistics, and APERO checks for that profile. The matching RI scheduled
tasks restore these outputs from shared storage or compute them on the server
if no valid precomputed output is available. To pick up new tables immediately
instead of waiting for the schedule, run their tasks in **Admin Portal → Async
Tasks** for the matching profile.

The Queue tab combines all named queues, including instrument workers and
APERO checks. The first running task has the progress summary; additional
running tasks appear above pending tasks with their runtime status and
Stop/Log controls. Recent History combines completed runs across queues.

## Remote Diagnostics

**Admin Portal → Diagnostics** lets an administrator select accessible APERO
profiles and issue a separate read-only diagnostic key. Keys expire after
1–24 hours and can be revoked immediately. Each grant is independent of the
normal user API token; only its SHA-256 digest is stored, and the credential
is shown once. Reports recheck the issuer's current permissions and profile
access. Grant creation, revocation, and report access are audited.

The page displays a local command. Run it on the computer hosting your chat
session; enter the key at its hidden prompt rather than pasting it into chat
or shell history:

```bash
apero_ri_debug --host=https://ari.example --key \
        --profile=spirou_mini2_08xxx_fir --object=GL699 --logs
```

Without `--profile`, the client downloads one report per authorized profile.
Repeat `--profile` to select several. `--pid` narrows LogDatabase records;
`--no-database` skips live database reads. `--output` changes the default
`apero-diagnostics/` directory. The client saves owner-readable JSON files,
never the key. A privately supplied `APERO_RI_DEBUG_KEY` environment variable
is also accepted. `--key=VALUE` is supported but discouraged because shell
history and process listings may expose it.

Reports include package/runtime provenance, sanitized profile configuration,
bounded path inventories, cache metadata and object tables, task schedules,
manifest freshness and sampled checksums, live file-index product counts,
recent LogDatabase records, product-path accessibility, and sampled FITS
header/HDU metadata. Science arrays are not transferred. `--logs` adds up to
three redacted recipe log tails. Limits, skipped checks, and failures appear
explicitly in each report. Database queries are fixed read-only SELECTs with
connection/read and statement timeouts, currently for MySQL/MariaDB using
the `mysql+pymysql` driver. No API accepts arbitrary paths, SQL, or commands.

Enabled **APERO Queue Setup** definitions linked to the selected profile are
queried automatically through their existing SSH forwards. The queue host
contributes its actual `DRS_UCONFIG`, package versions, queue task status,
execution settings, process registry, generated-script monitor hooks,
bounded Slurm/queue logs, monitor stores/statistics, and LogDatabase records.
Remote profile/instrument identity must match the selected ARI profile;
mismatches are reported without exporting the other profile's details.
The diagnostic queue endpoint accepts only loopback socket peers. This is
a read-only request to the connected queue, not a code deployment or job
submission. Existing running reduction jobs are not modified.

Deployment requires updating `apero-core`, `apero-drs`, and `apero-ri` on the
relevant hosts, reinstalling the ARI package to register `apero_ri_debug`, and
restarting the ARI server and queue GUI to load the new endpoints. Existing
queue monitor functionality is unchanged. Before deploying to production,
run the diagnostics tests and collect a report against your own profile.

Direct client access supports HTTP or HTTPS and requires network reachability.
HTTP transmits diagnostic keys and reports unencrypted; anyone able to observe
the connection can reuse a key until it expires or is revoked. HTTPS or an
approved SSH tunnel is recommended, particularly on untrusted networks. An
SSH tunnel can be accessed using a local URL such as `http://127.0.0.1:15000`.
Redirects, URL credentials, and disabled certificate verification are not
supported. A key cannot bypass a firewall/VPN or a separate front-end
password. Do not expose the unauthenticated queue GUI publicly.

Read-only token endpoints:

- `GET /api/diagnostics/profiles` lists the currently authorized profiles.
- `GET /api/diagnostics/report` accepts `instrument`, `profile_id`, optional
    `objname`, `pid`, `logs=1`, and `database=0`.
- `GET /api/diagnostics/export` returns the same report as gzipped JSON.

Supply the key only in `Authorization: Bearer ...`. These diagnostic keys do
not authorize normal ARI endpoints, queue actions, file downloads, or shell
access. Exports are credential-redacted but contain scientific metadata,
hostnames, usernames, and paths: share only with trusted collaborators, do
not commit them, and revoke the grant when investigation finishes.

## Search

The top-level **Search** page at `/search` is available from the home page,
top navigation, and sidebar, immediately after Astrometrics.

**Object / Observation** finds objects across accessible profiles by name
or alias, coordinates, observation date, RUN ID prefix, header key, target
information, or spectrum information. Results are grouped by profile and
link to the data portal. Clicking a RUN ID in Manage RUN IDs opens the
RUN ID search automatically. Astrometrics retains its catalogue and target
resolution tools and links to Search for data-portal lookups.

RUN ID searches match accessible IDs starting with the supplied text, so
`112.` finds observations from accessible `112.*` programs. Header, target,
and spectrum searches use **Select property** to open a scrollable key
picker with text and instrument filters. Selecting an instrument also
scopes that property search. Each mode includes a description and examples
from the instrument configuration files.

Result cards show the canonical object name followed by the actual matched
data, for example `OBJECT (run id = 112.A)` or `OBJECT (EXPTIME = 600)`.
Multiple matching values are retained, and each profile shows its object
count. Property keys are cached under `admin/search_index`; the enabled
global **Search Indexing** async task refreshes them every 24 hours by
default. Missing indexes build in the background and the picker retries;
existing keys remain available during stale-index refreshes.

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

At server startup, ARI makes one background attempt to reconnect missing
SSH tunnels for enabled queues in **Admin Portal → APERO Queue Setup**.
Disabled queues and tunnels already listening are left alone. Tunnels that
require a password or Duo still need **Interactive Auth**, and the remote
`apero_queue.py gui` dashboard must already be running. Failed attempts
are logged without delaying server startup.

Recommended setup is a reverse proxy (nginx/Apache) terminating HTTPS in
front of the app. The following environment variables configure the app
for that topology:

| Variable | Meaning | Default |
|----------|---------|---------|
| `ARI_PROXY_COUNT` | Number of trusted reverse proxies in front of the app (e.g. `1` for a single nginx). Enables `X-Forwarded-*` handling so client IPs, rate limits, and HTTPS detection are correct. | `0` (off) |
| `ARI_HTTPS` | Set to `1` when the site is served over HTTPS. Marks session cookies `Secure` and enables HSTS. | off |
| `ARI_MAX_CONTENT_MB` | Maximum request body size in MB. | `128` |
| `ARI_GEOIP_DB` | Optional override for the GeoLite2 City `.mmdb` path installed by setup. Only country and region are retained; client addresses are used for lookup in memory. | ARI cache database |

GeoIP2 is installed with ARI. To enable country and region summaries on any
existing installation, open **Admin Portal → Geo locate users** in
the running ARI site; no setup rerun or server restart is needed. Create a free
MaxMind GeoLite account, accept its End User License Agreement, then open
**Manage License Keys** and create a license key. The page links to each step.
Enter the account ID and key in ARI; ARI downloads and validates the latest
GeoLite2 City database. Credentials are used only for the download and are not
saved. The database is stored in
`<ARI data directory>/cache/geoip/GeoLite2-City.mmdb`.

The **Server and network** tab saves the number of trusted forwarding proxies
for the next ARI restart. Use zero for direct connections or ordinary router
port forwarding, and typically one for a single Caddy, nginx, Apache, or NAS
HTTP reverse proxy that supplies `X-Forwarded-For`. For chains, count the
trusted proxies that correctly forward headers, not routers. A saved value
overrides `ARI_PROXY_COUNT`; if no value has been saved, the environment
variable continues to work. A private or loopback client address cannot be
geolocated. If proxy trust is enabled, firewall the ARI port so untrusted
clients cannot bypass the proxy and forge forwarded headers. HTTPS termination,
`ARI_HTTPS` (secure cookies and HSTS), and `ARI_GEOIP_DB` are separate settings.

MaxMind requires GeoLite databases to be kept current. Return to the GeoLite
Location Database page to update the database. The database is not bundled
because its license and update terms are separate. Without a local database,
activity is still counted and locations are reported as unknown.


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
