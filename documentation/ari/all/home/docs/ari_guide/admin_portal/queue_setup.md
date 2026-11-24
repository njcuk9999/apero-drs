---
card_label: APERO Queue setup
card_icon: fa-solid fa-list-check
---

# APERO Queue setup

## What it does

`apero_queue.py gui` runs an APERO processing dashboard on a remote machine.
ARI opens that dashboard through an SSH local forward and proxies it in the
Monitor Portal. This lets authorized users inspect and, where permitted,
control queue jobs without exposing the queue HTTP server publicly.

## Why the queue needs a special connection

The queue GUI binds to loopback on the remote machine:

```text
127.0.0.1:8090
```

Loopback exists separately on every login node. A forwarding session connected
to `login1` cannot reach a GUI listening on `login3`, even though both are part
of the same cluster and the same public SSH hostname.

Therefore the SSH connection and the queue process must use the same login
node.

## Standard SSH mode

For a host alias that consistently reaches one machine, start the GUI on that
machine and use:

```bash
ssh SSH_ALIAS
apero_queue.py gui --headless --port 8090
```

Then establish the local forward:

```bash
ssh -f -N -o ExitOnForwardFailure=yes \
  -L LOCAL_PORT:127.0.0.1:8090 SSH_ALIAS
```

Verify from the ARI host:

```bash
curl -s http://127.0.0.1:LOCAL_PORT/api/state
```

## Alliance Duo mode

Alliance public login names may route to different login nodes. Alliance mode
uses the existing Duo-authenticated ControlMaster as the node-selection point.

1. Establish or verify the master:

   ```bash
   ssh -O check a_fir 2>/dev/null || ssh -fN a_fir
   ```

2. Open a shell through that exact master:

   ```bash
   ssh a_fir
   ```

3. Record the selected node and prepare the APERO environment:

   ```bash
   hostname
   # configured pre-GUI commands
   module load ...
   source ...
   ```

4. Start the queue in that same shell:

   ```bash
   apero_queue.py gui --headless --port 8090
   ```

5. Open a **new local terminal on the ARI host** for checks and for the
   forwarding command. Do not type them into the terminal where the queue GUI
   is running; that process owns the remote interactive shell.

6. All later `ssh a_fir` commands multiplex through the same master and
   therefore reach the same login node until that master is replaced.

Copy Command labels each block by terminal:

- Terminal 1 initializes the Alliance master.
- Terminal 2 opens the remote shell, runs the optional preparation commands,
  and starts the queue.
- Terminal 3 remains local and checks the remote node and HTTP endpoint.
- Terminal 4 remains local and starts either a foreground or background
  tunnel. Choose one, not both.
- Final HTTP verification is run from any local ARI-host terminal.

Do not start the queue from a separate `ssh fir.alliancecan.ca` session.
That may land on another login node and create the symptom “tunnel active,
dashboard not answering.”

## Pre-GUI commands

The queue definition's **Commands before apero_queue GUI** field stores one
shell command per line. Copy Command places them after `hostname` and before
the GUI launch.

Use this field for commands required to activate the queue environment, for
example:

```bash
module load python/3.12
source /project/.../environment.sh
cd /project/.../working-directory
```

Commands are copied for the administrator to run; ARI does not execute them
automatically on the cluster. This avoids silently activating the wrong
profile or performing privileged setup remotely.

## Tunnel modes

### APERO-managed

ARI owns an explicit control socket and uses it to start, inspect, and close
the tunnel. This is appropriate for ordinary non-interactive SSH access.

### Simple / docs-style

ARI uses the host's regular OpenSSH configuration and does not create a
separate control socket. Alliance mode automatically selects this behavior so
the tunnel can reuse the Duo-authenticated ControlMaster.

## The queue supervisor and Retry Dashboard

Modern APERO queue GUI startup has two processes:

- a stable public supervisor on the configured port, such as 8090;
- a private worker on an automatically selected loopback port.

The supervisor proxies HTTP requests to the worker. If the worker is dead or
hung, the SSH forward can still be active and the public port can still be
open.

**Retry Dashboard** sends:

```http
POST /api/shutdown
Content-Type: application/json

{"restart":true}
```

through the existing tunnel. The supervisor replaces only its worker. It does
not close SSH, reset queue state, or stop active queue tasks.

Retry cannot fix:

- a missing SSH tunnel;
- a queue GUI started on a different login node;
- a process that is not running at all;
- an incorrect remote port;
- a remote supervisor that is itself unreachable.

## Slurm information in the Processes tab

When `squeue` is available to the account running `apero_queue.py`, the
Processes tab adds a **Slurm jobs** view. It runs:

```bash
squeue -u "$USER"
```

and summarizes each live job's ID, state, partition, pending reason, elapsed
time, time limit, remaining time, nodes, CPUs, memory, node list, dependency,
and submission time.

The Slurm information is available from:

- the **Slurm jobs** toolbar button, which shows every live user job;
- the **Where** cell for a registered batch or chain process;
- the **Scheduler** link in its Tasks cell.

The process-specific view filters the scheduler output to the IDs recorded
when `sbatch` submitted that batch or chain. Task log buttons remain separate
because APERO logs and Slurm accounting provide different information.

On systems without `squeue`, ARI hides the scheduler controls instead of
showing broken links. Finished jobs are absent from `squeue`; use the
saved process status and APERO output logs for historical diagnosis.

## Does Stop run `scancel`?

Yes. For a registered Slurm batch or chain process, **Stop** invokes:

```bash
scancel JOB_ID...
```

It cancels every job ID stored on that process record. Queue entries that the
cancelled process was still running are then moved back to pending. The
process record is marked stopped.

For local GUI/CLI queue processes, Stop instead terminates the local process
group with `TERM`, then `KILL` if needed. It does not run `scancel`. If the
record belongs to a different host, ARI refuses to signal it from the current
host.

The selected-process Stop action shows a confirmation describing these two
behaviors before it runs.

## Diagnosing “Tunnel active, dashboard not answering”

Run these checks in order:

1. On the ARI host:

   ```bash
   ssh SSH_ALIAS hostname
   ```

2. On the queue shell, confirm:

   ```bash
   hostname
   ```

3. The names must match. For Alliance, both commands must use the same
   ControlMaster.
4. Through SSH:

   ```bash
   ssh SSH_ALIAS \
     'curl -s http://127.0.0.1:REMOTE_PORT/api/state'
   ```

5. Through the local tunnel:

   ```bash
   curl -s http://127.0.0.1:LOCAL_PORT/api/state
   ```

Interpretation:

| SSH node check | Remote curl | Local curl | Diagnosis |
| --- | --- | --- | --- |
| Different node | fails | fails | Queue and tunnel are on different login nodes. |
| Same node | fails | fails | Queue supervisor is not running or the remote port is wrong. |
| Same node | answers | fails | SSH forward is absent, stale, or uses another node/port. |
| Same node | answers | answers | ARI can reach the dashboard. Refresh status. |

## Queue restarts and ControlMaster lifetime

If the ControlMaster disappears or is deliberately replaced, a round-robin
Alliance hostname may select a different login node. Stop or restart the queue
through the newly authenticated master when this happens. The queue and
tunnel must be re-pinned to a single node after every new master.
