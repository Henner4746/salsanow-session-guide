# SalsaNOW session troubleshooting

These notes were adapted from a supplied session guide and a newer handoff. They describe one user's environment, not a universal guarantee about every GeForce NOW image or subscription. Check [verification status](verification.md) before treating a workaround as proven across restarts.

## 1. Find out what persists

The supplied guide reports persistent storage on `I:\`, plus `AppData` and `Documents`, while other profile paths and user environment settings can reset. Storage availability depends on the actual session. A program's location and its settings location may be different.

Before moving anything, identify the application's state directory and verify that the destination survives a complete session restart. The fact that SalsaNOW writes environment variables during startup does **not** by itself prove that the registry is wiped.

Useful read-only commands in Git Bash:

```bash
uname -a
pwd
df -h /c /i
ls -ld "$USERPROFILE/.lmstudio" "$LOCALAPPDATA/Programs/Git"
```

Record versions, session tier and date. Do not put complete settings files in an issue: they can include token material.

## 2. A tool cannot find Git Bash

Portable Git may be outside the locations an application searches. First check its documented path setting. If it searches `%LOCALAPPDATA%\Programs\Git`, a directory junction can point there without copying the installation.

Close the affected application, confirm the destination does not already exist, then run in **cmd**, substituting your installation path:

```bat
if not exist "%LOCALAPPDATA%\Programs" mkdir "%LOCALAPPDATA%\Programs"
mklink /J "%LOCALAPPDATA%\Programs\Git" "I:\ai\git"
```

Restart the application and verify its own Bash detection. `uname` identifies the shell/environment but does not prove that another application found it. Junction permissions and their survival after session reset still need checking in your environment. Do not replace an existing installation blindly.

## 3. Environment variables vanish

`setx` changes future process environments; it cannot update a process that is already running. A wrapper with `set "NAME=value"` sets the environment for the application it launches. It does not depend on registry persistence.

```bat
@echo off
setlocal
set "CODEBUFF_GIT_BASH_PATH=I:\ai\git\bin\bash.exe"
start "" "I:\path\to\your-app.exe"
```

This variable is application-specific, not a general Bash configuration.

## 4. System tools report access denied

The supplied session guide reports blocked system PowerShell and `nvidia-smi`. If SalsaNOW provides its own PowerShell, check `POWERSHELL_ROOT` and use that copy. This is environment-dependent; do not assume that a missing or denied command is always a PATH problem.

```bash
"$POWERSHELL_ROOT/pwsh.exe" -Command 'Get-ComputerInfo | Select-Object CsTotalPhysicalMemory'
```

Do not attempt to install drivers, bypass host restrictions or disable protection software.

## 5. LM Studio settings reset

The supplied documents identify `%USERPROFILE%\.lmstudio` as an important state directory. Confirm the location in your installed version. A configured model download directory does not necessarily move authentication settings.

To migrate safely:

1. Close LM Studio normally and confirm its processes stopped.
2. Make a private backup of the state directory. It may contain credentials.
3. Copy the directory to persistent storage and verify that the copy is complete. For `robocopy`, exit codes 0–7 indicate nonfatal outcomes; 8 or higher indicate a failure.
4. Rename the original directory as a backup; do not delete it. Create a junction at its original path pointing at the verified copy.
5. Start LM Studio, check settings and authentication, then perform a complete session-reset test.

The older guide's `robocopy /MOVE` and forced `taskkill` recipe is intentionally replaced by this backup-first workflow. This repository does not automatically migrate private state or kill applications.

## 6. No administrator rights or inbound network

The supplied environment has no normal inbound connectivity and no permission to install a Windows service. An outbound connector can make a running local server accessible. It cannot keep a terminated cloud session alive.

Set LM Studio's server port to **8080** in its UI as well as any launcher. Enable **Require Authentication**, create a separate API key per client and confirm that an unauthenticated request is rejected.

For a dashboard-managed Cloudflare tunnel:

1. Create the tunnel and a published application route in the dashboard.
2. Use your domain, subdomain `api`, type `HTTP`, origin `localhost:8080`.
3. Obtain the connection token privately. It is different from the LM Studio API key.
4. On the host, run a supported `cloudflared` version as a foreground process.

```bat
cloudflared.exe tunnel run --token-file "I:\private\tunnel-token.txt"
```

The example file is outside this repository. Keep it private. `--token-file` requires cloudflared **2025.4.0 or newer**. Keep the terminal open; Ctrl+C stops that connector. Source: [Cloudflare run parameters](https://developers.cloudflare.com/tunnel/reference/run-parameters/).

The remotely managed tunnel receives routes from Cloudflare. Do not combine this workflow with the older guide's local `ingress` YAML and assume offline validation proves the dashboard route works.

Do not run `cloudflared service install` on a host without administrator rights. On an ordinary personal computer that supports services, that is a separate installation decision.

## 7. Batch-file mistakes

- Escape parentheses and redirection characters in `echo` statements inside blocks.
- Use `echo.` for an empty line.
- `%VARIABLE%` expands when a block is parsed; delayed expansion changes this behavior.
- In cmd, `mkdir` creates intermediate directories; in Bash use `mkdir -p`.
- Consult `lms --help` for the installed CLI; the supplied guide reports `lms unload --all`, not `lms unload all`.
- Do not put credentials directly into launcher source files or test logs.

MSYS/Git Bash can translate arguments when starting Windows programs. Test cmd scripts from cmd or PowerShell, and use disposable fixtures. Never execute a supposedly stubbed script until you have inspected it for real stop, delete, move and process-kill commands.

## 8. Restart checklist

- Confirm the session exists and persistent storage is mounted.
- Confirm the application's state and model paths.
- Load a model and start the local server on the configured port.
- Check authentication before starting public exposure.
- Start the connector and check its status in Cloudflare.
- From a different computer, run the remote starter with `--check`, then `--chat`.
- After a full session reset, repeat both tests and report whether existing credentials survived.

No anti-idle scripts or session-limit bypasses are included. Session limits should be checked for the user's current subscription rather than copied as universal values.
