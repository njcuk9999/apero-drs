## Queue dashboard tabs

The queue dashboard (`apero_queue.py gui`) has four main tabs: **Control**
(run and manage the queue), **Processes** (the generate, reset, queue run
and Slurm batch/chain processes started around the queue - open their logs
or stop them), **Status** (inspect queue groups and tasks, click a task
to view its log) and **Stats** (how long each recipe type takes, and the
RAM, CPU and disk I/O used by queue tasks over time). The Control tab is
split into:

- **Info**: this summary of the Control tabs.
- **Generate**: fill the queue by running `apero_processing` (always in
  queue mode) with a run file and optional overrides.
- **Run**: run the next queued task(s) on this machine using APERO
  multiprocessing (`apero_queue.py run`).
- **Batch**: create (and optionally submit) classic `sbatch` scripts for
  the next queue group (`apero_queue.py batch`).
- **Chain**: create dependency-chained Slurm array jobs so queue groups
  run strictly in order (`apero_queue.py chain`).
- **Actions**: queue management actions such as retrying failed tasks,
  stopping running tasks, clearing or resetting queue states and resetting
  all APERO data (`apero_queue.py action` / `apero_queue.py reset`).
- **Template**: edit and save the named `sbatch` templates (resources and
  activation lines) used by Batch and Chain (`apero_queue.py init`).

## Server recovery

**Refresh** cancels a pending status request and reads the queue again.
Requests time out after 30 seconds; polling does not accumulate duplicate
requests while the server is slow.

**Restart server** replaces the dashboard worker on the same public port.
Queue files are preserved. Active GUI actions may be interrupted, but
separately running tasks and submitted Slurm jobs are not stopped. Check
the Processes and Status tabs before starting more work after a restart.
If the worker crashes, reloading the page displays the recovery control.
The supervisor itself must still be running; if its process is stopped,
start `apero_queue.py gui` again from the terminal.
