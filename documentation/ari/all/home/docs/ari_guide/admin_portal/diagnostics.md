---
card_label: Diagnostics
card_icon: fa-solid fa-stethoscope
---

# Diagnostics

Diagnostics gathers read-only evidence about an APERO profile and its linked
queue. Use it to investigate missing products, stale or slow object pages,
processing failures, and missing queue statistics. It does not rerun recipes,
refresh caches, execute arbitrary commands, or submit or change queue jobs.

## Profiles

The checkboxes under **Profiles** choose which profiles a newly generated key
may access. An administrator can select only profiles they currently have
access to. The **Report** section has its own separate selector: choosing a
checkbox does not collect a report or determine the report selector's value.

## Access Grants

Generate a key when a trusted collaborator needs to fetch diagnostics from
your ARI server without logging in as you. A key is not needed to collect or
export a report directly from this admin page.

1. Select the profile or profiles to share, add an optional label, and set a
   lifetime between 1 and 24 hours.
2. Select **Generate Key**. The key is displayed only once. The command shown
   beside it fetches reports on the collaborator's computer; the bare
   `--key` option prompts for the key without displaying it.
3. Give the collaborator the server URL and the key through a private channel.
   Do not paste the key into a chat, a URL, or shell history.
4. Revoke the grant from the table when the investigation is finished. Expiry,
   revocation, current issuer permissions, and current profile access are
   checked on requests. Issue and revoke actions and report access are audited.

Keys are separate from regular ARI API tokens. They allow only the diagnostic
read endpoints and the selected profiles, not arbitrary ARI endpoints, file
downloads, shell commands, or queue actions. Each key's hash is stored on the
server, not the key itself. Anyone with a valid key can use it until it expires
or is revoked.

HTTP is supported, including on local networks, but sends the key and reports
unencrypted. Anyone observing the connection can read the report and reuse the
key. HTTPS or an SSH tunnel is recommended on untrusted networks. A key does
not bypass a firewall, VPN, or an independent front-end password.

## Report Options

- **Profile** selects the one profile to inspect on this page. **Collect**
  shows progress by completed collection stages and saves the report privately.
  Each stage can take a different amount of time, so the percentage is not
  an estimate of elapsed time. **Export** downloads the completed report
  without collecting it again, as gzipped JSON when supported by the browser
  or plain JSON otherwise. Collect again after changing the report options.
  **Copy Report** copies the complete JSON to the clipboard instead of
  displaying it on the page.
  Collection continues on the ARI server if you refresh or leave this page;
  returning to the page restores your most recent accessible job and result.
  A server restart interrupts an active collection, which must be started
  again. Completed reports are accessible for 24 hours to their owner while
  that owner retains access to the profile. The 24 hours start when collection
  completes; the hourly **Diagnostics Cleanup** task removes expired files.
  Access stops at expiry even if cleanup is disabled or has not run yet. Use
  **Saved Reports** to reopen an earlier completed report, even after a later
  collection fails. Up to 100 of the newest accessible reports are listed.
  The current stage shows elapsed seconds and, for manifests, the task name;
  a slow filesystem or queue connection can leave one stage active for a
  long time without changing the percentage.
- After collection completes, **Delete Report** removes the saved snapshot and
  revokes any link. **Create Share Link** produces a copyable public URL for
  this report only. Anyone with the URL can copy or download its contents
  without an ARI login, so share it only with trusted people. The link expires
  with the report, can be revoked independently, and creating a new link
  invalidates the previous one. It also stops working if the owner loses
  diagnostics permission or access to the profile.
- The share capability is carried in the URL fragment and is not sent in the
  initial page request or normal server access logs. The viewer sends it in
  an authorization header. HTTP still exposes the capability and report to
  network observers; use HTTPS or an SSH tunnel on untrusted networks.
- **Object** is an optional exact APERO object name, for example `GL699`.
  When supplied, the report inspects that object's cached tables and, when
  live database queries succeed, indexed product examples, product paths,
  and up to three FITS header/HDU samples. When blank, product counts are
  grouped across the profile and no per-object tables, product examples, or
  FITS samples are gathered. It does not filter the recipe log query.
- **Recipe PID** is an optional exact APERO recipe process identifier, not
  an object name or a queue task ID. It filters the LogDatabase recipe records;
  blank returns up to 100 of the most recent records. It does not filter the
  file-index products or the linked queue's own diagnostics.
- **Include Log Tails** adds the last 64 KiB of up to three recipe log files
  selected from the returned database records. It requires **Live Database**,
  log paths recorded in those records, and accessible files within the
  configured log root. Missing or inaccessible files are reported. This
  option does not control the linked queue's own bounded log excerpts.
- **Live Database** runs read-only queries for the file-index and log-table
  schemas, product counts, and recipe records. It requires an accessible
  MySQL/MariaDB profile using `mysql+pymysql`. Turn it off to avoid these
  queries; indexed product examples, FITS samples, and recipe log tails are
  then unavailable. Other cache, path, task, and linked queue checks still run.
  A linked queue may independently query its own LogDatabase.

## Report Contents

The report includes the ARI host runtime and installed package information,
redacted profile settings, data-path metadata and bounded directory listings,
cached object/observation tables, task schedules, and precomputed manifest
freshness with a small sample of file checksums. Object-specific tables and
products are included only when requested. FITS headers and extension metadata
are sampled; science arrays are not transferred.

With live queries enabled, product counts group indexed files by block, output,
fiber, and type, including a count of missing RUN IDs. Recipe records include
start/end times, status, errors, and start/end host RAM and CPU snapshots.
Those resource snapshots are **not** per-process peaks or a continuous
performance history. Results are bounded; inspect error and truncation markers
before treating missing data as evidence that a file or task does not exist.

Enabled queue definitions linked to the selected profile are queried through
their existing ARI SSH forwards. A matching queue can provide its active
`DRS_UCONFIG`, runtime, queue status, process and script metadata, monitor
stores and statistics, recent LogDatabase records, and bounded queue log
excerpts. A profile/instrument mismatch is reported instead of exporting the
other profile's queue details. The queue diagnostic endpoint remains local to
the queue host and its SSH forward; do not expose the queue GUI publicly.

## Slow Requests

In browser developer tools, open **Network**, reload the affected page, and
select a slow document or API request. Compare its total duration with the
`Server-Timing: ari;dur=...` response header, measured in milliseconds. ARI
measures from the start of its request handler until response headers are
prepared; it does not include time waiting for a worker, network/proxy delays,
or the full body of a streamed response. A large ARI duration points to work
inside ARI, while a much larger browser duration can indicate queuing, network,
proxy or body-transfer time. Compare multiple requests rather than assuming a
single delay identifies the cause.

Reports are credential-redacted but may contain scientific metadata, file
paths, hostnames, usernames, FITS headers, and log excerpts. Review and share
them only with trusted collaborators. Redaction cannot guarantee removal of
every secret in free text. Treat reports as sensitive and do not commit them.

## Local Collection

Install the updated `apero_ri` package on the collaborator's machine. After the
administrator deploys the updated ARI, APERO and apero-core packages on the
relevant hosts and restarts ARI and the queue GUI, run the command displayed
on the diagnostics page, optionally adding filters:

```bash
apero_ri_debug --host=http://ari.example:5000 --key \
    --profile=spirou_mini2_08xxx_fir --object=GL699 --logs
```

Enter the key at the hidden prompt. Without `--profile`, one report is saved
for each authorized profile; repeat it to select several. `--pid` selects a
recipe PID, `--no-database` disables live ARI database queries, and `--output`
changes the output directory. Reports are saved as owner-readable JSON in
`apero-diagnostics/` by default. See the [ARI README](https://github.com/njcuk9999/apero-drs)
for deployment and API details.