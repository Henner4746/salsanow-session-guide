import contextlib
import http.server
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import unittest
from unittest import mock

import remote_ai


ROOT = Path(__file__).resolve().parents[1]
TEST_KEY = "test-only-not-a-real-credential"


class FixtureHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.server.requests.append((self.path, self.headers.get("Authorization")))
        if self.path == "/redirect/v1/models":
            self.send_response(302)
            self.send_header("Location", "/v1/models")
            self.end_headers()
            return
        if self.path == "/open/v1/models":
            self.reply(200, {"data": [{"id": "fixture-model"}]})
            return
        if self.headers.get("Authorization") != "Bearer " + TEST_KEY:
            self.reply(401, {"error": "private server detail must not be printed"})
        elif self.path == "/empty/v1/models":
            self.reply(200, {"data": []})
        elif self.path == "/bad/v1/models":
            self.reply(200, {"unexpected": True})
        elif self.path == "/v1/models":
            self.reply(200, {"data": [{"id": "fixture-model"}, {"id": "second-model"}]})
        else:
            self.reply(404, {"error": "not found"})

    def do_POST(self):
        if self.headers.get("Authorization") != "Bearer " + TEST_KEY:
            self.reply(401, {})
            return
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.server.last_payload = payload
        if self.path == "/v1/chat/completions" and payload["model"] == "fixture-model":
            self.reply(200, {"choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}]})
        else:
            self.reply(404, {})

    def reply(self, status, data):
        content = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


class StarterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        cls.server.requests = []
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.root = f"http://127.0.0.1:{cls.server.server_port}"
        cls.endpoint = cls.root + "/v1"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.server.requests.clear()

    def environment(self):
        env = os.environ.copy()
        env.update(API_BASE_URL=self.endpoint, API_KEY=TEST_KEY)
        return env

    def test_endpoint_normalization(self):
        self.assertEqual(remote_ai.normalize_endpoint(" https://api.example.com/ "), "https://api.example.com/v1")
        self.assertEqual(remote_ai.normalize_endpoint("https://api.example.com/custom/v1/"), "https://api.example.com/custom/v1")
        self.assertEqual(remote_ai.normalize_endpoint(self.endpoint), self.endpoint)

    def test_unsafe_endpoint_rejected(self):
        for value in (
            "http://example.com", "ftp://example.com", "https://user:password@example.com",
            "https://example.com?api_key=value", "https://example.com/#fragment",
            "https://example.com/v1/models", "https://example.com:bad", "https://exa mple.com",
        ):
            with self.subTest(value=value), self.assertRaises(remote_ai.SetupError):
                remote_ai.normalize_endpoint(value)

    def test_authentication_required_and_models_discovered(self):
        remote_ai.verify_authentication(self.endpoint)
        self.assertEqual(remote_ai.discover_models(self.endpoint, TEST_KEY), ["fixture-model", "second-model"])

    def test_embedding_model_is_not_default_chat_model(self):
        self.assertEqual(remote_ai.choose_model(["text-embedding-example", "fixture-model"]), "fixture-model")

    def test_embedding_only_list_requires_explicit_selection(self):
        with self.assertRaisesRegex(remote_ai.SetupError, "Only embedding"):
            remote_ai.choose_model(["nomic-embed-text"])
        self.assertEqual(remote_ai.choose_model(["nomic-embed-text"], "nomic-embed-text"), "nomic-embed-text")

    def test_open_server_refused(self):
        with self.assertRaisesRegex(remote_ai.SetupError, "Unauthenticated"):
            remote_ai.verify_authentication(self.root + "/open/v1")

    def test_wrong_key_refused_without_leaking_details(self):
        with self.assertRaises(remote_ai.SetupError) as result:
            remote_ai.discover_models(self.endpoint, "invalid-test-value")
        self.assertIn("401", str(result.exception))
        self.assertNotIn("private server detail", str(result.exception))
        self.assertNotIn("invalid-test-value", str(result.exception))

    def test_redirect_not_followed_with_key(self):
        with self.assertRaisesRegex(remote_ai.SetupError, "Redirect refused"):
            remote_ai.discover_models(self.root + "/redirect/v1", TEST_KEY)
        self.assertEqual(len(self.server.requests), 1)
        self.assertEqual(self.server.requests[0][0], "/redirect/v1/models")

    def test_invalid_and_empty_model_lists(self):
        for path in ("/empty/v1", "/bad/v1"):
            with self.subTest(path=path), self.assertRaises(remote_ai.SetupError):
                remote_ai.discover_models(self.root + path, TEST_KEY)

    def test_process_environment_does_not_change_parent(self):
        original = os.environ.copy()
        env = remote_ai.session_environment("https://api.example.com/v1", TEST_KEY, "fixture-model")
        self.assertEqual(env["ANTHROPIC_BASE_URL"], "https://api.example.com")
        self.assertEqual(env["OPENAI_BASE_URL"], "https://api.example.com/v1")
        self.assertEqual(env["OPENAI_API_KEY"], TEST_KEY)
        self.assertEqual(dict(os.environ), original)

    def test_chat_real_http_request(self):
        output = io.StringIO()
        with mock.patch("builtins.input", side_effect=["Say only: ok", "/exit"]), contextlib.redirect_stdout(output):
            self.assertEqual(remote_ai.chat(self.endpoint, TEST_KEY, "fixture-model", 1024), 0)
        self.assertIn("AI: ok", output.getvalue())
        self.assertEqual(self.server.last_payload["max_tokens"], 1024)

    def test_noninteractive_check(self):
        result = subprocess.run([sys.executable, str(ROOT / "remote_ai.py"), "--check"],
                                env=self.environment(), capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Selected: fixture-model", result.stdout)
        self.assertNotIn(TEST_KEY, result.stdout + result.stderr)

    def test_requested_model(self):
        result = subprocess.run([sys.executable, str(ROOT / "remote_ai.py"), "--check", "--model", "second-model"],
                                env=self.environment(), capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Selected: second-model", result.stdout)

    def test_unknown_model_refused(self):
        with mock.patch.dict(os.environ, self.environment()), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(remote_ai.main(["--check", "--model", "unknown"]), 1)

    def test_noninteractive_missing_key_refused(self):
        env = self.environment()
        env.pop("API_KEY")
        result = subprocess.run([sys.executable, str(ROOT / "remote_ai.py"), "--check"],
                                env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Set API_KEY", result.stderr)

    def test_os_launcher(self):
        if os.name == "nt":
            commands = [[os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", str(ROOT / "start-windows.cmd"), "--check"]]
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            if powershell:
                commands.append([powershell, "-NoProfile", "-File", str(ROOT / "start-windows.ps1"), "--check"])
        else:
            filename = "start-macos.command" if sys.platform == "darwin" else "start-linux.sh"
            commands = [["sh", str(ROOT / filename), "--check"]]
        for command in commands:
            with self.subTest(launcher=command):
                result = subprocess.run(command, env=self.environment(), capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Authentication and model discovery passed", result.stdout)
                self.assertNotIn(TEST_KEY, result.stdout + result.stderr)

    def test_terminal_launch_receives_key_in_environment_only(self):
        env = remote_ai.session_environment(self.endpoint, TEST_KEY, "fixture-model")
        with mock.patch("remote_ai.subprocess.call", return_value=0) as launch, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(remote_ai.open_terminal(env), 0)
        args, kwargs = launch.call_args
        self.assertNotIn(TEST_KEY, " ".join(args[0]))
        self.assertEqual(kwargs["env"]["API_KEY"], TEST_KEY)


if __name__ == "__main__":
    unittest.main()
