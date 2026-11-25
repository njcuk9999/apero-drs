# ARI Agent Guidance

Follow the monorepo [AGENTS.md](../AGENTS.md) and the ARI conventions in
[CLAUDE.md](CLAUDE.md).

## Remote Diagnostics

When debugging a running ARI instance or a linked remote APERO queue, prefer
observed diagnostic reports over assumptions based on this checkout. Ask the
user for the server URL, affected profile ID, and object/PID when relevant.
Ask them to generate a profile-scoped key in **Admin Portal → Diagnostics**
and run the displayed `apero_ri_debug` command locally. They do not need to
log into the remote machine or manually download files.

```bash
apero_ri_debug --host=https://ari.example --key \
    --profile=spirou_mini2_08xxx_fir --object=GL699 --logs
```

- The bare `--key` option uses a hidden terminal prompt. Never ask the user
  to paste a key into chat, put it in a URL, or send it through a tool that
  exposes secrets to the model. `APERO_RI_DEBUG_KEY` is an alternative when
  supplied privately by the user. Never print that environment variable.
- Keys last at most 24 hours, can be revoked immediately, and permit only
  read-only diagnostic reports for the profiles explicitly selected.
- HTTPS is required except for a loopback SSH tunnel. A token does not
  bypass network reachability, VPN rules, or front-end authentication. Do
  not disable TLS verification or recommend exposing the queue GUI.
- If the user has privately configured `APERO_RI_DEBUG_KEY` in the terminal
  available to this session and authorized collection, run the CLI directly
  using the non-secret URL and filters. Otherwise let the user enter the key
  directly in the terminal, then continue once the command completes.
- Reports are saved under `apero-diagnostics/` by default, one JSON file per
  authorized profile, with mode `0600`. Inspect these local files using
  normal file tools. `--output` chooses another local directory.
- Use `--object`, `--pid`, and repeated `--profile` filters to narrow a new
  collection. Use `--logs` for bounded redacted recipe log tails;
  `--no-database` avoids live database queries. Keys are never saved by the
  client. Do not add diagnostic exports to git.
- Reports identify runtime versions, cache/manifests, data paths, database
  products/logs, FITS header samples, and matching connected queue-host
  evidence. Queue collection uses existing ARI SSH forwards and performs
  no queue actions, service restarts, or remote command injection.
- Check `runtime`, `profile_id`, `drs_uconfig` in queue reports, timestamps,
  scope, truncation markers, and section errors before drawing conclusions.
  Missing evidence is not proof that a product or recipe is absent.
- To diagnose invisible products, compare live indexed counts, published
  manifests, RI cached tables, RUN_ID/security fields, and product-path
  access. LogDatabase RAM/CPU readings are host snapshots, not process peaks.

See [README.md](README.md#remote-diagnostics) for deployment, API endpoints,
and connection prerequisites. Focused verification:

```bash
PYTHONPATH=apero-core:apero-drs:apero-ri python -m pytest -q \
    apero-ri/tests/test_diagnostics.py apero-drs/tests/test_queue_stats.py
```