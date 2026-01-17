# VS Code Server Cleanup (Production-Safe)

These steps remove VS Code Server and related helper processes from the host, reduce idle CPU/RAM usage, and keep data intact. Run from a non-VS Code SSH session to avoid disconnects.

## Preconditions

- Ensure you have a separate SSH session (not VS Code Remote) since the cleanup will terminate VS Code server processes.
- Do not run during a deployment window that depends on a live VS Code session.

## Step 1: Identify VS Code Server Processes

```bash
ps aux | rg -i 'vscode-server|code-server|amazon q helper|remote-ssh'
```

## Step 2: Stop VS Code Server Processes

Run for each user that uses VS Code Remote (examples below cover root and a typical app user):

```bash
sudo pkill -u root -f 'vscode-server|remote-ssh|code-server'
sudo pkill -u root -f 'Amazon Q Helper|cloudcode_cli|geminicodeassist'
sudo pkill -u www-data -f 'vscode-server|remote-ssh|code-server' || true
```

If additional users exist, repeat with their usernames.

## Step 3: Remove VS Code Server Installations

Delete the server directories for each user. This does not touch application data.

```bash
sudo rm -rf /root/.vscode-server /root/.vscode-server-insiders /root/.vscode-remote
sudo rm -rf /root/.cache/ms-vscode-server /root/.cache/ms-vscode-remote
sudo rm -rf /home/*/.vscode-server /home/*/.vscode-server-insiders /home/*/.vscode-remote 2>/dev/null || true
sudo rm -rf /home/*/.cache/ms-vscode-server /home/*/.cache/ms-vscode-remote 2>/dev/null || true
```

## Step 4: Verify Cleanup

```bash
ps aux | rg -i 'vscode-server|code-server|amazon q helper|remote-ssh' || true
```

Expected: no VS Code server or helper processes remain.

## Step 5: Operational Guardrails (Non-Technical)

- Avoid reconnecting with VS Code Remote directly to this host.
- If remote editing is required, use a separate bastion or dev VM.
