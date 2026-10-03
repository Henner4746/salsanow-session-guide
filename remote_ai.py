"""A dependency-free remote LM Studio client. Credentials stay in process memory."""

import argparse
import getpass
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request


class SetupError(Exception):
    """An actionable connection or configuration failure."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def normalize_endpoint(value):
    value = value.strip().rstrip("/")
    parts = urllib.parse.urlsplit(value)
    if parts.scheme not in ("https", "http") or not parts.hostname:
        raise SetupError("Enter a full endpoint such as https://api.example.com/v1.")
    if parts.username is not None or parts.password is not None or parts.query or parts.fragment:
        raise SetupError("The endpoint must not contain credentials, a query or a fragment.")
    try:
        parts.port
    except ValueError as exc:
        raise SetupError("The endpoint port is invalid.") from exc
    if any(char.isspace() or ord(char) < 32 for char in value):
        raise SetupError("The endpoint contains whitespace or control characters.")
    if parts.scheme == "http" and parts.hostname not in ("localhost", "127.0.0.1", "::1"):
        raise SetupError("Use HTTPS for a remote endpoint. HTTP is allowed only on loopback.")
    if parts.path.endswith(("/models", "/chat/completions", "/messages")):
        raise SetupError("Enter the base URL, not a models or completion endpoint.")
    return value if parts.path.endswith("/v1") else value + "/v1"


def request_json(url, key=None, payload=None):
    headers = {"Accept": "application/json", "User-Agent": "RemoteAIStarter/1.0"}
    if key:
        headers["Authorization"] = "Bearer " + key
    body = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers)
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=120 if payload is not None else 20) as response:
            content = response.read(4 * 1024 * 1024 + 1)
            if len(content) > 4 * 1024 * 1024:
                raise SetupError("The server response is unexpectedly large.")
    except urllib.error.HTTPError as exc:
        exc.close()
        hints = {
            401: "Missing or rejected API key.",
            403: "Access denied; check server and Cloudflare Access policies.",
            404: "Endpoint or model not found; check the base path and model ID.",
            429: "Rate limit reached; wait before retrying.",
            502: "The proxy could not reach the host's local server.",
            530: "Read the Cloudflare error code and check DNS/tunnel health.",
        }
        if 300 <= exc.code < 400:
            hint = "Redirect refused; enter the final HTTPS endpoint directly."
        else:
            hint = hints.get(exc.code, "Check the host and proxy status.")
        raise SetupError(f"HTTP {exc.code}: {hint}") from exc
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        raise SetupError("Connection failed. Check TLS, the address and whether the host session is running.") from None
    try:
        return json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise SetupError("The endpoint returned non-JSON data, possibly a proxy/login page.") from None


def discover_models(endpoint, key):
    data = request_json(endpoint + "/models", key)
    if not isinstance(data, dict) or not isinstance(data.get("data"), list):
        raise SetupError("The server did not return an OpenAI-compatible model list.")
    models = []
    for item in data["data"]:
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item["id"]:
            if any(ord(char) < 32 or ord(char) == 127 for char in item["id"]):
                raise SetupError("The server returned a model ID with control characters.")
            if item["id"] not in models:
                models.append(item["id"])
    if not models:
        raise SetupError("No models found. Load a model on the host and try again.")
    return models


def verify_authentication(endpoint):
    try:
        request_json(endpoint + "/models")
    except SetupError as exc:
        if isinstance(exc.__cause__, urllib.error.HTTPError) and exc.__cause__.code == 401:
            return
        raise SetupError("Authentication check failed: " + str(exc)) from None
    raise SetupError("Unauthenticated model listing succeeded. Enable Require Authentication on the host before continuing.")


def choose_model(models, requested=None):
    if requested:
        if requested not in models:
            raise SetupError("Requested model is not in the server's model list.")
        return requested
    for model_id in models:
        if "embed" not in model_id.lower():
            return model_id
    raise SetupError("Only embedding-named models were found. Load a chat model or specify --model explicitly.")


def session_environment(endpoint, key, model):
    env = os.environ.copy()
    env.update({
        "OPENAI_BASE_URL": endpoint,
        "OPENAI_API_KEY": key,
        "ANTHROPIC_BASE_URL": endpoint[:-3],
        "ANTHROPIC_AUTH_TOKEN": key,
        "API_BASE_URL": endpoint,
        "API_KEY": key,
        "API_MODEL": model,
        "LM_API_TOKEN": key,
        # Avoid saving commands from this credential-bearing session in shell history.
        "HISTFILE": os.devnull,
    })
    return env


def open_terminal(env):
    if os.name == "nt":
        shell = shutil.which("pwsh") or shutil.which("powershell")
        command = [shell, "-NoLogo", "-NoProfile"] if shell else [os.environ.get("COMSPEC", "cmd.exe"), "/D"]
    else:
        # Only known interactive shells; do not execute an arbitrary SHELL string.
        preferred = os.path.basename(os.environ.get("SHELL", ""))
        candidates = [preferred] if preferred in ("bash", "zsh", "sh") else []
        candidates += ["zsh", "bash", "sh"] if sys.platform == "darwin" else ["bash", "sh"]
        shell = next((shutil.which(name) for name in candidates if shutil.which(name)), None)
        if not shell:
            raise SetupError("No supported interactive shell found. Use --chat instead.")
        name = os.path.basename(shell)
        command = [shell, "--noprofile", "--norc", "-i"] if name == "bash" else [shell, "-f", "-i"] if name == "zsh" else [shell, "-i"]
        if name == "sh":
            env.pop("ENV", None)
    print("\nOpening a configured terminal. Use API_MODEL for the discovered model ID.")
    print("Type exit when finished. No keys or profiles are written to disk.", flush=True)
    return subprocess.call(command, env=env)


def chat(endpoint, key, model, max_tokens):
    messages = []
    print("\nChat ready. Type /exit to finish. Conversation is kept only in memory.")
    while True:
        try:
            prompt = input("You: ").strip()
        except EOFError:
            return 0
        if prompt == "/exit":
            return 0
        if not prompt:
            continue
        candidate = messages + [{"role": "user", "content": prompt}]
        data = request_json(endpoint + "/chat/completions", key, {
            "model": model, "messages": candidate, "max_tokens": max_tokens, "stream": False,
        })
        try:
            choice = data["choices"][0]
            text = choice["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise SetupError("Unexpected completion format.") from None
        if not isinstance(text, str) or not text.strip():
            print("No answer text. Try a larger --max-tokens value or inspect model settings.")
            continue
        print("AI:", text)
        messages = candidate + [{"role": "assistant", "content": text}]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", help="HTTPS base URL; otherwise prompted or read from API_BASE_URL")
    parser.add_argument("--model", help="Optional model ID; defaults to the first model not named as an embedding model")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--check", action="store_true", help="Check auth and model discovery, then exit")
    modes.add_argument("--chat", action="store_true", help="Start a small chat instead of a terminal")
    parser.add_argument("--max-tokens", type=int, default=1024)
    args = parser.parse_args(argv)
    try:
        if sys.version_info < (3, 10):
            raise SetupError("Python 3.10 or newer is required.")
        interactive = sys.stdin.isatty() and sys.stdout.isatty() and sys.stderr.isatty()
        if args.max_tokens < 1:
            raise SetupError("--max-tokens must be positive.")
        value = args.endpoint or os.environ.get("API_BASE_URL")
        if not value:
            if not interactive:
                raise SetupError("Set API_BASE_URL or pass --endpoint when input is noninteractive.")
            value = input("Endpoint (e.g. https://api.example.com/v1): ")
        endpoint = normalize_endpoint(value)
        print("Checking:", endpoint)
        verify_authentication(endpoint)
        key = os.environ.get("API_KEY")
        if not key:
            if not interactive:
                raise SetupError("Set API_KEY in the process environment for noninteractive use.")
            key = getpass.getpass("LM Studio API key (hidden): ")
        if not key or any(ord(char) < 32 or ord(char) > 126 for char in key):
            raise SetupError("API key is empty or contains invalid header characters.")
        models = discover_models(endpoint, key)
        model = choose_model(models, args.model)
        print("Authentication and model discovery passed.")
        for model_id in models:
            print(" -", model_id)
        print("Selected:", model)
        if args.check:
            return 0
        if args.chat:
            return chat(endpoint, key, model, args.max_tokens)
        if not interactive:
            raise SetupError("An interactive terminal is required; use --check for automation.")
        return open_terminal(session_environment(endpoint, key, model))
    except SetupError as exc:
        print("Error:", exc, file=sys.stderr)
        return 1
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
