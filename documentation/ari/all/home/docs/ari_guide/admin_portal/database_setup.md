---
card_label: Database setup
card_icon: fa-solid fa-database
---

# Database setup

## What the database connection is for

APERO profiles use databases for calibration, telluric, index, and log data.
Many database servers are private and cannot be contacted directly from the
ARI host. An SSH local forward provides a secure route.

ARI connects to:

```text
127.0.0.1:LOCAL_PORT
```

and SSH forwards that connection to:

```text
REMOTE_DATABASE_HOST:REMOTE_DATABASE_PORT
```

from the SSH login host.

## Why an SSH config alias is required

The alias keeps the user, real login hostname, identity key, jump host, and
connection options out of ARI's database definition. It also gives OpenSSH a
stable name for multiplexing and makes manual tests match ARI.

## Standard SSH mode

ARI can start:

```bash
ssh -f -N -M -S CONTROL_SOCKET \
  -o BatchMode=yes \
  -o ExitOnForwardFailure=yes \
  -L LOCAL_PORT:DB_HOST:DB_PORT SSH_ALIAS
```

- `-f -N` creates a background forwarding-only connection.
- `-L` defines the local and remote endpoints.
- `ExitOnForwardFailure=yes` prevents a broken forward from reporting
  success.
- `BatchMode=yes` makes unattended setup fail clearly instead of waiting for
  a password.
- `-S` identifies ARI's control socket for status, reuse, and cleanup.

Simple/docs mode omits ARI's separate control socket and is useful when the
connection is intentionally managed outside ARI or must reuse an existing SSH
configuration.

## Alliance Duo mode

For an Alliance login, initialize and approve a reusable master first:

```bash
ssh -O check a_fir
ssh -fN a_fir
```

After Duo succeeds, a new forwarding channel can reuse that master:

```bash
ssh -f -N -o ExitOnForwardFailure=yes \
  -L LOCAL_PORT:DB_HOST:DB_PORT a_fir
```

Use simple mode for this workflow. APERO-managed mode creates a separate
control socket and can attempt a fresh non-interactive SSH login, which cannot
answer Duo.

## Why the database host is relative to the cluster

The database hostname in the forward is resolved on the SSH server, not on
the ARI server. For a private cluster hostname, the correct setting is often
the internal DNS name used by the login/processing environment. `localhost`
means the SSH login host itself, not the ARI browser.

## Validation sequence

1. Verify the login alias:

   ```bash
   ssh SSH_ALIAS hostname
   ```

2. From that login environment, verify DNS:

   ```bash
   ssh SSH_ALIAS getent hosts DB_HOST
   ```

3. Start or verify the ARI tunnel.
4. Confirm the local listener and test the database credentials through the
   profile test action.
5. Check the expected database tables.

## Common failures

| Failure | Likely cause |
| --- | --- |
| Interactive authentication is required | A new Duo/password login is needed before batch-mode SSH. |
| Local port did not become ready | SSH failed, the local port is occupied, or forwarding failed remotely. |
| Local port opens but database test fails | The forwarded host/port, credentials, TLS, or database name is wrong. |
| Works manually but not in ARI | ARI may be using a different `HOME`, `~/.ssh/config`, or UNIX permissions/context. |
| Connection stops after hours | The master was not kept alive, the network dropped, or the login session expired. |

## Security and lifecycle

- Use a unique local port per definition.
- Keep the database credential in the APERO/ARI secret configuration, never
  in the SSH host alias.
- Close stale ARI tunnels through the setup page.
- Do not expose the forwarded local port on a public network interface.
