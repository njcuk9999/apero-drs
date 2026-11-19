---
card_label: APERO RI guide
card_icon: fa-solid fa-window-maximize
related:
  - api
  - monitor
  - glossary
---

# APERO RI guide

APERO RI is the web interface around APERO reduction data and operational
workflows. It does not replace APERO itself: ARI connects users to data,
monitoring results, queue dashboards, and administrative configuration while
APERO remains responsible for reducing observations.

## What APERO RI is for

ARI provides:

- searchable views of APERO-reduced objects and observations;
- astrometric review and target-resolution tools;
- monitor pages for checks, issues, schedules, and reduction health;
- an Admin Portal for profiles, storage, databases, tunnels, queues, users,
  permissions, and background tasks;
- search, saved pins, user preferences, API access, and download workflows;
- versioned documentation.

## How it works

An ARI deployment reads one or more APERO profile configurations. A profile
describes the paths, database, instrument, and permissions associated with a
reduction. ARI reads accessible profile data directly when it is local, or
through configured SSHFS mounts and SSH tunnels when it is remote.

The browser talks to the ARI server. The ARI server then accesses:

1. local profile data and generated ARI caches;
2. remote filesystems through SSHFS;
3. databases through a local forwarded SSH port;
4. remote APERO queue dashboards through another local forwarded port;
5. external services only where an administrator has explicitly configured
   them.

## Guide map

| Area | Purpose |
| --- | --- |
| [Documentation](documentation) | Find authored guides, generated APERO references, search, and editing workflows. |
| [Data Portal](data_portal) | Explore profiles, objects, observations, products, and downloads. |
| [Monitor Portal](monitor_portal) | Review checks, issues, schedules, and reduction state. |
| [Admin Portal](admin_portal/) | Configure the server and connections used by ARI. |
| [Astrometrics](astrometrics) | Resolve, review, and maintain target coordinates and aliases. |
| [Search](search) | Search objects, observations, properties, documents, and permitted site pages. |
| [Pins](pins) | Save and revisit important APERO RI resources. |
| [User Portal](user_portal) | Manage profile access, preferences, downloads, messages, and API access. |

## Shared concepts

### Profile

A profile is an APERO instrument/configuration identity. Profile access
controls much of what a user can see in the Data Portal, Monitor Portal,
Search, and APERO Queue pages.

### Local path

A local path is a path as seen by the ARI server process. When data is on
another machine, SSHFS makes a remote directory appear at a local path.

### SSH config host

ARI normally connects by an SSH host alias from `~/.ssh/config`. The alias is
important because it centralizes the real hostname, user, key, jump host,
host-key policy, and multiplexing settings.

### SSH tunnel

A tunnel listens on a port on the ARI server and forwards connections through
SSH to a remote host and port. The remote service does not need a public
listener because SSH carries the connection through its encrypted channel.

!!! note
    A successful SSH connection does not prove that a remote service is
    available. The remote service and the forwarded port must also be checked.

### Standard SSH and Alliance Duo

Standard SSH expects non-interactive authentication, usually by a public key
and, for some hosts, a directly reusable SSH session.

Alliance login nodes require a Duo keyboard-interactive approval for a new
authentication. Batch-mode SSHFS, database tunnels, and queue tunnels cannot
answer that approval. Alliance mode therefore creates a long-lived OpenSSH
`ControlMaster` first. Later commands reuse the authenticated master without
prompting for Duo again.
