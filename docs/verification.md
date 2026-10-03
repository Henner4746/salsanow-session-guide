# Verification and evidence

Prepared on 2026-10-03. The newer supplied `HANDOFF-MAIN-PC.md` takes precedence over the older supplied guide where their session reports conflict. Original private documents and domains are not distributed in this repository.

| Item | Evidence | What it establishes |
|---|---|---|
| Authenticated HTTPS request returns 200; unauthenticated request returns 401 | Newer handoff, reported successful test | That session's remote API worked when recorded; not current uptime |
| Anthropic Messages, streaming and tool calling | Newer handoff, reported successful tests | Tested setup worked; not every model/client combination |
| Dashboard tunnel route and DNS | Observed during preparation in Cloudflare | Configuration was saved; alone this does not prove inference works |
| Settings and tokens survive a full session reset | Older guide explicitly says reset test outstanding | Remains unverified; handoff's persistence assertion is not a recorded reset procedure |
| Eight-hour connector stability | No completed duration test supplied | Remains unverified |
| GPU, memory, context and throughput | Supplied session documents | Machine-specific reports; no benchmark replication in this repo |
| `--token-file` and Anthropic endpoint semantics | Official documentation checked | Documented capabilities; installed versions still matter |
| Starter HTTP handling and environment setup | Repository's automated tests | Verified against local fixtures; no live user's endpoint or key required |
| Windows CMD and PowerShell launchers | 17-test suite passed locally on Windows with Python 3.14 | Both launchers successfully checked the authenticated local fixture |
| Model-list authentication after a reported host restart | Client-side API check during preparation | HTTP 200 with the test key, HTTP 401 without it; two model IDs listed. This was not a post-restart completion or duration test. |
| Windows/macOS/Linux launcher execution | [GitHub test run](https://github.com/Henner4746/salsanow-session-guide/actions/runs/37149390481), 2026-10-03 | All six jobs passed: three operating systems with Python 3.10 and 3.13; 17 fixture tests per job. No request to the private live endpoint was made. |

The older text claimed all commands were executed and verified while later admitting some paths were untested. This version keeps reported observations, documented features and pending tests separate. It also avoids claiming that startup registry writes prove registry deletion.

## How to add a useful verification result

Record date, OS, tool versions, relevant model ID and a sanitized sequence of steps. For a session-reset test, distinguish restarting an app, reconnecting a client and destroying/recreating the cloud session. Report both authenticated success and unauthenticated rejection after the reset. Do not publish tokens, settings exports or personal endpoint details.
