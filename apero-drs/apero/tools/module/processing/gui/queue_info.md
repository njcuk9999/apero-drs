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

## Chain array task size

Each queue group becomes a Slurm array. Each array task runs its assigned
queue runs one after another; different array tasks can run concurrently.
The batch template's **CPUs per task** value limits concurrent array tasks
in Chain mode; Slurm may run fewer. Later groups wait for the preceding
group to succeed.

Enter **Queue runs per Slurm array task** to set the maximum runs assigned
to each array task. Leave it blank to calculate a size separately for each
group: divide its number of pending runs by the concurrency limit and round
up. For example, 24 runs with a limit of 8 produce 8 array tasks with 3
runs each. Entering 1 instead produces 24 array tasks, at most 8 at a time.

## Server recovery

The **Info** button beside Shutdown GUI shows the dashboard worker's APERO
version, user, machine, Python environment, configuration and source path.
It also shows the Git branch, commit and commit date, plus whether the queue
source files had uncommitted changes. These are captured when the worker
starts. The commit date is not the time the checkout was updated, and
already-running jobs or code loaded before a checkout changed may differ.
Git details are unavailable when the installed queue module is not tracked
by an accessible Git checkout.

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
