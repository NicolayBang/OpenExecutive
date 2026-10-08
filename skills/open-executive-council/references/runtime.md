# Local CLI runtime

Requires Python 3.10+ and Codex CLI (tested with 0.154.0). The runner uses only Python's standard library. Resolve paths below relative to the installed skill directory.

Check the existing sign-in:

```text
python scripts/council.py status
```

The runner uses `codex` from PATH, or the standard Windows desktop installation at `%LOCALAPPDATA%/Programs/OpenAI/Codex/bin/codex.exe`. For another installation, pass `--codex /absolute/path/to/codex` before `status` or `run`. If no account is signed in, use the normal `codex login` flow once. The runner requires ChatGPT sign-in so it cannot silently switch to API-key billing. It does not copy, print, or manage the login cache.

Create a private directory containing a UTF-8 `brief.md`, then run:

```text
python scripts/council.py run --task /absolute/task --output /absolute/new-output --roles finance,product
```

The brief is sent on stdin instead of the command line. The CLI starts in a temporary working directory with user configuration loading disabled so unrelated repository instructions and configured MCP servers are not loaded. Authentication continues to use the normal Codex home. API-key environment overrides are removed from the child environment. Configurations that require a custom credential-store setting have not been tested; the runner stops if it cannot find the existing ChatGPT login.

The runner starts one independent CLI session per selected role, serially, then a separate coordinator session with all specialist reports. It checks distinct session IDs, completed turns, and final text. Shell, app, browser, computer-use, image-generation, web-search, and further delegation capabilities are disabled, and Codex runs with a read-only sandbox. This is a local process workflow, without container isolation.

The output directory must not already exist. Each role and the `executive/` directory retain `events.jsonl`, `stderr.log`, and their individual `report.md`. The root `result.json` records completion status and session IDs; the root `report.md` is written only after verifying all specialists and final synthesis. These files can contain company information: use gitignored storage or a location outside the repository.

Each council has a 20-minute maximum. Cancellation or timeout stops the process tree started by that invocation; it does not stop unrelated Codex sessions. Diagnostic files remain available. If cleanup fails, the runner reports it. Read the existing result before retrying a failed task.

CLI agents have independent thread IDs; they do not appear as native child threads of the desktop conversation that launched the runner. The skill returns their report into that conversation. Inference uses the signed-in account's allowance and remains remote.

Official references: [non-interactive Codex](https://developers.openai.com/codex/noninteractive) and [authentication](https://developers.openai.com/codex/auth).
