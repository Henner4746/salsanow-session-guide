# From endpoint to a configured terminal

This is illustrative output with example addresses and model names, not a recording of a private account. The hidden key is never printed.

```text
Endpoint (e.g. https://api.example.com/v1): https://api.example.com
Checking: https://api.example.com/v1
LM Studio API key (hidden):
Authentication and model discovery passed.
 - example-chat-model
 - example-embedding-model
Selected: example-chat-model

Opening a configured terminal. Use API_MODEL for the discovered model ID.
Type exit when finished. No keys or profiles are written to disk.
```

## Windows

Double-click `start-windows.cmd`. After entering the two values, the starter opens PowerShell when available, otherwise cmd. In the PowerShell session, an already installed Claude Code client can use:

```powershell
claude --model $env:API_MODEL
```

For cmd instead:

```bat
claude --model "%API_MODEL%"
```

## macOS and Linux

Open a terminal in the extracted repository:

```sh
# macOS
sh ./start-macos.command

# Linux
sh ./start-linux.sh
```

In the configured shell, an already installed Claude Code client can use:

```sh
claude --model "$API_MODEL"
```

## Prefer a simple chat?

Pass `--chat` to the same starter. For example:

```sh
sh ./start-linux.sh --chat
```

The built-in chat does not need Claude Code or pip packages. Type `/exit` to leave. To check a connection without generating text, use `--check` instead. Run `python remote_ai.py --help` for the complete options.
