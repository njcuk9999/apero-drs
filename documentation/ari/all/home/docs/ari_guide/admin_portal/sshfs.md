---
card_label: SSHFS management
card_icon: fa-solid fa-hard-drive
---

# SSHFS management

## What SSHFS does

SSHFS mounts one remote directory onto a directory on the ARI server. APERO RI
then reads that mount through an ordinary local path. SSHFS uses the SFTP
subsystem carried by SSH; it is not a separate network file protocol.

Use SSHFS when an APERO profile's files exist on another host, but ARI needs
to read them as local files.

## What ARI manages

ARI stores:

- a mount name;
- a connection method or SSH alias;
- the remote path;
- the local mount point;
- the selected private key;
- the network mode;
- mount status and the last command or diagnostic log.

Mount execution is command-only: ARI prepares an exact command for an
administrator to run. It does not silently mount storage in the web process.
This keeps FUSE mounts, permissions, and terminal authentication under the
administrator's control.

## Standard SSH mode

Standard mode is the default and preserves the existing direct-host or SSH
config-alias workflows.

### Direct host mode

ARI constructs a target such as:

```text
user@host:/remote/path
```

The selected private key, host-key policy, keepalive settings, and
`BatchMode=yes` are included in the SSHFS command. This mode assumes a
non-interactive key login.

### SSH config host mode

Instead of `user@host`, ARI uses a host alias:

```text
my-data-host:/remote/path
```

The alias can contain `HostName`, `User`, `IdentityFile`, `ProxyJump`, or
other OpenSSH options. This is preferred when the connection has a jump host,
unusual port, or several related options.

## Why the pre-setup steps matter

1. The generated SSH key pair separates the private credential on ARI from
   the public authorization installed or registered remotely.
2. The server-side `authorized_keys`, or the equivalent cluster key manager,
   grants that specific public key.
3. The private key is stored with restricted permissions so SSHFS can use it
   without exposing it to web users.
4. The remote directory must already exist and be readable. SSHFS cannot turn
   a nonexistent or unauthorized remote path into a valid profile.
5. The local mount point must be an empty directory. Reusing a directory
   containing local files can hide those files beneath the mount.

## Alliance Duo mode

Alliance login nodes can require public-key authentication followed by a
keyboard-interactive Duo approval. SSHFS itself cannot answer that prompt,
especially when it uses `BatchMode=yes`.

Alliance mode solves this with OpenSSH multiplexing:

```sshconfig
Host a_fir
    HostName fir.alliancecan.ca
    User ACCOUNT
    IdentityFile /path/to/stored/key
    IdentitiesOnly yes
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 12h
    ServerAliveInterval 30
    ServerAliveCountMax 6
    StrictHostKeyChecking accept-new
```

### Initialization

The administrator checks for the master:

```bash
ssh -O check a_fir
```

If it is absent, initialization is interactive:

```bash
ssh -fN a_fir
```

Approve Duo once. `-N` starts no remote command; it creates the authenticated
master. `-f` returns control to the shell after authentication.

### Mounting

After the master exists, SSHFS reuses its authenticated transport:

```bash
sshfs -o reconnect -o BatchMode=yes \
  -o ServerAliveInterval=30 -o ServerAliveCountMax=6 \
  a_fir:/remote/path /local/mount
```

`BatchMode=yes` is safe only at this stage because no new authentication is
needed over the active master. The mount keeps channels active; without it,
`ControlPersist 12h` means the master may remain for up to 12 hours after the
last channel closes.

### Why stale recovery is included

An ungraceful network loss can leave both a stale ControlMaster socket and a
wedged FUSE mount. Alliance mount commands therefore:

1. test the master;
2. attempt `ssh -O exit` if the test fails;
3. remove the matching stale socket;
4. establish a fresh master, which may prompt for Duo;
5. mount only if the local mount point is not already mounted.

For a wedged mount, `fusermount -uz` or `umount -l` detaches the stale FUSE
endpoint without relying on the unavailable remote filesystem.

## Mount Status interpretation

| State | Meaning | Action |
| --- | --- | --- |
| Not mounted | The mount point is not a live FUSE mount. | Copy and run the generated mount commands. |
| Mounted | `mountpoint` succeeds and the directory responds. | No action. |
| Mounted, stale | The mount exists but access/authentication has stopped. | Unmount or repair, then for Alliance re-establish Duo. |
| Unknown/timeout | Status checks could not finish promptly. | Check SSH/network health and use the stale-mount recovery. |

## Troubleshooting checklist

1. Run `ssh alias hostname` and confirm the expected remote machine.
2. For Alliance, run `ssh -O check alias`.
3. Test the remote directory through `ssh alias 'ls -ld /remote/path'`.
4. Check the local mount with `mountpoint path`.
5. Confirm that the APERO profile points to the local mount path, not the
   remote path.
6. Check that the ARI process has read permission on the mounted files.

!!! warning
    Initial Alliance authentication always requires human Duo approval unless
    Alliance support has explicitly granted Duo-exempt automation access.
