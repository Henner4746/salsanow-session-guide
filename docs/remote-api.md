# Using your own remote model server

You need an HTTPS endpoint, an LM Studio API key and an available model. The starter discovers model IDs automatically; do not copy a particular Qwen identifier from another person's machine.

## Two credentials, two purposes

| Credential | Used where | Purpose |
|---|---|---|
| Cloudflare tunnel connection token | Host's cloudflared connector | Connect the host to its tunnel |
| LM Studio API key | Client applications | Authorize model requests |

Never substitute the connection token for the API key. This repository includes neither credential and does not provide someone else's private endpoint.

## Configure the client

Run the operating-system starter and enter your address, for example `https://api.example.com/v1`. It first checks that `/v1/models` rejects unauthenticated access with HTTP 401, then prompts for a hidden key and checks the authenticated model list. A 403 or HTML login page requires inspecting the proxy/authentication layer; the starter will not silently treat it as proof of LM Studio authentication.

The default creates a child terminal with session-scoped variables. It does not modify the parent shell, registry, profile or installed GUI apps. The first advertised model whose name does not contain `embed` is selected unless you pass `--model`. Explicit selection can override this name heuristic; only the model's documentation and an actual completion establish its capabilities.

## Claude Code

In the configured terminal, if Claude Code is already installed:

```bash
# macOS / Linux / Git Bash
claude --model "$API_MODEL"
```

```powershell
# PowerShell
claude --model $env:API_MODEL
```

LM Studio documents `/v1/messages` and accepts API-key or bearer authentication when authentication is enabled. For Anthropic-compatible clients the starter sets the base URL without the trailing `/v1`. Source: [LM Studio Anthropic compatibility](https://lmstudio.ai/docs/developer/anthropic-compat).

A compatible endpoint is not a guarantee that every model supports reliable tool use or every agent integration. The supplied handoff reports working streaming and tool calls for its tested setup; verify your own model separately.

## A Python client without dependencies

```console
python remote_ai.py --chat
```

The built-in client uses OpenAI-compatible chat completions and keeps conversation history only in memory. It is a small connection test and basic chat, not a complete agent or GUI application.

For an existing Python project using the OpenAI SDK, read the configured session variables:

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url=os.environ["OPENAI_BASE_URL"],
    api_key=os.environ["OPENAI_API_KEY"],
)
response = client.chat.completions.create(
    model=os.environ["API_MODEL"],
    messages=[{"role": "user", "content": "Say only: ok"}],
    max_tokens=1024,
)
print(response.choices[0].message.content)
```

The SDK is an optional dependency of that separate project; the starter itself does not install it.

## GUI applications

Use your HTTPS base URL, LM Studio API key and discovered model ID in the application's provider settings. Some clients add `/v1` themselves. Follow that client's documented behavior instead of repeatedly guessing URLs.

## Session availability and output budgets

The endpoint may remain in DNS after the host session ends. Check the host and connector before repeatedly changing the client. HTTP 530 is not a unique diagnosis: Cloudflare's detailed error code matters.

Reasoning models can spend their output budget before emitting final answer text. Increase `--max-tokens` if appropriate. Context capacity and speed depend on the model, quantization, GPU and settings; this guide does not promise the handoff's measured performance on other machines.
