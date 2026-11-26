---
card_label: Admin Portal
card_icon: fa-solid fa-screwdriver-wrench
related:
  - ari_guide
---

# Admin Portal

The Admin Portal configures the infrastructure ARI uses. A profile can be
correctly installed on a cluster and still be unusable in ARI if its
filesystem, database, or queue connection is not correctly exposed to the ARI
server.

## Connection model

Most remote integrations follow the same sequence:

1. establish an SSH identity and host alias;
2. authenticate and validate the remote resource;
3. create a stable local representation on the ARI server;
4. test the final HTTP, filesystem, database, or forwarded-port behavior;
5. save the definition and monitor it.

The local representation is either:

- an SSHFS mount point for a remote directory;
- a localhost port forwarding to a database;
- a localhost port forwarding to an APERO queue dashboard.

## Detailed setup guides

| Guide | Admin page |
| --- | --- |
| [SSHFS management](sshfs) | Expose remote APERO directories as local paths. |
| [Database setup](database_setup) | Reach a remote MySQL/MariaDB service through SSH. |
| [APERO Queue setup](queue_setup) | Reach and monitor a remote APERO queue GUI. |
| [Diagnostics](diagnostics) | Collect read-only reports and grant temporary profile-scoped access. |

Additional Admin Portal page guides are placeholders for later expansion.
