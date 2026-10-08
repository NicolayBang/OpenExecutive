# Local container setup

Requires Docker and Python 3.10+ on the host. The runtime uses only Python's standard library. Resolve all paths relative to the installed skill directory.

Build once:

```text
python scripts/council.py build
```

Check the dedicated account login:

```text
python scripts/council.py status
```

If not signed in, run the following and let the user complete the official browser/device flow:

```text
python scripts/council.py login
```

The login lives in the Docker volume `open-executive-council-auth`, outside the repository and image. Treat that volume as sensitive. The script uses one fixed container name to serialize council/login runs so they cannot concurrently refresh the same login. Separate specialist agents run within the coordinator's Codex runtime. Never mount the Docker socket, the user's home directory, or the desktop auth cache into this container.

Run a task from a directory containing a UTF-8 `brief.md`:

```text
python scripts/council.py run --task /absolute/task --output /absolute/new-output --roles finance,product
```

The brief is sent on stdin, not mounted. No host data directory is mounted into the runtime. The output directory is created on the host and must not already exist; the host writes the captured report, JSONL events, and result metadata there. Reports and event logs may contain company information and belong in private storage.

The container has a read-only root filesystem, a writable temporary `/tmp`, its own persistent Codex home, no inbound ports, no host mounts, no Linux capabilities, and no Docker socket. Codex additionally runs with a read-only sandbox; shell, app, browser, computer-use, image-generation, and web-search capabilities are disabled for the council. Runtime network access is needed for Codex inference. The council is advisory and receives only the brief, not direct account integrations.

Each run has a 20-minute maximum. Cancellation, interruption, timeout, or failure stops and removes the task container; existing task outputs are retained for inspection. Do not retry failed or incomplete work without reading its result and confirming whether any useful output already exists.

To stop an active task, run `docker stop open-executive-council-worker`. The auth volume remains for future tasks. Signing out can be done with `python scripts/council.py logout`; deleting the auth volume is a separate deliberate cleanup step.

Official references: [non-interactive Codex](https://developers.openai.com/codex/noninteractive), [authentication in containers](https://developers.openai.com/codex/auth#login-on-headless-devices), and [Codex subagents](https://developers.openai.com/codex/multi-agent).
