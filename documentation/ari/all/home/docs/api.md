---
card_label: ARI API (Application Programming Interface)
card_icon: fa-solid fa-plug-circle-bolt
---

# APERO RI API – User Guide

Access APERO data programmatically using the **ari_api** Python client
library.  All examples use the profile `INSTRUMENT_offline` and the
target `GL699` — replace these with values appropriate to your setup.

---

## 1. Installation

Install the `apero_ri` package with the `api` extra:

```bash
git clone git@github.com:njcuk9999/apero-drs.git -b 0.8.running
cd apero-drs
pip install -U -e ./apero-ri[api]
```

This pulls in the lightweight client only (no apero-drs).

---

## 2. Getting Your API Token

1. Log in to the ARI web interface.
2. Navigate to **User Portal → API Access**.
3. Click **Generate Token** and copy the token immediately — it will not
   be shown again.

---

## 3. Configuration

Configure the client once per machine.  The client reads settings from
`<ARI_DIR>/api_config.json`, where `ARI_DIR` is the ARI data directory in use
for the current runtime (usually `~/.ari` unless you set `ARI_DIR` explicitly).

The two values are:

- `server`: the base URL of the ARI instance, for example
  `https://your-apero-ri-server.example.com`
- `token`: the API token generated in the ARI web UI at
  User Portal → API Access

You can set them in Python:

```python
from apero_ri import ari_api

ari_api.configure(
    server='https://your-apero-ri-server.example.com',
    token='paste-your-64-char-token-here',
)
```

If the check is running on another machine, the same file must exist there
with the same values.

---

## 4. Listing Available Profiles

A *profile* represents a specific APERO reduction configuration
(instrument + settings).

```python
from apero_ri import ari_api

profiles = ari_api.list_profiles()
print(profiles)
# ['spirou_xxs_08_cook_home', 'nirps_ha_online', ...]
```

For more detail (instrument, label):

```python
detailed = ari_api.list_profiles_detailed()
for p in detailed:
    print(f"{p['profile_id']}  ({p['instrument']})  – {p['label']}")
```

---

## 5. Working With a Profile

```python
profile = ari_api.AperoProfile('INSTRUMENT_offline')
```

### Object Table

The object table lists every target in the profile with summary counts.

```python
obj_table = profile.get_object_table()           # pandas DataFrame
obj_table = profile.get_object_table(fmt='astropy')   # astropy Table
obj_table = profile.get_object_table(fmt='dict')      # list of dicts

print(obj_table.head())
```

### Observation Table

One row per observation — timestamps, seeing, airmass, etc.

```python
obs_table = profile.get_observation_table()
print(f"Total observations: {len(obs_table)}")
print(obs_table.columns.tolist())
```

### List Object Names

```python
names = profile.list_objects()
print(names[:10])
```

---

## 6. Working With a Single Object

```python
obj = profile.get_object('GL699')
```

### Target Info

Returns a table of summary statistics (sections, keys, values):

```python
info = obj.target_info()                    # pandas DataFrame
info = obj.target_info(fmt='astropy')       # astropy Table
print(info)
```

### List Files

```python
files = obj.list_files()                    # list of dicts
files = obj.list_files(preset='all')        # different preset

for f in files[:5]:
    print(f.get('FILENAME'), f.get('BLOCK_KIND'))
```

---

## 7. File Count & Downloading

### Preview the count

Use `get_count()` to check how many files match **before** downloading.
It accepts the same filter arguments as `get_data()`:

```python
print(obj.get_count())                            # all default files
print(obj.get_count(KW_DPRTYPE='OBJ_FP'))         # only OBJ_FP files
print(obj.get_count(preset='all'))                 # different preset
```

### Download files

The `get_data()` method handles the full download workflow
(basket + compile + download + extract) in one call:

```python
downloaded = obj.get_data('/tmp/GL699_data')
print(f"Downloaded {len(downloaded)} files")
```

### Filter by column values

Only download files matching specific criteria:

```python
downloaded = obj.get_data(
    '/tmp/GL699_fp',
    KW_DPRTYPE='OBJ_FP',                  # column filter
)
```

### Options

These keyword arguments are shared by both `get_count()` and
`get_data()` (except where noted):

| Parameter   | Default   | Description |
|-------------|-----------|-------------|
| `localdir`  | *(required)* | Local directory for downloaded files (`get_data` only) |
| `preset`    | `'default'` | File filter preset |
| `overwrite` | `False`   | Re-download existing files (`get_data` only) |
| `**filters` | —         | Column-name=value filters on the file list |

---

## 8. Putting It All Together

```python
from apero_ri import ari_api

# First-time only:
# ari_api.configure(server='https://...', token='...')

# List profiles
for name in ari_api.list_profiles():
    print(name)

# Work with a profile
profile = ari_api.AperoProfile('INSTRUMENT_offline')
obj_table = profile.get_object_table()
print(obj_table[['OBJNAME', 'DISPNAME']].head(10))

# Inspect a single target
obj = profile.get_object('GL699')
info = obj.target_info()
print(info)

# Download reduced spectra
downloaded = obj.get_data(
    '/tmp/GL699_reduced',
    preset='default',
)
print(f"Saved {len(downloaded)} files")
```

---

## 9. Output Formats

All table-returning methods accept an `fmt` parameter:

| Value       | Returns                   | Requires         |
|-------------|---------------------------|------------------|
| `'pandas'`  | `pandas.DataFrame`        | pandas           |
| `'astropy'` | `astropy.table.Table`     | astropy          |
| `'dict'`    | `list[dict]`              | *(nothing extra)* |

---

## 10. API Token Management

- **Generate:** User Portal → API Access → *Generate Token*
- **Revoke:** User Portal → API Access → *Revoke Token*
- Each user may have **one** active token at a time.
- Generating a new token automatically revokes the old one.

---

## 11. Rate Limits & Quotas

- Download endpoints may enforce a per-user rate limit (configurable by
  the admin; default: 2 seconds between requests).
- Compiled archives are subject to a per-user storage quota (default:
  5 GB).  Remove old compilations to free space.

---

## API Endpoint Reference

For advanced usage or non-Python clients, the raw HTTP endpoints are
listed here.  All endpoints accept `Authorization: Bearer <token>` for
authentication.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/data-portal/profiles` | GET | List accessible profiles |
| `/api/data-portal/object-table?profile_id=` | GET | Object table |
| `/api/data-portal/obs-table?profile_id=` | GET | Observation table |
| `/api/data-portal/object-page?profile_id=&objname=` | GET | Object details |